"""
Agente de busca e conhecimento geral usando Gemini Pro
"""

from typing import Dict, Any, Optional, List
import google.generativeai as genai
from langfuse.decorators import observe

from .base import BaseAgent, AgentResponse, AgentCapability
from config.settings import settings


class SearchAgent(BaseAgent):
    """Agente para busca de informações e conhecimento geral"""

    def __init__(self):
        super().__init__(
            name="SearchAgent",
            capabilities=[AgentCapability.SEARCH],
            description="Busca informações gerais e responde perguntas sobre conhecimento geral",
        )

        # Configurar Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-pro")

        # Palavras-chave que indicam busca/pesquisa
        self.search_keywords = [
            "buscar",
            "procurar",
            "pesquisar",
            "encontrar",
            "descobrir",
            "explicar",
            "definir",
            "o que é",
            "como",
            "quando",
            "onde",
            "por que",
            "porque",
            "qual",
            "quem",
            "info",
            "informação",
            "sobre",
            "acerca",
            "a respeito",
            "falar sobre",
            "me conte",
        ]

    async def can_handle(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """Determina se pode processar a query"""
        query_lower = query.lower()

        # Verifica palavras-chave de busca
        search_indicators = sum(
            1 for keyword in self.search_keywords if keyword in query_lower
        )

        # Verifica se não é claramente para outro agente
        music_keywords = ["tocar", "música", "playlist", "spotify", "som"]
        email_keywords = ["email", "e-mail", "gmail", "mensagem", "correio"]
        standup_keywords = ["standup", "stand-up", "reunião", "daily"]

        other_agent_indicators = (
            sum(1 for keyword in music_keywords if keyword in query_lower)
            + sum(1 for keyword in email_keywords if keyword in query_lower)
            + sum(1 for keyword in standup_keywords if keyword in query_lower)
        )

        # Se tem indicadores de busca e poucos indicadores de outros agentes
        if search_indicators > 0 and other_agent_indicators == 0:
            return min(0.9, 0.3 + (search_indicators * 0.15))

        # Se não tem indicadores específicos de outros agentes, pode ser busca geral
        if other_agent_indicators == 0:
            return 0.5  # Confiança média para queries gerais

        return 0.1  # Baixa confiança se parece ser para outro agente

    @observe(name="search_agent_process")
    async def process(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Processa a query usando Gemini Pro"""
        try:
            # Construir prompt com contexto
            system_prompt = """Você é JARVIS, o assistente de IA inspirado no Homem de Ferro.
Responda de forma clara, concisa e útil. Mantenha um tom profissional mas amigável.
Se a pergunta for sobre algo muito específico ou técnico, forneça exemplos práticos quando possível."""

            # Adicionar contexto se disponível
            full_prompt = f"{system_prompt}\n\nPergunta: {query}"
            if context:
                full_prompt += f"\n\nContexto adicional: {context}"

            # Gerar resposta
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.temperature,
                    max_output_tokens=settings.max_tokens,
                ),
            )

            return AgentResponse(
                content=response.text,
                confidence=0.8,
                metadata={
                    "model": "gemini-pro",
                    "tokens_used": len(response.text.split()) * 1.3,  # Aproximação
                },
            )

        except Exception as e:
            return AgentResponse(
                content=f"Desculpe, encontrei um erro ao processar sua pergunta: {str(e)}",
                confidence=0.0,
                metadata={"error": str(e)},
            )

    def get_capabilities_description(self) -> str:
        """Descrição das capacidades para o usuário"""
        return """Posso ajudar com:
• Responder perguntas gerais sobre qualquer tópico
• Explicar conceitos complexos de forma simples
• Fornecer informações sobre tecnologia, ciência, história, etc.
• Resolver dúvidas e esclarecer definições
• Dar sugestões e recomendações gerais"""
