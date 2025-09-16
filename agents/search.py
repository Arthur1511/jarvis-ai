"""
Construtor para o agente de busca e conhecimento geral usando LangChain.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langfuse.langchain import CallbackHandler
from langgraph.prebuilt import create_react_agent
from pydantic import SecretStr

from agents.prompts import SEARCH_AGENT_SYSTEM_PROMPT
from config.settings import settings
from tools.date_tools import get_current_date


def create_search_agent():
    """Cria e configura o agente de busca reativo.

    Returns:
        Runnable: O agente reativo pronto para ser usado no LangGraph.
    """
    # Configura os callbacks para observabilidade
    callbacks = [CallbackHandler()] if settings.observability.is_enabled else None

    # Ferramentas do agente
    tools = [TavilySearch(max_results=10, topic="general"), get_current_date]

    # Instancia o modelo diretamente, que é a forma correta e robusta
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=SecretStr(settings.gemini_api_key),
        temperature=settings.ai_model_config.temperature,
        max_tokens=settings.ai_model_config.max_tokens,
        callbacks=callbacks,
    )

    # Criar agente reativo
    react_agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SEARCH_AGENT_SYSTEM_PROMPT,
        name="search",
    )

    return react_agent, tools


def get_search_agent_info():
    """Retorna os metadados do agente de busca."""
    return {
        "name": "search",
        "description": "Use this agent to search the web for up-to-date information. It is the best choice for questions about current events, facts, and topics that may have changed over time, including questions about specific dates or years. (Em Português: Use este agente para pesquisar informações atualizadas na web. É a melhor escolha para perguntas sobre eventos atuais, fatos e tópicos que podem ter mudado com o tempo, incluindo perguntas sobre datas ou anos específicos.)",
        "capabilities_description": """I can help with:
        - Answering general questions about any topic
        - Finding the most current information on events and people
        - Explaining complex concepts in a simple way
        - Providing information about technology, science, history, etc.
        - Resolving doubts and clarifying definitions""",
        "capabilities": ["search", "date"],
    }
