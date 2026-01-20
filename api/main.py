from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from api.routers import context, journal, goals, habits, reviews
from api.auth import verify_api_key
from api.exceptions import PersonalAxisException
from api.auth import API_KEY_NAME
import datetime

app = FastAPI(
    title="PersonalAxis API",
    description="AI-Powered Life OS - Mobile API",
    version="1.0.0"
)

# CORS for PWA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", API_KEY_NAME],
    allow_credentials=True,
    max_age=600
)

# Exception Handlers
# Order matters: Most specific first, then generic

@app.exception_handler(PersonalAxisException)
async def personalaxis_exception_handler(request: Request, exc: PersonalAxisException):
    """Handle all custom PersonalAxis exceptions with structured error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "user_message": exc.user_message,
                "details": exc.details,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR", 
                "message": exc.detail,
                "user_message": str(exc.detail),
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": exc.errors(),
                "user_message": "Girdi verileri hatalı.",
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global Exception: {exc}") # Log strictly
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "user_message": "Beklenmeyen bir hata oluştu.",
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    )

# Health check (Public)
@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}

# Protected Routes
app.include_router(context.router, dependencies=[Depends(verify_api_key)])
app.include_router(journal.router, dependencies=[Depends(verify_api_key)])
app.include_router(goals.router, dependencies=[Depends(verify_api_key)])
app.include_router(habits.router, dependencies=[Depends(verify_api_key)])
app.include_router(reviews.router, dependencies=[Depends(verify_api_key)])
