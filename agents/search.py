"""
Construtor para o agente de busca e conhecimento geral usando LangChain.
"""

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr

from agents.prompts import REACT_PROMPT
from config.settings import settings


def create_search_agent():
    """Cria e configura o agente de busca reativo.

    Returns:
        Runnable: O agente reativo pronto para ser usado no LangGraph.
    """
    # Configura os callbacks para observabilidade
    callbacks = [CallbackHandler()] if settings.observability.is_enabled else None

    # Ferramentas do agente
    tools = [DuckDuckGoSearchResults(name="search_tool", verbose=True)]

    # Instancia o modelo diretamente, que é a forma correta e robusta
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=SecretStr(settings.gemini_api_key),
        temperature=settings.ai_model_config.temperature,
        max_tokens=settings.ai_model_config.max_tokens,
        callbacks=callbacks,
    )

    # Criar agente reativo
    react_agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=REACT_PROMPT,
        name="search",
    )

    return react_agent, tools


def get_search_agent_info():
    """Retorna os metadados do agente de busca."""
    return {
        "name": "search",
        "description": "Use this agent to search the web for information. It can answer questions about any topic.",
        "capabilities_description": """I can help with:
        - Answering general questions about any topic
        - Explaining complex concepts in a simple way
        - Providing information about technology, science, history, etc.
        - Resolving doubts and clarifying definitions
        - Giving general suggestions and recommendations""",
        "capabilities": ["search"],
    }
