from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Dota2 Scraper API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    class Config:
        case_sensitive = True

settings = Settings() 