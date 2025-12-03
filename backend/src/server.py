from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from lib.db import init_database, close_database
from routes import authroute, sessionroute, projectroute, messageroute, imageroute, geonliroute
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    print("Starting up...")
    await init_database()
    yield
    # Shutdown
    print("Shutting down...")
    await close_database()


# Initialize FastAPI app
app = FastAPI(
    title="Geonli API",
    description="AI-powered satellite image analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS - THIS IS THE FIX
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL, 
        "http://localhost:3000", 
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include routers
app.include_router(authroute.router, prefix="/api")
app.include_router(sessionroute.router, prefix="/api")
app.include_router(projectroute.router, prefix="/api")
app.include_router(messageroute.router, prefix="/api")
app.include_router(imageroute.router, prefix="/api")
app.include_router(geonliroute.router) 

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Geonli API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    PORT = int(os.getenv("PORT", 5001))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )