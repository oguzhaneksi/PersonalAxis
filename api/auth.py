from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise HTTPException(status_code=403, detail="Missing API Key")

    expected_key = os.getenv("PERSONALAXIS_API_KEY")
    if not expected_key:
        # In production, this should probably log an error and return 500,
        # but for now we raise 500 to indicate misconfiguration.
        raise HTTPException(status_code=500, detail="API key not configured in server")
    
    if api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
