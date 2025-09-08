#!/bin/bash

# Setup script para Jarvis AI Assistant
echo "🤖 Configurando Jarvis AI Assistant..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p credentials logs data

# Copiar arquivo de configuração
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Edite-o com suas API keys."
else
    echo "ℹ️ Arquivo .env já existe ou .env.example não encontrado."
fi

echo ""
echo "🎉 Setup concluído!"
echo ""
echo "Próximos passos:"
echo "1. Configure suas API keys no arquivo .env"
echo "2. Teste a configuração: uv run python main.py config"
echo "3. Inicie o chat: uv run python main.py chat"
echo ""
echo "Comandos uv úteis:"
echo "- uv add <package>     # Adicionar dependência"
echo "- uv run <command>     # Executar comando no ambiente"
echo "- uv sync              # Sincronizar dependências"
echo ""
echo "Para ajuda: uv run python main.py --help"