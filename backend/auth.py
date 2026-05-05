from fastapi import HTTPException, Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = "dev-secret-key"
COOKIE_NAME = "session"
SESSION_MAX_AGE = 86400  # 24 hours

_serializer = URLSafeTimedSerializer(SECRET_KEY)

VALID_USERNAME = "user"
VALID_PASSWORD = "password"


def create_session_token(username: str) -> str:
    return _serializer.dumps(username)


def verify_session_token(token: str) -> str | None:
    try:
        return _serializer.loads(token, max_age=SESSION_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(request: Request) -> str:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401)
    username = verify_session_token(token)
    if not username:
        raise HTTPException(status_code=401)
    return username
