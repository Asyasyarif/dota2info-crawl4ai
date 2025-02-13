from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # APP
    APP_NAME: str = "Dota2 Retrospective API"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    ENCRYPTION_KEY: str
    
    # DATABASE
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    # AI
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    DEEPSEEK_API_KEY: str
    TAVILY_API_KEY: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str

    # STEAM
    STEAM_API_KEY: str
    STEAM_REDIRECT_URL: str

    class Config:
        case_sensitive = True
        env_file = ".env"
        
settings = Settings()