# 🤖 Jarvis AI Assistant - MVP

Assistente de IA inspirado no Jarvis do Homem de Ferro, construído com Python, LangChain e Gemini Pro.

## ⚡ Configuração Inicial

### Edite o arquivo .env

```bash
cp .env.example .env
nano .env
```

**Mínimo necessário:**

- `GEMINI_API_KEY` - Obtenha em [Google AI Studio](https://aistudio.google.com)

## ⚡ Como Executar

```bash
uv run python main.py config   # Verificar configuração
uv run python main.py chat     # Iniciar chat
```

## 🎯 Funcionalidades Atuais (MVP)

### Implementado

- **Chat CLI Interativo** - Interface limpa com Rich
- **Agente de Busca** - Perguntas gerais com Gemini Pro
- **Orquestração Multi-Agente** - Seleção e coordenação de agentes via langgraph-supervisor
- **Observabilidade** - Integração opcional com LangFuse
- **Histórico de Conversa** - Contexto persistente na sessão

### Em Desenvolvimento

- **📧 Email Agent** - Leitura e resumo de emails (Gmail)
- **🎵 Music Agent** - Controle do Spotify
- **📝 Standup Agent** - Notas baseadas em Azure DevOps/GitHub
- **📋 Planning Agent** - Assistente para sprints
- **📚 Obsidian Integration** - Acesso a notas

## 🛠 Comandos CLI

```bash
uv run python main.py chat          # Iniciar conversa
uv run python main.py config        # Verificar configuração
uv run python main.py setup         # Setup inicial
uv run python main.py version       # Informações da versão
```

### Comandos Durante o Chat

- `status` - Status do sistema
- `clear` - Limpar histórico
- `capabilities` - Ver funcionalidades
- `exit` - Sair

## 📁 Estrutura do Projeto

```text
jarvis_ai/
├── main.py                 # CLI principal
├── requirements.txt        # Dependências
├── .env.example           # Template configuração
├── config/
│   └── settings.py        # Configurações
├── core/
│   └── jarvis.py         # Classe principal
├── agents/
│   ├── base.py           # Classe base
│   └── search.py         # Agente de busca
└── tools/                # Integrações futuras
```

## ⚙️ Configuração

### Variáveis Essenciais (.env)

```bash
# Obrigatório
GEMINI_API_KEY=your_key_here

# Opcional (funcionalidades futuras)
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
GITHUB_TOKEN=your_github_token
OBSIDIAN_VAULT_PATH=/path/to/vault

# Observabilidade (opcional)
LANGFUSE_SECRET_KEY=your_langfuse_secret
LANGFUSE_PUBLIC_KEY=your_langfuse_public
```

## 🚀 Próximos Passos

### Fase 2 - Integrações (2-3 semanas)

1. **EmailAgent** - Gmail API
2. **MusicAgent** - Spotify API
3. **StandupAgent** - Azure DevOps + GitHub

### Fase 3 - Automação (1-2 semanas)

1. **PlanningAgent** - Assistente de sprints
2. **Obsidian Integration** - Notas e documentação

### Fase 4 - Voz e Local (futuro)

1. **Interface de Voz** - Speech-to-text + TTS
2. **Modelos Locais** - Ollama para privacidade
3. **UmbrelOS** - Deploy em servidor local

## 🐛 Troubleshooting

**uv não encontrado?**

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Erro de import?**

```bash
# Rode a partir da raiz do projeto
cd jarvis_ai
uv run python main.py chat
```

**API key inválida?**

```bash
uv run python main.py config  # Verificar configuração
```

**Dependências desatualizadas?**

```bash
uv sync  # Sincronizar e atualizar todas as dependências
```

**Problemas com ambiente?**

```bash
# Recriar ambiente virtual
rm -rf .venv
uv sync
```

## 🤝 Contribuindo

Este é um MVP focado em funcionamento básico. Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente seguindo o padrão dos agentes existentes
4. Teste localmente
5. Abra um PR

## 📊 Status Atual

- **Versão**: 0.1.0-MVP
- **Python**: 3.12+
- **Status**: ✅ Funcional para busca geral
- **Próximo**: Integração Gmail + Spotify

---

> "Sometimes you gotta run before you can walk." - Tony Stark

**🚀 Comece hoje mesmo seu assistente de IA!**
