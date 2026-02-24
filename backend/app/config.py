from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/joya"
    s3_bucket: str = "joya-pdfs"
    s3_endpoint_url: str | None = None
    s3_access_key: str = ""
    s3_secret_key: str = ""
    font_dir: str = "fonts"
    image_dir: str = "images"


settings = Settings()
