"""
Configurações centralizadas do Jarvis AI Assistant usando Pydantic V2.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configuração padrão para todos os modelos que precisam ler do .env
ENV_CONFIG = SettingsConfigDict(env_file=".env", extra='ignore')


# --- Modelos de Configuração por Serviço ---

class AiModelConfig(BaseSettings):
    """Configurações de comportamento dos modelos de IA"""
    model_config = ENV_CONFIG
    temperature: float = Field(0.5, description="Temperatura para a geração do modelo", alias="MODEL_TEMPERATURE")
    max_tokens: int = Field(4096, description="Máximo de tokens na resposta do modelo", alias="MODEL_MAX_TOKENS")

class TavilySettings(BaseSettings):
    """Configurações da integração com Tavily Search"""
    model_config = ENV_CONFIG
    api_key: Optional[str] = Field(None, alias="TAVILY_API_KEY")

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)
class ObservabilitySettings(BaseSettings):
    """Configurações de Observabilidade (LangFuse)"""
    model_config = ENV_CONFIG
    secret_key: Optional[str] = Field(None, alias="LANGFUSE_SECRET_KEY")
    public_key: Optional[str] = Field(None, alias="LANGFUSE_PUBLIC_KEY")
    host: str = Field("https://cloud.langfuse.com", alias="LANGFUSE_HOST")

    @property
    def is_enabled(self) -> bool:
        return bool(self.secret_key and self.public_key)

class SpotifySettings(BaseSettings):
    """Configurações da integração com Spotify"""
    model_config = ENV_CONFIG
    client_id: Optional[str] = Field(None, alias="SPOTIFY_CLIENT_ID")
    client_secret: Optional[str] = Field(None, alias="SPOTIFY_CLIENT_SECRET")
    redirect_uri: str = Field("http://localhost:8888/callback", alias="SPOTIFY_REDIRECT_URI")

    @property
    def is_enabled(self) -> bool:
        return bool(self.client_id and self.client_secret)

class GmailSettings(BaseSettings):
    """Configurações da integração com Gmail"""
    model_config = ENV_CONFIG
    credentials_path: Path = Path("credentials/gmail_credentials.json")
    token_path: Path = Path("credentials/gmail_token.json")

    @property
    def is_enabled(self) -> bool:
        return self.credentials_path.exists()

class GitHubSettings(BaseSettings):
    """Configurações da integração com GitHub"""
    model_config = ENV_CONFIG
    token: Optional[str] = Field(None, alias="GITHUB_TOKEN")
    username: Optional[str] = Field(None, alias="GITHUB_USERNAME")

    @property
    def is_enabled(self) -> bool:
        return bool(self.token and self.username)

class ObsidianSettings(BaseSettings):
    """Configurações da integração com Obsidian"""
    model_config = ENV_CONFIG
    vault_path: Optional[Path] = Field(None, alias="OBSIDIAN_VAULT_PATH")

    @field_validator("vault_path", mode='before')
    @classmethod
    def validate_path(cls, v):
        if not v:
            return None
        path = Path(v)
        if not path.exists():
            print(f"Aviso: O caminho para o vault do Obsidian não existe: {v}")
        return path

    @property
    def is_enabled(self) -> bool:
        return bool(self.vault_path and self.vault_path.exists())


# --- Classe Principal de Configurações ---

class Settings(BaseSettings):
    """Agrega todas as configurações do sistema"""
    model_config = ENV_CONFIG

    # Segredos e chaves de API de primeiro nível
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")

    # Grupos de configuração aninhados
    ai_model_config: AiModelConfig = Field(default_factory=AiModelConfig)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    tavily: TavilySettings = Field(default_factory=TavilySettings)
    spotify: SpotifySettings = Field(default_factory=SpotifySettings)
    gmail: GmailSettings = Field(default_factory=GmailSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    obsidian: ObsidianSettings = Field(default_factory=ObsidianSettings)

    # Configurações gerais
    database_url: str = "sqlite:///jarvis.db"
    log_level: str = "INFO"


# --- Instância Global ---
settings = Settings()
