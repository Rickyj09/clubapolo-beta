from decimal import Decimal
from datetime import date, datetime

def json_safe(value):
    """
    Convierte valores no serializables (Decimal, date, datetime)
    a tipos compatibles con JSON.
    """
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}

    if isinstance(value, list):
        return [json_safe(v) for v in value]

    return value
