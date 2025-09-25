from functools import lru_cache
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import SecretStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class EnvConfigService(BaseSettings):
  model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
    env_file=".env", extra="ignore", validate_default=True
  )

  OPENAI_API_KEY: SecretStr
  TAVILY_API_KEY: SecretStr

  PSQL_USERNAME: str
  PSQL_PASSWORD: SecretStr
  PSQL_HOST: str
  PSQL_PORT: int = 5432
  PSQL_DATABASE: str
  PSQL_SSLMODE: str = "disable"
  PSQL_CHAT_SESSIONS_SCHEMA: str = "chat_sessions"

  def __get_postgres_url(self, scheme: str) -> MultiHostUrl:
    return MultiHostUrl.build(
      scheme=scheme,
      username=self.PSQL_USERNAME,
      password=self.PSQL_PASSWORD.get_secret_value(),
      host=self.PSQL_HOST,
      path=self.PSQL_DATABASE,
      port=self.PSQL_PORT,
    )

  @computed_field
  @property
  def postgres_url(self) -> MultiHostUrl:
    return self.__get_postgres_url("postgresql")


@lru_cache
def get_env_configs() -> EnvConfigService:
  return EnvConfigService()
