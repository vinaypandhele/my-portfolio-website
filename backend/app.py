"""
Vinnuu PDF Tech - Main FastAPI Application
Comprehensive PDF and Image Processing Platform
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime, timedelta
import logging

# Import routes
from routes import auth, pdf_tools, image_tools, admin, files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vinnuu PDF Tech API",
    description="All-in-One PDF & AI Image Tools",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vinnuu_pdf_tech.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create upload directories
UPLOAD_DIR = "uploads/temp"
PROCESSED_DIR = "uploads/processed"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ==========================================
# API Routes
# ==========================================

# Authentication routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# PDF Tools routes
app.include_router(pdf_tools.router, prefix="/api/pdf", tags=["PDF Tools"])

# Image Tools routes
app.include_router(image_tools.router, prefix="/api/image", tags=["Image Tools"])

# File management routes
app.include_router(files.router, prefix="/api/files", tags=["Files"])

# Admin routes
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# ==========================================
# Health Check & Info Endpoints
# ==========================================

@app.get("/")
async def root():
    """Root endpoint - Redirect to frontend"""
    return {"message": "Vinnuu PDF Tech API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "Vinnuu PDF Tech API",
        "version": "1.0.0",
        "description": "All-in-One PDF & AI Image Processing Platform",
        "endpoints": {
            "auth": "/api/auth",
            "pdf": "/api/pdf",
            "image": "/api/image",
            "files": "/api/files",
            "admin": "/api/admin"
        }
    }

# ==========================================
# File Cleanup Task
# ==========================================

async def cleanup_old_files(background_tasks: BackgroundTasks):
    """
    Background task to delete files older than 24 hours
    """
    try:
        import shutil
        current_time = datetime.now()
        
        for directory in [UPLOAD_DIR, PROCESSED_DIR]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if current_time - file_time > timedelta(hours=24):
                            os.remove(file_path)
                            logger.info(f"Deleted old file: {filename}")
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

# Schedule cleanup task (call this periodically)
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Vinnuu PDF Tech API started successfully")
    # Initialize database tables
    # Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Vinnuu PDF Tech API shutdown")

# ==========================================
# Error Handlers
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return {
        "success": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "success": False,
        "error": "Internal server error",
        "status_code": 500
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
