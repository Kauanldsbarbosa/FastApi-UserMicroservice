from datetime import datetime, timedelta, timezone


def expires_date(token_expires_in: int) -> datetime:
    datetime_with_tz = datetime.now(timezone.utc) + timedelta(minutes=token_expires_in)
    
    return datetime_with_tz.replace(tzinfo=None)
