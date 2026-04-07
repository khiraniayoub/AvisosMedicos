import requests
import json
import threading

class TeamsSender:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_notification(self, aviso_data):
        """
        Envía una notificación a Teams en un hilo separado para no bloquear la UI.
        """
        thread = threading.Thread(target=self._send_payload, args=(aviso_data,))
        thread.start()

    def _send_payload(self, aviso_data):
        try:
            # Construir la tarjeta adaptativa (Adaptive Card) o mensaje simple
            # Usaremos un mensaje con formato Markdown simple pero efectivo
            
            # Extraer datos con valores por defecto para evitar errores
            paciente = aviso_data.get("Paciente", "Desconocido")
            hotel = aviso_data.get("Hotel", "Desconocido")
            habitacion = aviso_data.get("Habitacion", "-")
            motivo = aviso_data.get("Motivo Urgencia", "No especificado")
            medico = aviso_data.get("Doctor", "Sin asignar")
            fecha = aviso_data.get("Fecha", "")
            hora = aviso_data.get("Hora Solicitud", "")

            # Color de la tarjeta según prioridad/estado podría ser un extra, 
            # pero por ahora usaremos MessageCard estandar.
            
            # Para flujos de Power Automate (Workflows app), a veces se requiere enviar la tarjeta directamente
            # o con una estructura específica. Vamos a probar enviando la Adaptive Card pura.
            card_payload = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "🚨 Nuevo Aviso Creado",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": "Attention"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Paciente:", "value": paciente},
                            {"title": "Hotel:", "value": f"{hotel} (Hab: {habitacion})"},
                            {"title": "Motivo:", "value": motivo},
                            {"title": "Médico:", "value": medico},
                            {"title": "Fecha/Hora:", "value": f"{fecha} - {hora}"}
                        ]
                    },
                    {
                         "type": "TextBlock",
                         "text": "Pulse para ver detalles",
                         "isSubtle": True,
                         "wrap": True,
                         "size": "Small"
                    }
                ],
                "actions": []
            }
            
            # Versión "Legacy Connector" usa wrap: {"type":"message", "attachments":[...]}
            # Versión "Workflow" suele aceptar la tarjeta directa o dentro de "attachments" pero sin type message.
            # Al ser un error de visualización, probaremos un formato híbrido que suele funcionar en ambos:
            # Enviar la tarjeta como 'attachments' pero con el formato Microsoft moderno.
            
            # INTENTO 2: Estructura compatible con Power Automate "Post card in chat or channel"
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card_payload
                    }
                ]
            }

            # CHANGE: Some Power Automate flows FAIL if you send the legacy wrapper.
            # Let's try sending the CARD CONTENT ONLY as the root, which is common for "Wait for a webhook" triggers actions.
            # However, standard "Incoming Webhook" requires the legacy wrapper.
            # Given the URL is 'powerplatform', it is likely a Workflow. 
            
            # Strategy: Send the legacy format first (as implemented). 
            # If that failed to show up (but got 202), it implies the Flow swallowed it.
            # Let's try simplifying to a simple TEXT message to verify connectivity first.
            
            payload_simple = {
                "text": f"🚨 **Nuevo Aviso**\n\n**Paciente:** {paciente}\n**Hotel:** {hotel}\n**Motivo:** {motivo}"
            }

            headers = {"Content-Type": "application/json"}
            
            # Send SIMPLE text first to debug
            response = requests.post(self.webhook_url, json=payload_simple, headers=headers)
            
            if response.status_code != 202:
                print(f"Error al enviar a Teams: {response.status_code} - {response.text}")
            else:
                print("Notificación enviada a Teams correctamente.")

        except Exception as e:
            print(f"Excepción enviando a Teams: {e}")
