"""
Módulo de configuración para cargar variables de entorno.
"""
import os
from pathlib import Path


def load_telegram_token() -> str:
    """
    Carga el token del bot de Telegram desde el archivo .env
    
    Returns:
        str: Token del bot o cadena vacía si no se encuentra
    """
    env_file = Path(__file__).parent.parent.parent / ".env"
    
    if env_file.exists():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                    # Remove quotes if present
                    if token.startswith('"') and token.endswith('"'):
                        token = token[1:-1]
                    elif token.startswith("'") and token.endswith("'"):
                        token = token[1:-1]
                    return token
        except Exception as e:
            print(f"Error leyendo .env: {e}")
    
    return ""


def is_telegram_configured() -> bool:
    """
    Verifica si el bot de Telegram está configurado
    
    Returns:
        bool: True si hay un token configurado
    """
    token = load_telegram_token()
    return bool(token and token != "TU_TOKEN_AQUI")

