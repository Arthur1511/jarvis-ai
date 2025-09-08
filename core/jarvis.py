"""
Classe principal do Jarvis AI Assistant
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from langfuse import Langfuse
from langfuse.decorators import observe

from config.settings import settings
from .router import AgentRouter
from agents.base import AgentResponse


class JarvisAI:
    """Classe principal do assistente Jarvis"""

    def __init__(self):
        self.router = AgentRouter()
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup LangFuse se configurado
        self.langfuse = None
        if settings.is_langfuse_enabled:
            self.langfuse = Langfuse(
                secret_key=settings.langfuse_secret_key,
                public_key=settings.langfuse_public_key,
                host=settings.langfuse_host,
            )

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        self.logger.info("Jarvis AI iniciado com sucesso")

    @observe(name="jarvis_process_query")
    async def process_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Processa uma query do usuário

        Args:
            query: A pergunta/comando do usuário
            context: Contexto adicional (histórico, preferências, etc.)

        Returns:
            AgentResponse: Resposta processada
        """
        try:
            self.logger.info(f"Processando query: {query[:50]}...")

            # Adicionar contexto do histórico recente
            enhanced_context = self._build_context(context)

            # Rotear query para agente apropriado
            response = await self.router.route_query(query, enhanced_context)

            # Salvar no histórico
            self._save_to_history(query, response)

            self.logger.info(f"Query processada com confiança: {response.confidence}")
            return response

        except Exception as e:
            self.logger.error(f"Erro ao processar query: {e}", exc_info=True)
            return AgentResponse(
                content=f"Desculpe, encontrei um erro interno: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
            )

    def _build_context(
        self, additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Constrói contexto enriquecido para a query"""
        context = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_length": len(self.conversation_history),
        }

        # Adicionar histórico recente (últimas 3 interações)
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]
            context["recent_queries"] = [item["query"] for item in recent_history]
            context["recent_responses"] = [
                item["response_summary"] for item in recent_history
            ]

        # Adicionar contexto adicional
        if additional_context:
            context.update(additional_context)

        return context

    def _save_to_history(self, query: str, response: AgentResponse):
        """Salva interação no histórico da conversa"""
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_summary": response.content[:100] + "..."
            if len(response.content) > 100
            else response.content,
            "confidence": response.confidence,
            "metadata": response.metadata,
        }

        self.conversation_history.append(history_item)

        # Limitar histórico (manter últimas 50 interações)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema e agentes"""
        agents_info = self.router.get_available_agents()

        return {
            "session_id": self.session_id,
            "conversation_length": len(self.conversation_history),
            "available_agents": list(agents_info.keys()),
            "agents_details": agents_info,
            "integrations": {
                "langfuse": settings.is_langfuse_enabled,
                "spotify": settings.is_spotify_enabled,
                "gmail": settings.is_gmail_enabled,
                "github": settings.is_github_enabled,
                "obsidian": settings.is_obsidian_enabled,
            },
            "last_interaction": (
                self.conversation_history[-1]["timestamp"]
                if self.conversation_history
                else None
            ),
        }

    def get_capabilities(self) -> str:
        """Retorna descrição das capacidades atuais"""
        capabilities = [
            "🔍 **Busca e Conhecimento Geral**",
            "   • Responder perguntas sobre qualquer tópico",
            "   • Explicar conceitos complexos",
            "   • Fornecer definições e esclarecimentos",
            "",
            "🚧 **Em Desenvolvimento**",
            "   • 📧 Gerenciamento de emails (Gmail)",
            "   • 🎵 Controle de música (Spotify)",
            "   • 📝 Geração de notas de standup",
            "   • 📋 Planejamento de sprints",
            "   • 📚 Integração com Obsidian",
        ]

        return "\n".join(capabilities)

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        try:
            # Teste simples com agente de busca
            test_response = await self.process_query("teste de conectividade")

            return {
                "status": "healthy",
                "agents_responding": test_response.confidence > 0,
                "langfuse_connected": self.langfuse is not None,
                "session_active": len(self.conversation_history) >= 0,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.conversation_history.clear()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger.info("Histórico de conversa limpo")

    async def shutdown(self):
        """Shutdown gracioso do sistema"""
        self.logger.info("Iniciando shutdown do Jarvis...")

        # Flush LangFuse se ativo
        if self.langfuse:
            self.langfuse.flush()

        self.logger.info("Jarvis desligado com sucesso")
