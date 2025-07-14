from fastapi import FastAPI
from ai_service.config import settings
from ai_service.routers import resume_1
from ai_service.middleware.auth import verify_tokens_via_cookies

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.middleware("http")(verify_tokens_via_cookies)

app.include_router(resume_1.router)

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.APP_TITLE}"}

