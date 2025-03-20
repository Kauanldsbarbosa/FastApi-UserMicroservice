import re


def validate_email(email: str):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise ValueError('The email is not valid.')

    return email


def validate_password(password: str):
    MIN_PASSWORD_LENGTH = 6

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError('Password must be at least 6 characters long')
    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise ValueError(
            'Password must contain at least one special character'
        )
    return password
