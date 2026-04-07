"""
Módulo para enviar notificaciones de avisos médicos a través de Telegram.
"""
import requests
from typing import Optional, Dict, Any


class TelegramNotifier:
    """
    Clase para enviar notificaciones de avisos médicos a través de Telegram Bot API.
    """
    
    def __init__(self, bot_token: str):
        """
        Inicializa el notificador de Telegram.
        
        Args:
            bot_token: Token del bot de Telegram obtenido de @BotFather
        """
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_aviso_notification(self, chat_id: str, aviso_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Envía una notificación formateada del aviso al médico.
        
        Args:
            chat_id: ID del chat de Telegram del médico
            aviso_data: Diccionario con los datos del aviso
            
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if not chat_id:
            return False, "Chat ID vacío"
        
        message = self._format_aviso_message(aviso_data)
        return self._send_message(chat_id, message)
    
    def _format_aviso_message(self, data: Dict[str, Any]) -> str:
        """
        Formatea el mensaje con los datos del aviso usando emojis para mejor legibilidad.
        
        Args:
            data: Diccionario con los datos del aviso
            
        Returns:
            str: Mensaje formateado en Markdown
        """
        # Helper para obtener valores con fallback
        def get(key: str, default: str = "N/A") -> str:
            value = data.get(key, default)
            return str(value) if value else default
        
        # Determinar emoji de estado
        estado = get("Estado", "Abierto")
        estado_emoji = "🟢" if estado.lower() == "cerrado" else "🔴"
        
        # Construir mensaje
        message = f"""
🚨 *NUEVO AVISO MÉDICO* {estado_emoji}

📅 *Fecha:* {get('Fecha')}
⏰ *Hora Aviso:* {get('Hora Aviso')}
🏨 *Hotel:* {get('Hotel')}
🚪 *Habitación:* {get('Habitacion')}

👤 *PACIENTE*
━━━━━━━━━━━━━━
• Nombre: {get('Paciente')}
• Edad: {get('Edad')} años
• Nacionalidad: {get('Nacionalidad')}
• NHC: {get('Historia Medica')}

🩺 *DATOS MÉDICOS*
━━━━━━━━━━━━━━
• Motivo: {get('Motivo Urgencia')}
• Diagnóstico: {get('Diagnostico', '-')}

💳 *PAGADOR*
━━━━━━━━━━━━━━
• Tipo: {get('Pagador')}
• Seguro: {get('Seguro', '-')}
• TTOO: {get('Touroperador', '-')}

📍 *Distancia:* {get('Distancia', 'N/A')} km del hospital
        """.strip()
        
        # Añadir información de traslado si aplica
        traslado = get('Traslado', 'No')
        if traslado.lower() in ('si', 'sí', 'yes', 'true'):
            message += f"\n\n🚑 *TRASLADO*\n"
            message += f"• Tipo: {get('Tipo Traslado', '-')}\n"
            hora_amb = get('Hora Ambulancia', '-')
            if hora_amb != '-':
                message += f"• Hora Ambulancia: {hora_amb}\n"
        
        # Añadir información de ingreso si aplica
        ingreso = get('Ingreso', 'No ingresa')
        if ingreso.lower() not in ('no ingresa', 'no', '-'):
            message += f"\n\n🏥 *INGRESO*\n"
            message += f"• Tipo: {ingreso}\n"
            medico_ingreso = get('Medico Ingreso', '-')
            if medico_ingreso != '-':
                message += f"• Médico: {medico_ingreso}\n"
        
        # Añadir observaciones si existen
        observaciones = get('Observaciones', '')
        if observaciones and observaciones != 'N/A':
            message += f"\n\n📝 *Observaciones:*\n{observaciones}"
        
        return message
    
    def _send_message(self, chat_id: str, text: str) -> tuple[bool, str]:
        """
        Envía un mensaje a través de la API de Telegram.
        
        Args:
            chat_id: ID del chat de destino
            text: Texto del mensaje
            
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return True, "Mensaje enviado correctamente"
            else:
                error_msg = response.json().get('description', 'Error desconocido')
                return False, f"Error de Telegram: {error_msg}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout: No se pudo conectar con Telegram"
        except requests.exceptions.ConnectionError:
            return False, "Error de conexión: Verifica tu internet"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Prueba la conexión con el bot de Telegram.
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                bot_info = response.json().get('result', {})
                bot_name = bot_info.get('username', 'Unknown')
                return True, f"Conectado correctamente al bot @{bot_name}"
            else:
                return False, "Token inválido o bot no encontrado"
                
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"


def get_chat_id_instructions() -> str:
    """
    Retorna instrucciones para obtener el chat_id de un usuario.
    
    Returns:
        str: Instrucciones formateadas
    """
    return """
Para obtener tu Chat ID de Telegram:

1. Inicia conversación con tu bot (búscalo por su nombre de usuario)
2. Envía cualquier mensaje al bot (ej: /start o "Hola")
3. Visita esta URL en tu navegador (reemplaza TU_TOKEN):
   https://api.telegram.org/botTU_TOKEN/getUpdates
   
4. Busca en la respuesta JSON el campo "chat":{"id": XXXXXXX}
5. Ese número es tu Chat ID (puede ser positivo o negativo)
6. Cópialo y pégalo en el campo correspondiente

Nota: El Chat ID es diferente para cada usuario.
    """.strip()
