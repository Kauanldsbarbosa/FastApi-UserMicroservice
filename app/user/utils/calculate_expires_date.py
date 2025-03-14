from datetime import datetime, timedelta, timezone


def expires_date(token_expires_in: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=token_expires_in)
