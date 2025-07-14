    from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
import httpx
from ai_service.config import settings

ACCESS_TOKEN_COOKIE_NAME = "Authorization"
REFRESH_TOKEN_COOKIE_NAME = "Refresh-Token"

async def verify_tokens_via_cookies(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    docs_url = getattr(request.app, "docs_url", "/docs")
    redoc_url = getattr(request.app, "redoc_url", "/redoc")
    openapi_url = getattr(request.app, "openapi_url", "/openapi.json")
    if request.url.path in [docs_url, redoc_url, openapi_url]:
         return await call_next(request)

    access_token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": f"Not authenticated: Missing '{REFRESH_TOKEN_COOKIE_NAME}' cookie"},
        )

    if not access_token:
         print(f"Warning: Missing '{ACCESS_TOKEN_COOKIE_NAME}' cookie, proceeding with refresh token only.")

    async with httpx.AsyncClient() as client:
        try:
            auth_service_cookies = {}
            if access_token:
                 auth_service_cookies[ACCESS_TOKEN_COOKIE_NAME] = access_token
            if refresh_token:
                 auth_service_cookies[REFRESH_TOKEN_COOKIE_NAME] = refresh_token

            response = await client.get(
                settings.AUTH_SERVICE_URL,
                cookies=auth_service_cookies,
                timeout=10.0
            )

            if response.status_code in [200, 204]:
                print(f"Authentication successful (Status: {response.status_code}) for request to {request.url.path}")
                return await call_next(request)
            elif response.status_code in [401, 403]:
                print(f"Authentication failed (Auth service returned {response.status_code}) for request to {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed: Invalid session or token"},
                )
            else:
                print(f"Error communicating with auth service (Unexpected Status: {response.status_code}) for request to {request.url.path}")
                body = await response.text()
                print(f"Auth service response body (if any): {body}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Could not verify authentication due to an internal error"},
                )

        except httpx.RequestError as exc:
            print(f"Error calling authentication service at {settings.AUTH_SERVICE_URL}: {exc}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": f"Authentication service unavailable: {exc}"},
            )
        except Exception as exc:
             print(f"Unexpected Python error during authentication processing: {exc}")
             import traceback
             traceback.print_exc()
             return JSONResponse(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 content={"detail": f"An unexpected internal error occurred during authentication processing"},
             )
