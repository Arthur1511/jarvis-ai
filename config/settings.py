"""
Configurações centralizadas do Jarvis AI Assistant
"""

import os
from typing import Optional
from pydantic import BaseSettings, validator
from pathlib import Path


class Settings(BaseSettings):
    """Configurações do sistema"""

    # AI Models
    gemini_api_key: str

    # Observability
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # Spotify
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    spotify_redirect_uri: str = "http://localhost:8888/callback"

    # Gmail
    gmail_credentials_path: Path = Path("credentials/gmail_credentials.json")
    gmail_token_path: Path = Path("credentials/gmail_token.json")

    # GitHub
    github_token: Optional[str] = None
    github_username: Optional[str] = None

    # Azure DevOps
    azure_devops_org: Optional[str] = None
    azure_devops_project: Optional[str] = None
    azure_devops_pat: Optional[str] = None

    # Obsidian
    obsidian_vault_path: Optional[Path] = None

    # Database
    database_url: str = "sqlite:///jarvis.db"

    # Logging
    log_level: str = "INFO"

    # Model settings
    temperature: float = 0.1
    max_tokens: int = 4096

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("obsidian_vault_path", pre=True)
    def validate_obsidian_path(cls, v):
        if v and not Path(v).exists():
            print(f"Warning: Obsidian vault path does not exist: {v}")
        return Path(v) if v else None

    @property
    def is_langfuse_enabled(self) -> bool:
        """Verifica se LangFuse está configurado"""
        return bool(self.langfuse_secret_key and self.langfuse_public_key)

    @property
    def is_spotify_enabled(self) -> bool:
        """Verifica se Spotify está configurado"""
        return bool(self.spotify_client_id and self.spotify_client_secret)

    @property
    def is_gmail_enabled(self) -> bool:
        """Verifica se Gmail está configurado"""
        return self.gmail_credentials_path.exists()

    @property
    def is_github_enabled(self) -> bool:
        """Verifica se GitHub está configurado"""
        return bool(self.github_token and self.github_username)

    @property
    def is_obsidian_enabled(self) -> bool:
        """Verifica se Obsidian está configurado"""
        return bool(self.obsidian_vault_path and self.obsidian_vault_path.exists())


# Instância global das configurações
settings = Settings()
