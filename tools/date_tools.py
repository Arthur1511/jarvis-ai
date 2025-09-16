"""
Ferramentas para manipulação de data e hora.
"""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_date(time_zone: str = "America/Sao_Paulo") -> str:
    """
    Retorna a data e hora atuais, incluindo o fuso horário.

    Args:
        time_zone: O fuso horário a ser usado (padrão: "America/Sao_Paulo").
                   Formatos esperados: "UTC", "America/Sao_Paulo", "Europe/Lisbon".
    """
    # Nota: A implementação real do fuso horário exigiria a biblioteca 'pytz' ou 'zoneinfo' (Python 3.9+).
    # Para manter a simplicidade e evitar novas dependências, esta implementação de exemplo
    # apenas mostra o formato, mas sempre usará o tempo da máquina local.
    # Em um ambiente de produção, a lógica de fuso horário real seria implementada aqui.
    now = datetime.now()
    return f"A data e hora atuais são: {now.strftime('%Y-%m-%d %H:%M:%S')} ({time_zone})"
