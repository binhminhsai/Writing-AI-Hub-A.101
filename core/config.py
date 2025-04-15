from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None  # Changed from OPENAI_API_KEY to openai_api_key
    
    class Config:
        env_file = ".env"

settings = Settings()
