import csv
import enum
import fcntl
import io
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from gino.dialects.asyncpg import JSONB
from gino.ext.starlette import Gino
from pydantic import BaseModel

from .utils import settings

# const
DATE_FMT = '%m/%d/%Y'

DATE_FIELD = 'Rate Date'
COST_FIELD = 'Buying Rate'
RATE_FIELD = 'Central Rate'
SALE_FIELD = 'Selling Rate'

MAPPED_FIELDS = {
    COST_FIELD: 'cost',
    RATE_FIELD: 'rate',
    SALE_FIELD: 'sale',
}

# logger
log = logging.getLogger(__name__)

# database
db = Gino(dsn=settings.DATABASE_URL)


# source: https://iban.com/currency-codes
class Currency(enum.Enum):
    # fmt: off
    # standard names
    CFA_FRANC           = 'XOF'
    DANISH_KRONE        = 'DKK'
    EURO                = 'EUR'
    NAIRA               = 'NGN'
    POUND_STERLING      = 'GBP'
    RAND                = 'ZAR'
    SAUDI_RIYAL         = 'SAR'
    SWISS_FRANC         = 'CHF'
    US_DOLLAR           = 'USD'
    YEN                 = 'JPY'
    YUAN_RENMINBI       = 'CNY'

    # non-standard names
    JAPANESE_YEN        = 'JPY'
    POUNDS_STERLING     = 'GBP'
    RIYAL               = 'SAR'
    SOUTH_AFRICAN_RAND  = 'ZAR'

    # extras/special names?
    SDR                 = 'SDR'  # IMF Special Drawing Right
    WAUA                = 'WAUA'  # West African Unit of Account (not in source)

    # fmt: on

    @classmethod
    def from_name(cls, currency_name) -> 'Currency':
        KNOWN_NAMES = [c.name for c in list(cls)]  # type: ignore

        # build list of potential names
        name = (currency_name or '').upper().replace(' ', '_').replace('/', '_')
        names = [name, name.split('_')[0]]

        for name in names:
            value = getattr(cls, name, None)
            if not value:
                for known_name in KNOWN_NAMES:
                    if known_name.startswith(name):
                        value = getattr(cls, known_name)
                        break

            if value:
                return value

        raise ValueError(f'unknown currency: {currency_name}')


class Rate(BaseModel):
    currency: Currency
    cost: Decimal
    rate: Decimal
    sale: Decimal

    def to_dict(self, exclude=None):
        values = self.dict(exclude=exclude)
        return {
            key: f'{value:.2f}' if isinstance(value, Decimal) else value
            for key, value in values.items()
        }


DayRates = Tuple[date, List[Rate]]


class ExchangeRates(db.Model):  # type: ignore
    __tablename__ = 'exchange_rates'

    date = db.Column(db.Date(), primary_key=True)
    rates = db.Column(JSONB())

    def __repr__(self):
        return 'Rate [{self.date}]'


def to_rate(data: dict) -> Optional[Rate]:
    """Converts a CBN published record to a Rate object.

    :param data: CBN published record
    :type data: dict
    :return: Rate object of the record.
    :rtype: Rate
    """
    try:
        values = {'currency': Currency.from_name(data['Currency'].strip())}
        values.update(
            {field: Decimal(data[df]) for df, field in MAPPED_FIELDS.items()}  # type: ignore
        )
    except (InvalidOperation, ValueError) as ex:
        log.warn(f'unable to process: {data}. error: {ex}')
        return None

    return Rate(**values)


async def read_rates():
    """Returns iterable of latest exchange rates published by CBN."""
    log.debug('downloading exchange rates csv ...')
    r = requests.get(settings.RATES_DOC_URL)
    if r.status_code != requests.codes.ok:
        log.warn(f'download failed: {r.reason} ...')
        yield []

    rates: List[Rate] = []
    day_date = datetime.today().date()

    buffer = io.StringIO(r.content.decode('utf-8'))
    for row in csv.DictReader(buffer):
        row_date = datetime.strptime(row['Rate Date'], DATE_FMT).date()
        if row_date != day_date and rates:
            yield [day_date, rates]

            day_date = row_date
            rates = []

        if rate := to_rate(row):
            rates.append(rate)

    if rates:
        yield [day_date, rates]


async def update_rates():
    async for day_date, pub_rates in read_rates():
        rates = await ExchangeRates.get(day_date)
        if rates:
            break

        await ExchangeRates.create(
            date=day_date,
            rates={r.currency.value: r.to_dict(exclude={'currency'}) for r in pub_rates},
        )


async def initialize_scheduler():
    # check that tables exists
    await db.gino.create_all()

    # schedule exchange rates updates
    try:
        _ = open('.scheduler.lock', 'w')
        fcntl.lockf(_.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

        scheduler = AsyncIOScheduler()
        scheduler.start()

        # update latest rates data
        scheduler.add_job(update_rates, "interval", hours=24)

        # fill up the database with rates
        await db.func.count(ExchangeRates.date).gino.scalar()
        scheduler.add_job(update_rates)
    except BlockingIOError as ex:
        log.warn(f'blocking io error: {ex}')
