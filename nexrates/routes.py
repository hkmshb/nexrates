import datetime
from typing import List

from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse

from .data import Currency, ExchangeRates
from .utils import settings

router = APIRouter()


async def _get_rates(date: datetime.date, symbols: List[Currency]) -> dict:
    if date < datetime.date(2001, 12, 10):
        content = {'error': 'There is no data for dates older than 2001-12-10'}
        return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)

    exchange_rates = (
        await ExchangeRates.query.where(ExchangeRates.date <= date)
        .order_by(ExchangeRates.date.desc())
        .gino.first()
    )
    rates = exchange_rates.rates

    if symbols:
        if all(symbol.value in rates for symbol in symbols):
            rates = {symbol: rates[symbol.value] for symbol in symbols}
        else:
            symbol_names = ','.join([c.value for c in symbols if c.value not in rates])
            content = {'error': f"Symbols '{symbol_names}' are invalid for date {date}"}
            return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)

    return {'date': exchange_rates.date.strftime('%Y-%m-%d'), 'rates': rates}


@router.get('/api/latest')
async def latest_exchange_rates(symbols: List[Currency] = Query(None, alias='symbol')):
    result = await _get_rates(datetime.date.today(), symbols)
    return result


@router.get('/api/history')
async def historic_exchange_rates(
    start_at: datetime.date,
    end_at: datetime.date,
    symbols: List[Currency] = Query(None, alias='symbol'),
):
    exchange_rates = (
        await ExchangeRates.query.where(ExchangeRates.date >= start_at)
        .where(ExchangeRates.date <= end_at)
        .order_by(ExchangeRates.date.desc())
        .gino.all()
    )

    historic_rates = {}
    for er in exchange_rates:
        rates = er.rates

        if symbols:
            if all(symbol.value in rates for symbol in symbols):
                rates = {symbol: rates[symbol.value] for symbol in symbols}
            else:
                symbol_names = ','.join([c.value for c in symbols if c.value not in rates])
                content = {'error': f"Symbols '{symbol_names}' are invalid for date {er.date}"}
                return JSONResponse(content=content, status_code=status.HTTP_400_BAD_REQUEST)

        historic_rates[er.date] = rates

    return {
        'start_at': start_at.isoformat(),
        'end_at': end_at.isoformat(),
        'rates': historic_rates,
    }


@router.get('/api/{date}')
async def exchange_rates(
    date: datetime.date = None, symbols: List[Currency] = Query(None, alias='symbol')
):
    date = date or datetime.date.today()
    result = await _get_rates(date, symbols)
    return result


@router.get('/api/')
async def api_root():
    return {'details': f'{settings.BASE_URL}/', 'docs': f'{settings.BASE_URL}/api/docs/'}
