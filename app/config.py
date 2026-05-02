from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import List, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./timeless.db"  # Default to SQLite for development
    
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
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str], None]):
        if v is None:
            return ["http://localhost:3000", "http://localhost:8000"]
        if isinstance(v, list):
            return v
        s = str(v).strip()
        if s.startswith("["):
            import json
            return json.loads(s)
        return [x.strip() for x in s.split(",") if x.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
