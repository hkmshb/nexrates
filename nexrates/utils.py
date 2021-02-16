import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic import AnyUrl, BaseSettings, HttpUrl, validator

BASE_DIR = Path(__file__).absolute().parent


def configure_logging():
    """Configures logging for the API service."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl
    LOG_LEVEL: int = logging.INFO
    RATES_DOC_URL: HttpUrl

    @validator('LOG_LEVEL', pre=True)
    def normalize_log_level(cls, value):
        return getattr(logging, value)


# load .env file
load_dotenv('.env')

# settings instance
settings = Settings()
