"""Settings management"""

import decimal
import uuid

import pydantic


class Settings(pydantic.BaseSettings):
    """Grocery Aid app settings"""

    database_url: pydantic.PostgresDsn = "postgresql+asyncpg://test@localhost/test"  # type: ignore

    store_root_namespace: uuid.UUID = pydantic.Field(
        default_factory=uuid.uuid4,
        description="The root namespace of UUID hierarchy used in the application",
    )

    # S-Group specific configuration
    sok_api_url: pydantic.AnyHttpUrl = "http://localhost/sok"  # type: ignore
    sok_store_ids: list[str] = []
    sok_products_batch_size: pydantic.PositiveInt = pydantic.Field(
        1000, description="Number of products fetched via API per query"
    )
    sok_products_fetch_limit: pydantic.NonNegativeInt = pydantic.Field(
        0,
        description="""
        Maximum number of products per store fetched via API. Set to zero to fetch
        all products. Setting to a small number is useful for testing.
        """,
    )

    # API defaults
    default_store_visit_bin_limit: decimal.Decimal = decimal.Decimal(10)

    class Config:
        env_file = ".env"


settings = Settings()
