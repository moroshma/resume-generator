# main.py

from fastapi import FastAPI
# --- Annotation [main.py: 1] ---
# Import the settings instance from config.py
from ai_service.config import settings
# --- Annotation [main.py: 2] ---
# Import the router containing API endpoints.
from ai_service.routers import resume_1
# --- Annotation [main.py: 3] ---
# Import the new JWT verification middleware function.
from ai_service.middleware.auth import verify_tokens_via_cookies

# --- Annotation [main.py: 4] ---
# Create the FastAPI application instance.
# Use settings from config.py for title, description, version.
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    # --- Annotation [main.py: 5] ---
    # Explicitly define paths for documentation (optional but good practice).
    # These paths are automatically excluded from authentication by the middleware.
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- Annotation [main.py: 6] ---
# Add the JWT verification middleware to the FastAPI application.
# The string "http" means this middleware will process standard HTTP requests.
# Every request (except those explicitly skipped in the middleware)
# will now pass through 'verify_jwt_token' before reaching the route handlers.
app.middleware("http")(verify_tokens_via_cookies)

# --- Annotation [main.py: 7] ---
# Include the router defined in routers/resume.py.
# This makes the endpoints defined in that router available under the application.
# You can optionally add a prefix, e.g., app.include_router(resume.router, prefix="/api/v1")
app.include_router(resume_1.router)

# --- Annotation [main.py: 8] ---
# Optional: Add a simple root endpoint for health checks or basic info.
# This endpoint will also be protected by the middleware.
@app.get("/")
async def read_root():
    """ Basic endpoint to check if the service is running. """
    return {"message": f"Welcome to {settings.APP_TITLE}"}
