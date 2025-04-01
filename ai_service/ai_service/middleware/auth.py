# middleware/auth.py (New file)

# --- Annotation [middleware/auth.py: 1] ---
# Import necessary modules from FastAPI for handling requests and responses.
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse

# --- Annotation [middleware/auth.py: 2] ---
# Import 'httpx' for making asynchronous HTTP requests to the auth service.
# Using async client prevents blocking the FastAPI application.
import httpx

# --- Annotation [middleware/auth.py: 3] ---
# Import the settings instance to get the AUTH_SERVICE_URL.
from ai_service.config import settings

# --- Annotation [middleware/auth.py: 4] ---
# Define an asynchronous middleware function.
# FastAPI middleware functions take the 'request' and 'call_next' function as arguments.
# 'call_next' passes the request to the next middleware or the actual route handler.
async def verify_jwt_token(request: Request, call_next):
    """
    Middleware to verify JWT token by calling an external authentication service.
    """
    # --- Annotation [middleware/auth.py: 5] ---
    # Allow OPTIONS requests (used for CORS preflight checks) to pass through
    # without authentication, as they don't carry credentials.
    if request.method == "OPTIONS":
        return await call_next(request)

    # --- Annotation [middleware/auth.py: 6] ---
    # Allow access to FastAPI's automatic documentation endpoints (/docs, /redoc)
    # and the OpenAPI schema (/openapi.json) without requiring a token.
    # This makes it easier to explore the API.
    if request.url.path in [f"{request.app.docs_url}", f"{request.app.redoc_url}", f"{request.app.openapi_url}"]:
         return await call_next(request)

    # --- Annotation [middleware/auth.py: 7] ---
    # Try to get the 'Authorization' header from the incoming request.
    auth_header = request.headers.get("Authorization")
    token = None

    # --- Annotation [middleware/auth.py: 8] ---
    # Check if the header exists and starts with "Bearer ".
    # This is the standard way to send JWT tokens.
    if auth_header and auth_header.startswith("Bearer "):
        # Extract the token part after "Bearer ".
        token = auth_header.split(" ")[1]

    # --- Annotation [middleware/auth.py: 9] ---
    # If no token is found (header missing or incorrect format),
    # return a 401 Unauthorized response immediately.
    if not token:
        # Using JSONResponse directly allows customizing the response body.
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Not authenticated: Missing or invalid Authorization header"},
        )

    # --- Annotation [middleware/auth.py: 10] ---
    # Use an 'async with' block to create an httpx.AsyncClient.
    # This ensures the client's resources (like connections) are properly managed and closed.
    async with httpx.AsyncClient() as client:
        try:
            # --- Annotation [middleware/auth.py: 11] ---
            # Prepare the headers for the request to the authentication service.
            # We forward the original 'Authorization' header containing the Bearer token.
            auth_service_headers = {"Authorization": auth_header}

            # --- Annotation [middleware/auth.py: 12] ---
            # Make an asynchronous GET request to the configured AUTH_SERVICE_URL.
            # Pass the headers required by the auth service. Set a timeout.
            response = await client.get(
                settings.AUTH_SERVICE_URL,
                headers=auth_service_headers,
                timeout=10.0 # Add a reasonable timeout (e.g., 10 seconds)
            )

            # --- Annotation [middleware/auth.py: 13] ---
            # Check the status code returned by the authentication service.
            if response.status_code == 200:
                # --- Annotation [middleware/auth.py: 14] ---
                # If the auth service returns 200 OK, the token is valid.
                # Proceed to the actual route handler by calling 'call_next'.
                # You might optionally want to attach user info from the auth response
                # to the request state if the auth service returns it:
                # try:
                #     user_info = response.json()
                #     request.state.user = user_info # Make user info available in routes
                # except Exception:
                #     request.state.user = None # Handle cases where parsing fails
                print(f"Authentication successful for request to {request.url.path}") # Optional logging
                return await call_next(request)
            elif response.status_code in [401, 403]:
                # --- Annotation [middleware/auth.py: 15] ---
                # If the auth service returns 401 or 403, the token is invalid or expired.
                # Return a 401 Unauthorized from our service.
                print(f"Authentication failed (Auth service returned {response.status_code}) for request to {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication failed: Invalid or expired token"},
                )
            else:
                # --- Annotation [middleware/auth.py: 16] ---
                # If the auth service returns any other error status code (e.g., 5xx),
                # it indicates a problem with the auth service itself.
                # Return a 500 Internal Server Error from our service.
                print(f"Error communicating with auth service (Status: {response.status_code}) for request to {request.url.path}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Could not verify authentication due to an internal error"},
                )

        # --- Annotation [middleware/auth.py: 17] ---
        # Catch potential network errors (e.g., connection refused, timeout)
        # when trying to reach the authentication service.
        except httpx.RequestError as exc:
            print(f"Error calling authentication service at {settings.AUTH_SERVICE_URL}: {exc}")
            # Return a 503 Service Unavailable error, indicating the dependency is down.
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": f"Authentication service unavailable: {exc}"},
            )
        # --- Annotation [middleware/auth.py: 18] ---
        # Catch any other unexpected exceptions during the process.
        except Exception as exc:
            print(f"Unexpected error during authentication: {exc}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"An unexpected error occurred during authentication"},
            )
