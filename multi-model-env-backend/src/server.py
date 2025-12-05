from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.lib.db import init_database, close_database
from src.routes import authroute, sessionroute, projectroute, messageroute, imageroute, geonliroute
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting GeoNLI Backend...")
    print(f"📍 Environment: {'Modal' if os.getenv('MODAL_ENV') else 'Local'}")
    print(f"📍 GPU: {os.getenv('MODAL_GPU', 'None')}")
    
    await init_database()
    print("✅ Database initialized")
    yield
    print("🛑 Shutting down...")
    await close_database()

app = FastAPI(
    title="GeoNLI API",
    description="AI-powered satellite image analysis platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://*.modal.run",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.include_router(authroute.router, prefix="/api")
app.include_router(sessionroute.router, prefix="/api")
app.include_router(projectroute.router, prefix="/api")
app.include_router(messageroute.router, prefix="/api")
app.include_router(imageroute.router, prefix="/api")
app.include_router(geonliroute.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GeoNLI API",
        "environment": "Modal" if os.getenv("MODAL_ENV") else "Local",
        "version": "1.0.0",
        "status": "running",
        "gpu": os.getenv("MODAL_GPU", "None")
    }

@app.get("/health")
async def health_check():
    import torch
    return {
        "status": "healthy",
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
    }

# --------------------- LOCAL RUN SUPPORT ---------------------

if __name__ == "__main__" and not os.getenv("MODAL_ENV"):
    import uvicorn
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
