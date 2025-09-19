# 🧑‍💻 Copilot Instructions for Jarvis AI

## Arquitetura Geral
- Multi-agente: Cada agente em `agents/` resolve um domínio (busca, email, música, etc.)
- Orquestração: Seleção e coordenação de agentes via langgraph-supervisor (não há router.py)
- Entrada principal: `main.py` (CLI), delega para `core/jarvis.py`
- Contexto: Histórico e contexto de conversa gerenciados em `core/jarvis.py`
- Observabilidade: Integração opcional com LangFuse

## Fluxos de Desenvolvimento
- Ambiente: Use `uv` para instalar e sincronizar dependências (`uv add`, `uv sync`)
- Configuração: Variáveis em `.env` (veja `.env.example`)
- Testes: O projeto seguirá o padrão TDD (Test Driven Development). Priorize escrever testes antes da implementação. Use `pytest` para rodar os testes.
- Debug: Use comandos CLI (`status`, `config`, `clear`) e logs

## Padrões Específicos
- Agentes: Herdam de uma base comum, implementam `can_handle` (score) e `process` (async, retorna `AgentResponse`)
- Orquestração: Supervisor seleciona agentes com base no score de `can_handle`
- LangChain: Agentes usam wrappers LLM (ex: `ChatGoogleGenerativeAI`)
- Ferramentas: Agentes podem expor tools do LangChain/LlamaIndex para uso reativo
- Config centralizada: `config/settings.py` + `.env`
- Extensibilidade: Novos agentes seguem padrão de `agents/search.py` e são registrados no supervisor

## Integrações
- Gemini Pro: LLM principal via LangChain
- LangFuse: Observabilidade se configurado
- Futuras: Gmail, Spotify, GitHub, Obsidian (stubados)

## Exemplos
- Para adicionar agente: crie `agents/meu_agente.py`, implemente métodos, registre no supervisor
- Para adicionar tool: use `Tool` do LangChain ou importe de LlamaIndex/LangGraph
	- Exemplo concreto: `tools/date_tools.py` implementa uma tool customizada usando o decorator `@tool` do LangChain para manipulação de data/hora, pronta para ser registrada em agentes.

- `main.py` — CLI
- `core/jarvis.py` — lógica principal
- `agents/` — agentes individuais
- `config/settings.py` — configuração
- `tools/` — código de tools customizadas utilizadas por agentes (ex: integrações, utilitários)
- `.env.example` — template de variáveis
- `.github/copilot-instructions.md` — instruções para o Copilot
- `GEMINI.md` - instruções para o gemini-cli
