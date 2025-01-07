from datetime import datetime, date

from falgueras.common.logging_utils import get_colored_logger

logger = get_colored_logger(__name__)

# ISO 8601
TIMESTAMP_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_ISO_FORMAT = "%Y-%m-%d"


def cast_to_date(date_str: str, date_format: str = DATE_ISO_FORMAT) -> date:
    try:
        return datetime.strptime(date_str, date_format).date()
    except ValueError as exc:
        logger.error(exc)
        raise exc


def cast_to_datetime(timestamp_str: str, timestamp_format: str = TIMESTAMP_ISO_FORMAT) -> datetime:
    try:
        return datetime.strptime(timestamp_str, timestamp_format)
    except ValueError as exc:
        logger.error(exc)
        raise exc


def format_datetime_iso(date_time: datetime) -> str:
        """Format a datetime object into ISO format."""
        return date_time.strftime(TIMESTAMP_ISO_FORMAT)