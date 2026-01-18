from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv
from api.exceptions import AuthMissingError, AuthInvalidError

load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise AuthMissingError()

    expected_key = os.getenv("PERSONALAXIS_API_KEY")
    if not expected_key:
        # Server misconfiguration - keep as HTTPException for internal error
        raise HTTPException(status_code=500, detail="API key not configured in server")
    
    if api_key != expected_key:
        raise AuthInvalidError()
    return api_key
