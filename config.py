from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    WATCH_PATH: str
    DATABASE_PATH: str

    @property
    def get_database_url(self):
        return f"sqlite:///{self.DATABASE_PATH}"


    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
