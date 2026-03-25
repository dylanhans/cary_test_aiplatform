from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"
    use_azure: bool = False
    database_url: str = "postgresql://dylanhans@localhost:5432/cary_ai"
    api_secret_key: str = "dev_secret"
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()