"""
Roteamento inteligente de agentes usando LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from agents.base import BaseAgent, AgentResponse
from agents.search import SearchAgent
# Imports dos outros agentes serão adicionados conforme implementamos


class RouterState(TypedDict):
    """Estado do roteador LangGraph"""

    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    context: Optional[Dict[str, Any]]
    selected_agent: Optional[str]
    confidence_scores: Dict[str, float]
    response: Optional[AgentResponse]


class AgentRouter:
    """Roteador inteligente de agentes usando LangGraph"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.graph = None
        self._setup_agents()
        self._build_graph()

    def _setup_agents(self):
        """Inicializa todos os agentes disponíveis"""
        # Inicializar agentes
        self.agents["search"] = SearchAgent()

        # TODO: Adicionar outros agentes conforme implementamos
        # self.agents["email"] = EmailAgent()
        # self.agents["music"] = MusicAgent()
        # self.agents["standup"] = StandupAgent()
        # self.agents["planning"] = PlanningAgent()

    def _build_graph(self):
        """Constrói o grafo de roteamento com LangGraph"""
        workflow = StateGraph(RouterState)

        # Adicionar nós
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("select_agent", self._select_agent)
        workflow.add_node("process_query", self._process_query)
        workflow.add_node("format_response", self._format_response)

        # Definir fluxo
        workflow.set_entry_point("analyze_query")
        workflow.add_edge("analyze_query", "select_agent")
        workflow.add_edge("select_agent", "process_query")
        workflow.add_edge("process_query", "format_response")
        workflow.add_edge("format_response", END)

        # Compilar grafo
        self.graph = workflow.compile()

    async def _analyze_query(self, state: RouterState) -> RouterState:
        """Analisa a query e extrai informações relevantes"""
        query = state["query"]

        # Extrair contexto simples (pode ser expandido)
        context = {
            "length": len(query),
            "has_question_mark": "?" in query,
            "words": query.split(),
            "timestamp": "now",  # Pode adicionar timestamp real
        }

        state["context"] = context
        return state

    async def _select_agent(self, state: RouterState) -> RouterState:
        """Seleciona o melhor agente para a query"""
        query = state["query"]
        context = state.get("context")

        # Calcular scores de confiança para cada agente
        confidence_scores = {}
        for agent_name, agent in self.agents.items():
            try:
                score = await agent.can_handle(query, context)
                confidence_scores[agent_name] = score
            except Exception as e:
                print(f"Erro ao calcular score para {agent_name}: {e}")
                confidence_scores[agent_name] = 0.0

        # Selecionar agente com maior confiança
        if confidence_scores:
            selected_agent = max(confidence_scores, key=confidence_scores.get)
            max_score = confidence_scores[selected_agent]

            # Se a confiança é muito baixa, usar agente padrão
            if max_score < 0.3:
                selected_agent = "search"  # Agente padrão
        else:
            selected_agent = "search"

        state["selected_agent"] = selected_agent
        state["confidence_scores"] = confidence_scores
        return state

    async def _process_query(self, state: RouterState) -> RouterState:
        """Processa a query usando o agente selecionado"""
        selected_agent = state["selected_agent"]
        query = state["query"]
        context = state.get("context")

        if selected_agent in self.agents:
            agent = self.agents[selected_agent]
            response = await agent.process(query, context)
        else:
            # Fallback para agente de busca
            agent = self.agents["search"]
            response = await agent.process(query, context)

        state["response"] = response
        return state

    async def _format_response(self, state: RouterState) -> RouterState:
        """Formata a resposta final"""
        response = state["response"]

        # Adicionar mensagem AI ao histórico
        if response:
            ai_message = AIMessage(content=response.content)
            state["messages"].append(ai_message)

        return state

    async def route_query(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Rota uma query para o agente apropriado"""

        # Estado inicial
        initial_state = RouterState(
            messages=[HumanMessage(content=query)],
            query=query,
            context=context,
            selected_agent=None,
            confidence_scores={},
            response=None,
        )

        # Executar grafo
        result = await self.graph.ainvoke(initial_state)

        # Retornar resposta
        return result.get(
            "response",
            AgentResponse(
                content="Desculpe, não consegui processar sua solicitação.",
                confidence=0.0,
            ),
        )

    def get_available_agents(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações sobre agentes disponíveis"""
        return {name: agent.get_info() for name, agent in self.agents.items()}

    def add_agent(self, name: str, agent: BaseAgent):
        """Adiciona um novo agente ao roteador"""
        self.agents[name] = agent
        # Rebuildar grafo se necessário
        self._build_graph()
