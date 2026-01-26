# Cookie-Based Authentication Plan

## Overview

Replace API key authentication with HTTP-only cookie sessions for secure PWA access.

## Why Cookies?

| Problem with API Keys | Cookie Solution |
|----------------------|-----------------|
| Cannot read `.env` in PWA | Browser manages cookies automatically |
| Exposed to XSS attacks | `httpOnly` flag blocks JS access |
| Manual header management | Automatic with `credentials: 'include'` |
| No built-in expiration | Browser handles expiry |

## Architecture

```
PWA → POST /api/auth/login (password) → Set-Cookie: session_token
PWA → GET /api/* (cookie auto-sent) → Verify session → Response
```

## Implementation Tasks

### Backend (api/)

1. **Update `auth.py`**
   - Add session storage (in-memory dict, Redis later)
   - Create `/api/auth/login` endpoint (validates password from `.env`)
   - Create `/api/auth/logout` endpoint (clears cookie)
   - Create `/api/auth/status` endpoint (checks session validity)
   - Create `verify_session()` dependency (replaces `verify_api_key`)

2. **Update `main.py`**
   - Register auth router
   - Replace `verify_api_key` with `verify_session` on protected routes
   - Update CORS to support credentials

3. **Update `exceptions.py`**
   - Add `AuthSessionExpiredError` exception

### Frontend (web/js/)

4. **Update `api-client.js`**
   - Remove API key handling
   - Add `credentials: 'include'` to all fetch calls
   - Add `login()`, `logout()`, `checkAuthStatus()` methods

5. **Update `app.js`**
   - Add auth check on app initialization
   - Add login screen UI
   - Add logout functionality
   - Handle 401 responses (redirect to login)

6. **Update `app.css`**
   - Add login form styles

### Environment

7. **Update `.env`**
   - Add `PERSONALAXIS_PASSWORD` variable
   - Keep `PERSONALAXIS_API_KEY` for backward compatibility (optional)

## Cookie Configuration

```python
response.set_cookie(
    key="personalaxis_session",
    value=session_token,
    httponly=True,      # XSS protection
    secure=True,        # HTTPS only (False for localhost)
    samesite="strict",  # CSRF protection
    max_age=30*24*3600, # 30 days
    path="/"
)
```

## Security Considerations

- Session tokens: 32-byte cryptographically secure random
- Session expiry: 30 days (long-lived for PWA convenience)
- `secure=False` only for localhost development
- Clean up expired sessions periodically

## Testing Checklist

- [ ] Login with correct password → session cookie set
- [ ] Login with wrong password → 401 error
- [ ] Access protected route with valid session → success
- [ ] Access protected route without session → 401 redirect to login
- [ ] Logout → cookie cleared, subsequent requests fail
- [ ] Expired session → 401, redirect to login
- [ ] Works on mobile Safari (iOS PWA)
