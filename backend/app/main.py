from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth as auth_router
from app.routers import competitors as competitors_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[startup] Environment: {settings.ENVIRONMENT}")
    print(f"[startup] App running on FastAPI")
    yield
    print("[shutdown] Goodbye.")


app = FastAPI(
    title="AI Ads Supervisor API",
    description="Backend for the AI Ads Supervisor platform.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(competitors_router.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "app": "AI Ads Supervisor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}