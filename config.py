from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    OWNER_ID: int
    OWNER_USERNAME: str
    MAIN_CHANNEL: str
    
    # Configurable Crypto Addresses
    USDT_ADDRESS: str = "Not Configured"
    BTC_ADDRESS: str = "Not Configured"
    ETH_ADDRESS: str = "Not Configured"
    SOL_ADDRESS: str = "Not Configured"

    class Config:
        env_file = ".env"
        extra = "ignore"

config = Settings()
