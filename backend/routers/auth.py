from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel

import auth as auth_module
from auth import get_current_user

router = APIRouter(prefix="/api/auth")


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(credentials: LoginRequest, response: Response):
    if credentials.username != auth_module.VALID_USERNAME or credentials.password != auth_module.VALID_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth_module.create_session_token(credentials.username)
    response.set_cookie(
        auth_module.COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        max_age=auth_module.SESSION_MAX_AGE,
    )
    return {"username": credentials.username}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(auth_module.COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(username: str = Depends(get_current_user)):
    return {"username": username}
