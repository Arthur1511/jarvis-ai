# Jarvis AI Assistant

A modular AI assistant inspired by Iron Man's JARVIS, built with Python, LangChain, and Gemini Pro. Designed to help with information search, data analysis, workflow automation, and daily task management.

## 🎯 Project Vision

Create a local AI assistant that can:
- Search and analyze information intelligently
- Manage emails and calendar efficiently  
- Analyze datasets (CSV, Parquet files)
- Automate daily workflows
- Integrate with personal tools (Obsidian, Google Sheets)
- Provide voice interaction (planned feature)
- Run on local server infrastructure (UmbrelOS compatible)

## 🚀 Current Features

- **Intelligent Agent Routing**: Automatically selects the best agent for each query
- **Rich CLI Interface**: Beautiful terminal interface with conversation history
- **Search Agent**: General knowledge queries powered by Gemini Pro
- **Memory System**: Persistent conversation history and context
- **Extensible Architecture**: Easy to add new agents and capabilities
- **Observability Ready**: LangFuse integration for monitoring (optional)

## 🛠 Tech Stack

- **Core**: Python 3.8+, LangChain, Google Gemini Pro
- **CLI**: Typer, Rich Console
- **Data**: Pandas, PyArrow (for Parquet support)
- **Memory**: SQLite, Sentence Transformers
- **Monitoring**: LangFuse (optional)
- **Future**: MCP (Model Context Protocol) for external integrations

## 📋 Prerequisites

- Python 3.8 or higher
- Google AI Studio account (for Gemini Pro API key)
- 8GB RAM minimum (for local model support in future versions)

## ⚡ Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository (or create project structure)
mkdir jarvis_ai && cd jarvis_ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Initialize Project

```bash
# Run initial setup
python main.py setup

# Start interactive chat
python main.py chat
```

## 🎮 Usage

### Interactive Chat Mode

```bash
python main.py chat
```

Available commands during chat:
- `exit` / `quit` / `sair` - Exit the chat
- `help` - Show available commands and capabilities  
- `clear` - Clear conversation history

### Configuration Check

```bash
python main.py config
```

### Example Interactions

```
You: What is machine learning?
🤖 JARVIS: Machine learning is a subset of artificial intelligence (AI) that enables computers to learn and make decisions from data without being explicitly programmed for every scenario...

You: How can you help me with my daily tasks?
🤖 JARVIS: I can assist you with several daily tasks: information research, general questions, and explanations of complex topics. Soon I'll be able to help with email management, calendar organization, data analysis, and workflow automation...
```

## 🏗 Project Structure

```
jarvis_ai/
├── main.py                 # Main CLI application
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── core/
│   ├── __init__.py
│   ├── agent_router.py     # Intelligent agent routing
│   └── memory.py           # Memory system (planned)
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Base agent class
│   ├── search_agent.py     # General search and knowledge
│   ├── email_agent.py      # Email management (planned)
│   ├── calendar_agent.py   # Calendar integration (planned)
│   ├── data_agent.py       # Dataset analysis (planned)
│   └── workflow_agent.py   # Task automation (planned)
├── tools/
│   ├── __init__.py
│   ├── mcp_tools.py        # MCP integrations (planned)
│   └── data_tools.py       # Data processing tools (planned)
├── memory/
│   ├── __init__.py
│   ├── vector_store.py     # Vector embeddings (planned)
│   └── conversation_store.py # Conversation history (planned)
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini Pro API key | Yes | - |
| `LANGFUSE_SECRET_KEY` | LangFuse monitoring secret | No | - |
| `LANGFUSE_PUBLIC_KEY` | LangFuse monitoring public key | No | - |
| `LANGFUSE_HOST` | LangFuse server URL | No | `https://cloud.langfuse.com` |
| `OBSIDIAN_VAULT_PATH` | Path to Obsidian vault | No | - |

### Model Settings

- **Default Model**: `gemini-pro`
- **Temperature**: `0.1` (focused responses)
- **Max Tokens**: `4096`
- **Embedding Model**: `all-MiniLM-L6-v2` (for future vector search)

## 🚧 Planned Features (Roadmap)

### Phase 1: Core Foundation ✅
- [x] Basic CLI interface
- [x] Agent routing system
- [x] Search agent with Gemini Pro
- [x] Configuration management

### Phase 2: Data & Email Integration
- [ ] **DataAgent**: CSV/Parquet analysis with pandas + LLM
- [ ] **EmailAgent**: Gmail integration via MCP
- [ ] **CalendarAgent**: Google Calendar management via MCP
- [ ] Vector memory system with embeddings

### Phase 3: Workflow Automation  
- [ ] **WorkflowAgent**: Task automation and organization
- [ ] Obsidian integration for note-taking
- [ ] Google Sheets integration for financial tracking
- [ ] Stand-up notes generation
- [ ] Sprint planning assistance

### Phase 4: Voice & Local Models
- [ ] Speech-to-text (OpenAI Whisper)
- [ ] Text-to-speech (Coqui TTS)
- [ ] Local model support for privacy
- [ ] UmbrelOS compatibility

### Phase 5: Advanced Features
- [ ] Multi-modal capabilities (image analysis)
- [ ] Custom tool creation
- [ ] Plugin system
- [ ] Web interface
- [ ] Mobile companion app

## 🔌 Extensibility

### Adding New Agents

1. Inherit from `BaseAgent` class
2. Implement `can_handle()` and `process()` methods
3. Register agent in main application
4. Add specific tools and capabilities

Example:
```python
from agents.base_agent import BaseAgent, AgentResponse

class MyCustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomAgent", "Handles custom tasks")
    
    def can_handle(self, query: str) -> float:
        # Return confidence score 0.0-1.0
        return 0.8 if "custom" in query.lower() else 0.0
    
    async def process(self, query: str, context=None) -> AgentResponse:
        # Process the query and return response
        return AgentResponse(content="Custom response")
```

### Adding New Tools

Tools can be added to agents to extend capabilities:
- MCP connections for external APIs
- Local file processing
- Database integrations
- Custom automation scripts

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'agents'"**
   - Ensure you're running from the project root directory
   - Check that `__init__.py` files exist in all directories

2. **"Invalid API key"**
   - Verify your Gemini API key in `.env` file
   - Check that the key has proper permissions

3. **Import errors**
   - Update dependencies: `pip install -r requirements.txt --upgrade`
   - Check Python version compatibility

### Getting Help

- Check existing issues in the repository
- Review configuration with `python main.py config`
- Enable debug logging by modifying `logging.basicConfig(level=logging.DEBUG)`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to new functions
- Include docstrings for public methods
- Write tests for new agents and tools
- Update README for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Marvel's JARVIS (Just A Rather Very Intelligent System)
- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [Google Gemini](https://ai.google.dev/)
- CLI interface by [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)

## 📊 Project Status

- **Version**: 0.1.0 (Alpha)
- **Status**: Active Development
- **Python**: 3.8+ 
- **License**: MIT
- **Contributions**: Welcome

---

**"Sometimes you gotta run before you can walk."** - Tony Stark

*Start building your own AI assistant today!*
