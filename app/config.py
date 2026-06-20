from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # MongoDB (URI must include auth for Atlas; db name in path or use mongodb_db_name)
    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db_name: str = "timeless"

    # Server
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "your-32-byte-encryption-key-123456"

    # CORS (env: JSON array or comma-separated, e.g. https://myapp.vercel.app)
    cors_origins: Union[str, List[str]] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://timless-front.vercel.app",
    ]

    # SMTP Settings (legacy - kept for reference)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@timeless.app"

    # Resend API (primary email provider)
    resend_api_key: str = ""

    # httpSMS Settings
    httpsms_api_key: str = ""
    httpsms_from_phone: str = ""

    # Frontend URL
    frontend_url: str = "https://timless-front.vercel.app"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str], None]):
        if v is None:
            return ["http://localhost:3000", "http://localhost:8000", "https://timless-front.vercel.app"]
        if isinstance(v, list):
            return v
        
        s = str(v).strip()
        if not s:
            return ["http://localhost:3000", "http://localhost:8000", "https://timless-front.vercel.app"]
            
        if s.startswith("["):
            try:
                import json
                return json.loads(s)
            except Exception:
                # Fallback if JSON is malformed
                pass
        
        # Split by comma for non-JSON or malformed JSON strings
        return [x.strip() for x in s.split(",") if x.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
