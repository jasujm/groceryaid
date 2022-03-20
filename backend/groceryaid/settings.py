"""Settings management"""

import pydantic


class Settings(pydantic.BaseSettings):
    """Grocery Aid app settings"""

    database_url: pydantic.PostgresDsn = "postgresql+asyncpg://test@localhost/test"
    sok_api_url: pydantic.AnyHttpUrl = "http://localhost/sok"

    class Config:
        env_file = ".env"


settings = Settings()
