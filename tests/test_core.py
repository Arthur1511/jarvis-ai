
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Adiciona o diretório raiz ao path para encontrar os módulos do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importa a classe a ser testada
from core.jarvis import JarvisAI

# Mock para as dependências externas
@pytest.fixture
def mock_dependencies():
    """Mock de todas as dependências externas para isolar a classe JarvisAI."""
    with patch('core.jarvis.create_search_agent') as mock_create_agent:
        with patch('core.jarvis.get_search_agent_info') as mock_get_info:
            with patch('core.jarvis.ChatGoogleGenerativeAI') as mock_llm:
                with patch('core.jarvis.create_supervisor') as mock_create_supervisor:
                    with patch('core.jarvis.Langfuse') as mock_langfuse:
                        # Configura o retorno dos mocks
                        mock_agent = MagicMock()
                        mock_tools = [MagicMock()]
                        mock_create_agent.return_value = (mock_agent, mock_tools)
                        
                        mock_get_info.return_value = {
                            'name': 'search',
                            'description': 'A mock search agent.'
                        }
                        
                        mock_graph = MagicMock()
                        mock_create_supervisor.return_value.compile.return_value = mock_graph

                        yield {
                            'mock_create_agent': mock_create_agent,
                            'mock_get_info': mock_get_info,
                            'mock_llm': mock_llm,
                            'mock_create_supervisor': mock_create_supervisor,
                            'mock_graph': mock_graph,
                            'mock_langfuse': mock_langfuse
                        }

def test_jarvisai_initialization(mock_dependencies):
    """
    Testa se a classe JarvisAI é inicializada corretamente.
    """
    # Instancia a classe
    jarvis = JarvisAI()

    # Verifica se os componentes principais foram chamados
    mock_dependencies['mock_create_agent'].assert_called_once()
    mock_dependencies['mock_get_info'].assert_called_once()
    mock_dependencies['mock_llm'].assert_called_once()
    mock_dependencies['mock_create_supervisor'].assert_called_once()

    # Verifica se os atributos da classe foram definidos corretamente
    assert len(jarvis.agents) == 1
    assert len(jarvis.agents_metadata) == 1
    assert jarvis.agents_metadata[0]['name'] == 'search'
    assert jarvis.graph is not None
    assert jarvis.logger is not None

