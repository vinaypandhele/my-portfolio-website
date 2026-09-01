"""
Configuration file for Vinnuu PDF Tech
Environment variables and settings
"""

import os
from datetime import timedelta
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "Vinnuu PDF Tech"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", False)
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./vinnuu_pdf_tech.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # File Upload
    max_file_size_mb: int = 100
    upload_dir: str = "uploads/temp"
    processed_dir: str = "uploads/processed"
    allowed_pdf_extensions: list = [".pdf"]
    allowed_image_extensions: list = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"]
    
    # API
    api_version: str = "/api/v1"
    cors_origins: list = ["*"]
    
    # Email (Optional)
    smtp_server: str = os.getenv("SMTP_SERVER", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # Google API (for AI features)
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Initialize settings
settings = Settings()

# Common constants
FILE_CLEANUP_HOURS = 24
MAX_CONCURRENT_UPLOADS = 5
API_RATE_LIMIT = 100  # requests per hour
