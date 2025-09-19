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
from agents.prompts import SUPERVISOR_PROMPT
from agents.search import create_search_agent, get_search_agent_info
from config.settings import settings
from tools.date_tools import get_current_date


class JarvisAI:
    """Classe principal do assistente Jarvis"""

    def __init__(self):
        self.conversation_history: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.langfuse = None
        self.langfuse_handler = None
        self.agents = []
        self.agents_metadata = []
        self.all_tools = []

        self._setup_logging()
        self._setup_observability()
        self._create_agents()
        self.graph = self._build_supervisor()
        
        self.logger.info("Jarvis AI iniciado com sucesso")

    def _setup_logging(self):
        """Configura o logging para a aplicação."""
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

    def _setup_observability(self):
        """Inicializa o LangFuse se estiver habilitado."""
        if settings.observability.is_enabled:
            self.langfuse = Langfuse(
                public_key=str(settings.observability.public_key),
                secret_key=str(settings.observability.secret_key),
                host=str(settings.observability.host),
            )
            self.langfuse_handler = CallbackHandler()
            self.logger.info("LangFuse de observabilidade habilitado.")

    def _create_agents(self):
        """Cria e registra todos os agentes disponíveis."""
        search_agent, search_tools = create_search_agent()
        self.agents.append(search_agent)
        self.agents_metadata.append(get_search_agent_info())
        self.all_tools.extend(search_tools)
        # Adicione novos agentes aqui

    def _build_supervisor(self):
        """Constrói o grafo do supervisor com os agentes registrados."""
        supervisor_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            api_key=SecretStr(settings.gemini_api_key),
            temperature=settings.ai_model_config.temperature,
        )

        agent_descriptions = "\n".join(
            [f"- **{meta['name']}**: {meta['description']}" for meta in self.agents_metadata]
        )
        supervisor_system_prompt = SUPERVISOR_PROMPT.format(
            num_agents=len(self.agents), agent_descriptions=agent_descriptions
        )

        return create_supervisor(
            model=supervisor_llm,
            agents=self.agents,
            tools=[get_current_date],
            add_handoff_messages=True,
            add_handoff_back_messages=True,
            output_mode="last_message",
            prompt=supervisor_system_prompt,
        ).compile()

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
            "available_agents": [agent["name"] for agent in self.agents_metadata],
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
        """Retorna descrição das capacidades atuais, gerada dinamicamente."""
        if not self.agents_metadata:
            return "Nenhuma capacidade disponível no momento."

        capabilities_list = []
        for meta in self.agents_metadata:
            # Adiciona o nome do agente como um título
            agent_name = meta.get("name", "Agente Desconhecido").replace("_", " ").title()
            capabilities_list.append(f"### 🤖 {agent_name}")
            
            # Adiciona a descrição das capacidades do agente
            description = meta.get("capabilities_description", "Nenhuma descrição de capacidade fornecida.")
            # Formata a descrição para melhor leitura, adicionando bullets
            formatted_description = "\n".join([f"- {line.strip()}" for line in description.split('-') if line.strip()])
            capabilities_list.append(formatted_description)
            capabilities_list.append("") # Adiciona uma linha em branco para separação

        # Adiciona uma seção para funcionalidades em desenvolvimento
        capabilities_list.append("### 🚧 Em Desenvolvimento")
        capabilities_list.append("- 🎵 Controle de música (Spotify)")
        capabilities_list.append("- 📧 Leitura e envio de e-mails (Gmail)")

        return "\n".join(capabilities_list)

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
