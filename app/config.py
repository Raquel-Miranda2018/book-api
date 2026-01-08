class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "book-recommendation-api"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./data/books.db"

    # Admin user credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "Admin@123"

    # JWT settings
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS settings (ADICIONE ESTA LINHA)
    ALLOWED_ORIGINS: list = ["*"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()