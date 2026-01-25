
from datetime import datetime, timedelta
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

def parse_date(date_str: str) -> datetime:
    """
    Parses a date string into a datetime object.
    Returns None if parsing fails.
    """
    if not date_str or date_str == "N/A" or date_str == "Freshly Posted":
        # Treat "Freshly Posted" as today
        if date_str == "Freshly Posted":
            return datetime.now()
        return None

    try:
        # datautil.parser is very robust
        dt = parser.parse(date_str)
        # Ensure offset-naive for comparison (or aware, but simpler to normalize to naive UTC if strict)
        # For simple bot logic, converting to naive local/UTC is usually fine if consistent.
        # Let's return the datetime object directly, parser usually handles it well.
        # If timezone aware, convert to naive for simple subtraction with datetime.now()
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        return dt
    except Exception as e:
        logger.debug(f"Could not parse date '{date_str}': {e}")
        return None

def is_recent(date_str: str, days: int = 7) -> bool:
    """
    Checks if the date_str is within the last 'days' days.
    """
    dt = parse_date(date_str)
    if not dt:
        # If we can't parse it, we default to including it (or excluding depending on policy).
        # User said "if date is available and able to apply then post otherwise no".
        # If "Freshly Posted" (Internshala), we return True.
        # If empty/N/A, risky. Let's assume False to be safe if strict, or True if we trust source.
        # Given "old dates" complaint, let's match strictness.
        if date_str == "Freshly Posted": return True
        return False # safe default for unknown dates to avoid spamming old stuff

    cutoff = datetime.now() - timedelta(days=days)
    return dt >= cutoff
