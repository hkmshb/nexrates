from decimal import Decimal

import pytest

from nexrates.data import Currency, Rate, to_rate


class TestCurrency:
    @pytest.mark.parametrize(
        'name',
        [
            'CFA FRANC',
            'DANISH KRONE',
            'JAPANESE YEN',
            'POUND STERLING',
            'POUNDS STERLING',
            'SWISS FRANC',
            'YUAN/RENMINBI',
        ],
    )
    def test_from_name_with_enum_names(self, name):
        value = Currency.from_name(name)
        assert value is not None
        assert isinstance(value, Currency)

    @pytest.mark.parametrize('name', ['CFA', 'US', 'YUAN'])
    def test_from_name_with_partial_name(self, name):
        value = Currency.from_name(name)
        assert value is not None
        assert isinstance(value, Currency)

    @pytest.mark.parametrize('name', ['POESA'])
    def test_from_name_with_invalid_names_fails(self, name):
        pytest.raises(ValueError, lambda: Currency.from_name(name))


class TestRate:
    rate = Rate(currency=Currency.EURO, cost=100.00, rate=120.00, sale=150.00)
    record = {
        'Rate Date': '2/15/2021',
        'Currency': 'US DOLLAR',
        'Buying Rate': '459.5375',
        'Central Rate': '460.1438',
        'Selling Rate': '460.75',
    }

    def test_to_dict_without_exclude(self):
        value = self.rate.to_dict()
        assert value is not None
        assert 'currency' in value and value.get('currency') == Currency.EURO
        assert 'cost' in value and value.get('cost') == "100.00"
        assert 'rate' in value and value.get('rate') == "120.00"
        assert 'sale' in value and value.get('sale') == "150.00"

    def test_to_dict_with_exclude(self):
        value = self.rate.to_dict(exclude={'currency', 'cost'})
        assert value is not None
        assert 'currency' not in value
        assert 'cost' not in value
        assert 'rate' in value and value.get('rate') == "120.00"
        assert 'sale' in value and value.get('sale') == "150.00"

    def test_to_rate(self):
        rate = to_rate(self.record)
        assert rate is not None
        assert isinstance(rate, Rate)
        assert rate.currency == Currency.US_DOLLAR

        # quantize decimals to 2 decimal places
        two_places = Decimal(10) ** -2
        assert rate.cost.quantize(two_places) == Decimal(459.5375).quantize(two_places)
        assert rate.rate.quantize(two_places) == Decimal(460.1438).quantize(two_places)
        assert rate.sale.quantize(two_places) == Decimal(460.75).quantize(two_places)
