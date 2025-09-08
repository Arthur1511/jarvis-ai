"""
Classe base para todos os agentes do Jarvis
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from enum import Enum


class AgentCapability(Enum):
    """Capacidades dos agentes"""

    SEARCH = "search"
    EMAIL = "email"
    MUSIC = "music"
    STANDUP = "standup"
    PLANNING = "planning"


class AgentResponse(BaseModel):
    """Resposta padronizada dos agentes"""

    content: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None
    requires_action: bool = False
    action_data: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Classe base para todos os agentes"""

    def __init__(
        self, name: str, capabilities: List[AgentCapability], description: str
    ):
        self.name = name
        self.capabilities = capabilities
        self.description = description

    @abstractmethod
    async def can_handle(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Determina se o agente pode processar a query

        Args:
            query: Query do usuário
            context: Contexto adicional

        Returns:
            float: Confiança de 0.0 a 1.0
        """
        pass

    @abstractmethod
    async def process(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Processa a query e retorna uma resposta

        Args:
            query: Query do usuário
            context: Contexto adicional

        Returns:
            AgentResponse: Resposta processada
        """
        pass

    def _extract_keywords(self, query: str) -> List[str]:
        """Extrai palavras-chave da query para análise"""
        # Implementação simples - pode ser melhorada
        import re

        words = re.findall(r"\b\w+\b", query.lower())
        stop_words = {
            "o",
            "a",
            "de",
            "que",
            "e",
            "do",
            "da",
            "em",
            "para",
            "com",
            "não",
            "uma",
            "os",
            "no",
            "se",
            "na",
            "por",
            "mais",
            "as",
            "dos",
            "como",
            "mas",
            "foi",
            "ao",
            "ele",
            "das",
            "tem",
            "à",
            "seu",
            "sua",
            "ou",
            "ser",
            "quando",
            "muito",
            "há",
            "nos",
            "já",
            "está",
            "eu",
            "também",
            "só",
            "pelo",
            "pela",
            "até",
            "isso",
            "ela",
            "entre",
            "era",
            "depois",
            "sem",
            "mesmo",
            "aos",
            "ter",
            "seus",
            "suas",
            "numa",
            "nem",
            "suas",
            "meu",
            "às",
            "minha",
            "têm",
            "numa",
            "pelos",
            "pelas",
        }
        return [word for word in words if word not in stop_words and len(word) > 2]

    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o agente"""
        return {
            "name": self.name,
            "capabilities": [cap.value for cap in self.capabilities],
            "description": self.description,
        }
