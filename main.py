"""
Interface CLI principal do Jarvis AI Assistant
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env no início da aplicação
load_dotenv()

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from core.jarvis import JarvisAI

app = typer.Typer(
    name="jarvis",
    help="🤖 Jarvis AI Assistant - Seu assistente pessoal inspirado no Homem de Ferro",
    rich_markup_mode="rich",
)

console = Console()


def display_banner():
    """Exibe banner de inicialização"""
    banner = Text()
    banner.append("🤖 ", style="bold blue")
    banner.append("J.A.R.V.I.S", style="bold cyan")
    banner.append(" - Just A Rather Very Intelligent System", style="dim")

    console.print(
        Panel(
            banner,
            title="[bold green]Jarvis AI Assistant[/bold green]",
            subtitle="[dim]Versão 0.1.0 - MVP[/dim]",
            border_style="blue",
        )
    )


def display_help():
    """Exibe ajuda dos comandos disponíveis"""
    help_content = """
**Comandos disponíveis durante a conversa:**
• `exit`, `quit`, `sair` - Sair do chat
• `help`, `ajuda` - Mostrar esta ajuda
• `status` - Verificar status do sistema
• `clear` - Limpar histórico da conversa
• `capabilities` - Mostrar capacidades atuais

**Exemplos de uso:**
• "Explique o que é machine learning"
• "Como funciona o protocolo HTTP?"
• "Me conte sobre a história do Brasil"
• "Defina inteligência artificial"

*Digite sua pergunta naturalmente e pressione Enter.*
    """
    console.print(Markdown(help_content))


@app.command()
def chat():
    """🎯 Inicia conversa interativa com o Jarvis"""
    asyncio.run(_chat_async())


async def _chat_async():
    """Função async para chat interativo"""
    display_banner()

    # Verificar configuração básica
    if not settings.gemini_api_key:
        console.print("[red]❌ GEMINI_API_KEY não configurado![/red]")
        console.print("Configure sua API key no arquivo .env")
        return

    # Inicializar Jarvis
    console.print("[dim]Inicializando sistemas...[/dim]")
    jarvis = JarvisAI()

    # Verificar saúde do sistema
    health = await jarvis.health_check()
    if health["status"] != "healthy":
        console.print(
            f"[red]❌ Sistema não está funcionando: {health.get('error', 'Erro desconhecido')}[/red]"
        )
        return

    console.print("[green]✅ Jarvis online e pronto![/green]")
    console.print(
        "[dim]Digite 'help' para ver comandos disponíveis ou 'exit' para sair" 
    )
    console.print()

    # Loop principal de conversa
    while True:
        try:
            # Prompt do usuário
            user_input = Prompt.ask("[bold blue]Você[/bold blue]", console=console).strip()

            # Comandos especiais
            if user_input.lower() in ["exit", "quit", "sair"]:
                console.print("[dim]Encerrando conversa...[/dim]")
                await jarvis.shutdown()
                break

            elif user_input.lower() in ["help", "ajuda"]:
                display_help()
                continue

            elif user_input.lower() == "status":
                status = jarvis.get_system_status()
                display_status(status)
                continue

            elif user_input.lower() == "clear":
                jarvis.clear_history()
                console.clear()
                display_banner()
                console.print("[green]✅ Histórico limpo![/green]")
                continue

            elif user_input.lower() in ["capabilities", "capacidades"]:
                capabilities = jarvis.get_capabilities()
                console.print(Markdown(capabilities))
                continue

            elif not user_input:
                continue

            # Processar query
            with console.status("[dim]Processando...[/dim]", spinner="dots"):
                response = await jarvis.process_query(user_input)

            # Exibir resposta
            jarvis_text = Text()
            jarvis_text.append("🤖 JARVIS", style="bold cyan")

            console.print(jarvis_text, end=": ")
            console.print(response.get("content", "Não foi possível processar a resposta."))

            # Mostrar metadata em modo debug (se confiança baixa)
            if response.get("confidence", 1.0) < 0.5:
                console.print(f"[dim]Confiança: {response.get('confidence'):.2f}[/dim]")

            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Conversa interrompida pelo usuário[/dim]")
            await jarvis.shutdown()
            break
        except Exception as e:
            console.print(f"[red]❌ Erro inesperado: {e}[/red]")


def display_status(status: dict):
    """Exibe status do sistema em formato tabular"""
    table = Table(title="Status do Sistema Jarvis")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Detalhes", style="dim")

    # Status geral
    table.add_row("🤖 Sistema", "[green]✅ Online[/green]", f"Sessão: {status['session_id']}")

    table.add_row(
        "💬 Conversa",
        f"[blue]{status['conversation_length']} mensagens[/blue]",
        status.get("last_interaction", "Nenhuma")[:19]
        if status.get("last_interaction")
        else "N/A",
    )

    # Agentes disponíveis
    agents = ", ".join(status["available_agents"])
    table.add_row(
        "🧠 Agentes", f"[green]{len(status['available_agents'])} ativos[/green]", agents
    )

    # Integrações
    integrations = status["integrations"]
    for name, enabled in integrations.items():
        icon = "✅" if enabled else "⏸️"
        status_text = "[green]Ativo[/green]" if enabled else "[yellow]Inativo[/yellow]"
        table.add_row(f"🔌 {name.title()}", f"{icon} {status_text}", "")

    console.print(table)


@app.command()
def config():
    """⚙️ Verifica configuração do sistema"""
    console.print(Panel("[bold]Verificação de Configuração[/bold]", border_style="blue"))

    # Verificar variáveis essenciais
    config_table = Table()
    config_table.add_column("Configuração", style="cyan")
    config_table.add_column("Status", justify="center")
    config_table.add_column("Valor/Nota", style="dim")

    # Gemini API
    gemini_status = "✅ Configurado" if settings.gemini_api_key else "❌ Não configurado"
    gemini_color = "green" if settings.gemini_api_key else "red"
    config_table.add_row(
        "Gemini API Key",
        f"[{gemini_color}]{gemini_status}[/{gemini_color}]",
        "***" + settings.gemini_api_key[-4:] if settings.gemini_api_key else "Necessário no .env",
    )

    # LangFuse
    langfuse_status = "✅ Ativo" if settings.observability.is_enabled else "⏸️ Inativo"
    langfuse_color = "green" if settings.observability.is_enabled else "yellow"
    config_table.add_row(
        "LangFuse (Observabilidade)",
        f"[{langfuse_color}]{langfuse_status}[/{langfuse_color}]",
        "Opcional para monitoring",
    )

    # Outras integrações
    integrations = {
        "Tavily": settings.tavily.is_enabled,
        "Spotify": settings.spotify.is_enabled,
        "Gmail": settings.gmail.is_enabled,
        "GitHub": settings.github.is_enabled,
        "Obsidian": settings.obsidian.is_enabled,
    }

    for name, enabled in integrations.items():
        status = "✅ Configurado" if enabled else "⏸️ Não configurado"
        color = "green" if enabled else "yellow"
        config_table.add_row(
            name,
            f"[{color}]{status}[/{color}]",
            "Funcionalidade futura" if not enabled else "Pronto",
        )

    console.print(config_table)

    # Dicas de configuração
    if not settings.gemini_api_key:
        console.print(
            "\n[red]⚠️ Configure GEMINI_API_KEY no arquivo .env para usar o Jarvis" 
        )

    console.print("\n[dim]Arquivo de configuração: .env[/dim]")
    console.print(f"[dim]Banco de dados: {settings.database_url}[/dim]")


@app.command()
def setup():
    """🔧 Setup inicial do projeto"""
    console.print("[bold blue]Configuração inicial do Jarvis AI[/bold blue]")

    # Criar diretórios necessários
    directories = ["credentials", "logs", "data"]
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        console.print(f"✅ Diretório {dir_name}/ criado")

    # Verificar .env
    env_file = Path(".env")
    if not env_file.exists():
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil

            shutil.copy(env_example, env_file)
            console.print("✅ Arquivo .env criado a partir do .env.example")
        else:
            console.print("❌ .env.example não encontrado")
    else:
        console.print("ℹ️ Arquivo .env já existe")

    # Próximos passos
    next_steps = """
**Próximos passos:**

1. **Configure sua API key do Gemini:**
   ```
   # Edite o arquivo .env
   GEMINI_API_KEY=sua_api_key_aqui
   ```

2. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

3. **Teste o sistema:**
   ```
   python main.py config
   python main.py chat
   ```

4. **Para integrações futuras, configure:**
   - Spotify API (Client ID + Secret)
   - Gmail API (Credentials JSON)
   - GitHub Token
   - Path do Obsidian Vault
    """

    console.print(Markdown(next_steps))


@app.command()
def version():
    """📋 Mostra informações da versão"""
    version_info = """
**Jarvis AI Assistant v0.1.0**

- 🤖 Agente de busca com Gemini Pro
- 🔀 Roteamento inteligente com LangGraph
- 📊 Observabilidade com LangFuse
- 💬 Interface CLI interativa

**Em desenvolvimento:**
- 📧 Integração Gmail
- 🎵 Controle Spotify
- 📝 Notas de Standup
- 📋 Planning de Sprints
- 🎙️ Interface de voz
    """
    console.print(Markdown(version_info))


if __name__ == "__main__":
    app()