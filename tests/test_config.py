from pathlib import Path
from importlib import import_module, reload
import pytest
from pydantic import ValidationError

# Adiciona o diretório raiz ao path para encontrar os módulos do projeto
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def settings_module():
    """Carrega e retorna o módulo de configurações para cada teste."""
    # Importa o módulo dinamicamente para garantir o isolamento
    return import_module("config.settings")

@pytest.fixture(autouse=True)
def isolated_settings(monkeypatch, settings_module):
    """Garante que cada teste rode com um ambiente e configurações limpas."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_TEMPERATURE", raising=False)
    # Recarrega o módulo para limpar o estado da instância singleton antes de cada teste
    reload(settings_module)

@pytest.fixture
def temp_env_file(tmp_path):
    """Cria um arquivo .env temporário para testes."""
    env_content = "GEMINI_API_KEY=test_api_key_from_file\nMODEL_TEMPERATURE=0.8"
    env_path = tmp_path / ".env"
    env_path.write_text(env_content)
    return env_path

def test_settings_load_from_file(temp_env_file, monkeypatch, settings_module):
    """
    Testa se as configurações são carregadas corretamente de um arquivo .env.
    """
    monkeypatch.chdir(temp_env_file.parent)
    reload(settings_module)  # Recarrega para forçar a leitura do novo .env
    settings_instance = settings_module.Settings()
    assert settings_instance.gemini_api_key == "test_api_key_from_file"
    assert settings_instance.ai_model_config.temperature == 0.8

def test_settings_load_from_env_vars(monkeypatch, settings_module):
    """
    Testa se as configurações são carregadas corretamente das variáveis de ambiente.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_from_env")
    monkeypatch.setenv("MODEL_TEMPERATURE", "0.95")
    reload(settings_module)  # Recarrega para ler as novas variáveis de ambiente
    settings_instance = settings_module.Settings()
    assert settings_instance.gemini_api_key == "test_api_key_from_env"
    assert settings_instance.ai_model_config.temperature == 0.95

def test_settings_missing_required_field(settings_module, monkeypatch, tmp_path):
    """
    Testa se o Pydantic levanta um erro de validação se um campo obrigatório não for fornecido.
    """
    # Muda para um diretório vazio para garantir que nenhum .env seja encontrado
    monkeypatch.chdir(tmp_path)
    # A fixture isolated_settings já limpou a variável de ambiente.
    with pytest.raises(ValidationError):
        reload(settings_module)
        settings_module.Settings()