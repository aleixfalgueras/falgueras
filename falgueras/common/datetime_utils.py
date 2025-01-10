from datetime import datetime, date, timezone

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)

TZ_FORMAT = "%Y-%m-%d %H:%M:%S%z"

def get_date(date_str: str, _format: str = "%Y-%m-%d") -> date:
    try:
        return datetime.strptime(date_str, _format).date()
    except ValueError as exc:
        logger.error(exc)
        raise exc


def get_datetime(datetime_str: str, _format: str = "%Y-%m-%d %H:%M:%S", tz: timezone = None) -> datetime:
    try:
        dt = datetime.strptime(datetime_str, _format)
        if tz:
            dt = dt.replace(tzinfo=tz)
        return dt

    except ValueError as exc:
        logger.error(exc)
        raise exc


# BigQuery formatting functions to query date, datetime, and timestamp columns.

def bq_date_format(_date: date) -> str:
    """A calendar date (year, month, day). Ex: 2024-11-21"""
    return _date.isoformat()


def bq_datetime_format(_datetime: datetime) -> str:
    """A calendar date and time. No timezone info, ms precision. Ex: 2021-01-01 12:34:56.000000"""
    return _datetime.replace(tzinfo=None).isoformat(timespec="microseconds")


def bq_timestamp_format(_datetime: datetime) -> str:
    """
    A BigQuery timestamp value is an absolute point in time. It has ms precision and it's stored with UTC timezone.
    When you insert a TIMESTAMP value, it is converted to UTC if it includes a time zone offset.
    When you query a TIMESTAMP value, it is always returned in UTC format.
    Ex: 2021-01-01 12:34:56.000000-08:00
    """
    if _datetime.tzinfo is None:
        logger.warn(f"No timezone detected for datetime {_datetime}, adding UTC timezone.")
        _datetime = _datetime.replace(tzinfo=timezone.utc)

    return _datetime.isoformat(timespec="microseconds")
