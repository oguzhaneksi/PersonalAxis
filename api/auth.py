from datetime import datetime, timedelta
import os
import secrets
from typing import Optional, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, HTTPException, Response

from api.exceptions import AuthInvalidError, AuthMissingError, AuthSessionExpiredError
from api.schemas import LoginRequest

load_dotenv()

SESSION_COOKIE_NAME = "personalaxis_session"
SESSION_DURATION_DAYS = int(os.getenv("PERSONALAXIS_SESSION_DAYS", "30"))
SESSION_SECURE = os.getenv("PERSONALAXIS_COOKIE_SECURE", "true").lower() == "true"
SESSION_SAMESITE = os.getenv("PERSONALAXIS_COOKIE_SAMESITE", "strict")

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Simple in-memory session store (replace with Redis for production scaling)
sessions: Dict[str, datetime] = {}


def _cleanup_expired_sessions() -> None:
    now = datetime.now()
    expired = [token for token, expires_at in sessions.items() if expires_at <= now]
    for token in expired:
        sessions.pop(token, None)


@router.post("/login")
async def login(payload: LoginRequest, response: Response):
    """Authenticate using a password stored in .env and set a session cookie."""
    password = payload.password
    if not password:
        raise AuthMissingError()

    expected_password = os.getenv("PERSONALAXIS_PASSWORD")
    if not expected_password:
        raise HTTPException(status_code=500, detail="Server authentication not configured")

    if password != expected_password:
        raise AuthInvalidError()

    _cleanup_expired_sessions()
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=SESSION_DURATION_DAYS)
    sessions[session_token] = expires_at

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=SESSION_SECURE,
        samesite=SESSION_SAMESITE,
        max_age=SESSION_DURATION_DAYS * 24 * 60 * 60,
        path="/"
    )

    return {"success": True, "data": {"expires_at": expires_at.isoformat()}}


@router.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    if session_token:
        sessions.pop(session_token, None)

    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")
    return {"success": True, "data": {"status": "logged_out"}}


@router.get("/status")
async def status(session_token: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    _cleanup_expired_sessions()
    if not session_token or session_token not in sessions:
        return {"success": True, "data": {"authenticated": False}}

    return {
        "success": True,
        "data": {
            "authenticated": True,
            "expires_at": sessions[session_token].isoformat()
        }
    }


async def verify_session(session_token: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME)):
    if not session_token:
        raise AuthMissingError()

    _cleanup_expired_sessions()
    expires_at = sessions.get(session_token)
    if not expires_at:
        raise AuthSessionExpiredError()


    return session_token
