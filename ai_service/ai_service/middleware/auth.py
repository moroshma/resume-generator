# middleware/auth.py

from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
import httpx
from ai_service.config import settings # Assuming settings has AUTH_SERVICE_URL

# --- Define the expected cookie names ---
# Match the names used by the Go auth service
ACCESS_TOKEN_COOKIE_NAME = "Authorization"
REFRESH_TOKEN_COOKIE_NAME = "Refresh-Token"

async def verify_tokens_via_cookies(request: Request, call_next): # Renamed again
    """
    Middleware to verify JWT access token by calling an external authentication service,
    passing required cookies (Authorization and Refresh-Token).
    """
    # Allow OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)

    # Allow access to docs/openapi without authentication
    docs_url = getattr(request.app, "docs_url", "/docs")
    redoc_url = getattr(request.app, "redoc_url", "/redoc")
    openapi_url = getattr(request.app, "openapi_url", "/openapi.json")
    if request.url.path in [docs_url, redoc_url, openapi_url]:
         return await call_next(request)

    # --- Read BOTH cookies from the incoming request ---
    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

    # --- The Go service requires the refresh token first ---
    if not refresh_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": f"Not authenticated: Missing '{REFRESH_TOKEN_COOKIE_NAME}' cookie"},
        )

    # Although the Go service can potentially refresh the access token,
    # for a simple check endpoint, it might still expect the access token cookie
    # to be present initially. If it's truly optional, you could remove this check.
    # However, it's safer to assume the /check endpoint expects both if available.
    if not access_token:
         # If the access token is missing, but refresh is present, the Go service *might*
         # handle it IF the check endpoint triggers the refresh logic.
         # For simplicity here, we'll require it for the initial check.
         # Alternatively, you could proceed and let the Go service potentially fail/refresh.
         print(f"Warning: Missing '{ACCESS_TOKEN_COOKIE_NAME}' cookie, proceeding with refresh token only.")
         # If strictly required by the /check endpoint:
         # return JSONResponse(
         #     status_code=status.HTTP_401_UNAUTHORIZED,
         #     content={"detail": f"Not authenticated: Missing '{ACCESS_TOKEN_COOKIE_NAME}' cookie"},
         # )


    async with httpx.AsyncClient() as client:
        try:
            # --- Prepare COOKIES for the outgoing request to the Auth Service ---
            # Pass both cookies that the Go middleware expects
            auth_service_cookies = {}
            if access_token:
                 auth_service_cookies[ACCESS_TOKEN_COOKIE_NAME] = access_token
            if refresh_token:
                 auth_service_cookies[REFRESH_TOKEN_COOKIE_NAME] = refresh_token

            # Make the GET request to the authentication service, sending cookies
            response = await client.get(
                settings.AUTH_SERVICE_URL,
                cookies=auth_service_cookies,
                timeout=10.0
            )

            # --- MODIFIED SUCCESS CHECK ---
            # Accept both 200 OK and 204 No Content as success indicators
            if response.status_code in [200, 204]:
            # --- END MODIFICATION ---
                print(f"Authentication successful (Status: {response.status_code}) for request to {request.url.path}")
                return await call_next(request)
            elif response.status_code in [401, 403]:
                print(f"Authentication failed (Auth service returned {response.status_code}) for request to {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed: Invalid session or token"},
                )
            else:
                # Handle other unexpected auth service status codes (e.g., 5xx)
                print(f"Error communicating with auth service (Unexpected Status: {response.status_code}) for request to {request.url.path}")
                body = await response.text() # Get more details for logging if possible
                print(f"Auth service response body (if any): {body}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Could not verify authentication due to an internal error"},
                )


        # --- Error handling remains the same ---
        except httpx.RequestError as exc:
            print(f"Error calling authentication service at {settings.AUTH_SERVICE_URL}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": f"Authentication service unavailable: {exc}"},
            )
        except Exception as exc:
             print(f"Unexpected Python error during authentication processing: {exc}") # Clarified log
             # Also log the traceback for better debugging
             import traceback
             traceback.print_exc()
             return JSONResponse(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 content={"detail": f"An unexpected internal error occurred during authentication processing"}, # Clarified message
             )
