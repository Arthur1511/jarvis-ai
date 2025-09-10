"""
Construtor para o agente de busca e conhecimento geral usando LangChain.
"""

from langgraph.prebuilt import create_react_agent
from langchain.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse.langchain import CallbackHandler
from pydantic import SecretStr

from config.settings import settings


def create_search_agent():
    """Cria e configura o agente de busca reativo.

    Returns:
        Runnable: O agente reativo pronto para ser usado no LangGraph.
    """
    # Configura os callbacks para observabilidade
    # Configura os callbacks para observabilidade
    callbacks = [CallbackHandler()] if settings.observability.is_enabled else None

    # Instancia o modelo diretamente, que é a forma correta e robusta
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=SecretStr(settings.gemini_api_key),
        temperature=settings.ai_model_config.temperature,
        max_tokens=settings.ai_model_config.max_tokens,
        callbacks=callbacks,
    )

    # Ferramentas do agente
    tools = [DuckDuckGoSearchRun()]

    # Este prompt é um template padrão para agentes ReAct, com a persona do JARVIS adicionada.
    template = """Você é JARVIS, o assistente de IA inspirado no Homem de Ferro. Responda de forma clara, concisa e útil.
Você tem acesso às seguintes ferramentas:

{tools}

Use o seguinte formato:

Question: A pergunta que você deve responder
Thought: Você deve sempre pensar sobre o que fazer
Action: A ação a ser tomada, deve ser uma de [{tool_names}]
Action Input: A entrada para a ação
Observation: O resultado da ação
... (Este padrão de Thought/Action/Action Input/Observation pode se repetir N vezes)
Thought: Eu agora sei a resposta final
Final Answer: A resposta final para a pergunta original

Comece!

Question: {input}
Thought:{agent_scratchpad}"""
    prompt_template = ChatPromptTemplate.from_template(template)

    # Criar agente reativo
    react_agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=prompt_template,
        name="SearchAgent",
    )

    return react_agent

def get_search_agent_info():
    """Retorna os metadados do agente de busca."""
    return {
        "description": "Busca informações gerais e responde perguntas sobre conhecimento geral",
        "capabilities_description": """Posso ajudar com:\n• Responder perguntas gerais sobre qualquer tópico
• Explicar conceitos complexos de forma simples
• Fornecer informações sobre tecnologia, ciência, história, etc.
• Resolver dúvidas e esclarecer definições
• Dar sugestões e recomendações gerais""",
        "capabilities": ["search"],
    }