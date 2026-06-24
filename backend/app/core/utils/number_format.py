from decimal import Decimal
from typing import Union


def format_currency(amount: Union[Decimal, float, str, int]) -> str:
    try:
        decimal_account = Decimal(str(amount))
        # ? format with comma (,) and 2 decimal places
        return f"{decimal_account:,.2f}"
    except (ValueError, TypeError, AttributeError):
        return str(amount)


def parse_decimal(amount: Union[str, float, int]) -> Decimal:
    try:
        if isinstance(amount, str):
            amount = amount.replace(",", "")
        return Decimal(str(amount))
    except (ValueError, TypeError, AttributeError):
        raise ValueError(f"Could not convert {amount} to Decimal")
