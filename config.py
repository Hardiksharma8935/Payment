from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    OWNER_ID: int
    OWNER_USERNAME: str
    MAIN_CHANNEL: str

    class Config:
        env_file = ".env"
        extra = "ignore"

config = Settings()
