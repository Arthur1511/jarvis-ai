"""
Classe principal do Jarvis AI Assistant
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from langgraph.errors import GraphRecursionError
from langgraph_supervisor import create_supervisor
from pydantic import SecretStr

# Importa os construtores e metadados dos agentes
from agents.search import create_search_agent, get_search_agent_info
from config.settings import settings
from tools.date_tools import get_current_date


class JarvisAI:
    """Classe principal do assistente Jarvis"""

    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Setup LangFuse PRIMEIRO para que os handlers o encontrem
        self.langfuse = None
        self.langfuse_handler = None
        if settings.observability.is_enabled:
            self.langfuse = Langfuse(
                public_key=str(settings.observability.public_key),
                secret_key=str(settings.observability.secret_key),
                host=str(settings.observability.host),
            )
            self.langfuse_handler = CallbackHandler()

        # Inicializa agentes e seus metadados
        search_agent, search_tools = create_search_agent()
        self.agents = [
            search_agent,
            # Adicione novos agentes aqui como tupla
        ]
        self.all_tools = search_tools

        self.agents_metadata = [
            get_search_agent_info(),
            # "music": get_music_agent_info(),
        ]

        # LLM para o supervisor
        supervisor_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=SecretStr(settings.gemini_api_key),
            temperature=settings.ai_model_config.temperature,
        )

        # Cria grafo supervisor com os runnables dos agentes
        self.graph = create_supervisor(
            model=supervisor_llm,
            agents=self.agents,
            tools=[get_current_date],
            add_handoff_messages=True,
            add_handoff_back_messages=True,
            output_mode="last_message",
            prompt=(
                f"""
                    **SYSTEM IDENTITY:**
                    You are the central supervisor for JARVIS, an AI assistant inspired by Iron Man's J.A.R.V.I.S. Your primary role is to manage a team of specialized agents and ensure the user's request is handled efficiently and accurately. You do not perform tasks yourself; you delegate and orchestrate.

                    **AVAILABLE AGENTS:**
                    You have access to {len(self.agents)} agent(s):
                    {chr(10).join([f"- **{meta['name']}**: {meta['description']}" for meta in self.agents_metadata])}

                    **WORKFLOW:**
                    1.  **Analyze:** Carefully analyze the user's query and any provided context or conversation history.
                    2.  **Route:** Based on the analysis, determine the most appropriate agent to handle the query.
                    3.  **Delegate:** Assign the task to the selected agent. You must delegate to one agent at a time.
                    4.  **Supervise & Conclude:** Once the agent completes its work, you will receive its final output. Your last and final action is to present this result to the user in a clear and helpful manner. Frame the response as if you are JARVIS presenting the information.

                    **ROUTING EXAMPLE:**
                    - User Query: "who is the president of the USA in 2025?" -> Appropriate Agent: "search"
                    - User Query (Portuguese): "quem é o presidente dos EUA em 2025?" -> Appropriate Agent: "search"
                    - User Query: "what's the weather like in paris?" -> Appropriate Agent: "search"
                    - User Query (Portuguese): "como está o tempo em paris?" -> Appropriate Agent: "search"
                    - User Query: "summarize the last email I received" -> Appropriate Agent: "email" (if available)
                    - User Query (Portuguese): "resuma o último email que recebi" -> Appropriate Agent: "email" (if available)

                    **CRITICAL DIRECTIVES:**
                    - **Delegate, Don't Work:** Your only job is to route tasks to agents and present their final results. Do not answer questions or perform actions yourself.
                    - **One Agent at a Time:** Do not delegate to multiple agents in parallel.
                    - **No Suitable Agent:** If the user's query cannot be handled by any of your available agents, respond with: "I'm sorry, but that request is outside of my current capabilities."
                    - **Clarity is Key:** When presenting the final answer, ensure it is well-formatted and easy to understand.
                """
            ),
        ).compile()

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Jarvis AI iniciado com sucesso")

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Processa uma query do usuário
        """
        try:
            self.logger.info(f"Processando query: {query[:50]}...")
            enhanced_context = self._build_context(context)

            # Define o limite de iterações e os callbacks para a execução do grafo
            max_iterations = 3
            recursion_limit = 2 * max_iterations + 1
            config = {"recursion_limit": recursion_limit}
            if self.langfuse_handler:
                config["callbacks"] = [self.langfuse_handler]

            # Executa o grafo supervisor
            response_data = self.graph.invoke(
                {"messages": [("user", query)], "context": enhanced_context},
                config=config,
            )

            # A resposta final geralmente está na chave 'messages' do dicionário retornado
            final_message = response_data.get("messages", ["(sem resposta)"])[-1]
            final_content = (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )

            # Monta uma resposta estruturada para uso interno
            processed_response = {
                "content": final_content,
                "confidence": 0.9,  # Confiança é alta pois o supervisor escolheu um agente
                "metadata": {"raw_response": response_data},
            }

            self._save_to_history(query, processed_response)
            self.logger.info("Query processada com sucesso.")

            # Forçar o envio dos dados para o Langfuse
            if self.langfuse:
                self.langfuse.flush()

            return processed_response

        except GraphRecursionError:
            self.logger.warning("Limite de recursão do agente atingido.")
            return {
                "content": "I was unable to find a definitive answer in a reasonable number of steps. Please try rephrasing your question.",
                "confidence": 0.5,
                "metadata": {"error": "Recursion limit reached"},
            }
        except Exception as e:
            self.logger.error(f"Erro ao processar query: {e}", exc_info=True)
            return {
                "content": f"Desculpe, encontrei um erro interno: {str(e)}",
                "confidence": 0.0,
                "metadata": {"error": str(e)},
            }

    def _build_context(
        self,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Constrói contexto enriquecido para a query"""
        context = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_length": len(self.conversation_history),
        }
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]
            context["recent_queries"] = [item["query"] for item in recent_history]
            context["recent_responses"] = [
                item["response_summary"] for item in recent_history
            ]
        if additional_context:
            context.update(additional_context)
        return context

    def _save_to_history(self, query: str, response: Dict[str, Any]):
        """Salva interação no histórico da conversa"""
        content = response.get("content", "")
        history_item = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_summary": content[:100] + "..."
            if len(content) > 100
            else content,
            "confidence": response.get("confidence", 0.0),
            "metadata": response.get("metadata", {}),
        }
        self.conversation_history.append(history_item)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema e agentes"""
        return {
            "session_id": self.session_id,
            "conversation_length": len(self.conversation_history),
            "available_agents": list(self.agents.keys()),
            "agents_details": self.agents_metadata,
            "integrations": {
                "langfuse": settings.observability.is_enabled,
                "spotify": settings.spotify.is_enabled,
                "gmail": settings.gmail.is_enabled,
                "github": settings.github.is_enabled,
                "obsidian": settings.obsidian.is_enabled,
            },
            "last_interaction": (
                self.conversation_history[-1]["timestamp"]
                if self.conversation_history
                else None
            ),
        }

    def get_capabilities(self) -> str:
        """Retorna descrição das capacidades atuais"""
        # Esta função pode ser melhorada para buscar as descrições dos metadados
        capabilities = [
            "🔍 **Busca e Conhecimento Geral**",
            "   • Responder perguntas sobre qualquer tópico",
            "   • Explicar conceitos complexos",
            "",
            "🚧 **Em Desenvolvimento**",
            "   • 🎵 Controle de música (Spotify)",
        ]
        return "\n".join(capabilities)

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema"""
        try:
            test_response = await self.process_query("teste de conectividade")
            return {
                "status": "healthy",
                "agents_responding": test_response.get("confidence", 0) > 0,
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
        if self.langfuse:
            self.langfuse.flush()
        self.logger.info("Jarvis desligado com sucesso")
