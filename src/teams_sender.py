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
            nhc = aviso_data.get("Historia Medica", "-")
            motivo = aviso_data.get("Motivo Urgencia", "No especificado")
            medico = aviso_data.get("Medico", "Sin asignar")
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
            
            # Formatear fecha localmente para el mensaje
            fecha_display = fecha
            if "-" in fecha and len(fecha) == 10:
                y, m, d = fecha.split("-")
                fecha_display = f"{d}/{m}/{y}"

            # Construir mensaje de texto simple pero completo
            msg_lines = [
                "🚨 **NUEVO AVISO MÉDICO**",
                f"**Paciente:** {paciente} (NHC: {nhc})",
                f"**Hotel:** {hotel} (Hab: {habitacion})",
                f"**Motivo:** {motivo}",
                f"**Médico:** {medico}",
                f"**Fecha/Hora:** {fecha_display} - {hora}",
                "\n_Enviado desde el Gestor de Avisos Vithas_"
            ]
            # Envolver el mensaje Markdown dentro de una Adaptive Card básica
            # Esto es necesario porque la plantilla de Power Automate seleccionada
            # exige un array 'attachments' dentro del body.
            card_payload = {
                "type": "AdaptiveCard",
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "\n\n".join(msg_lines),
                        "wrap": True
                    }
                ]
            }

            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": card_payload
                    }
                ]
            }

            headers = {"Content-Type": "application/json"}
            
            response = requests.post(self.webhook_url, json=payload, headers=headers)
            
            if response.status_code != 202:
                print(f"Error al enviar a Teams: {response.status_code} - {response.text}")
            else:
                print("Notificación enviada a Teams correctamente.")

        except Exception as e:
            print(f"Excepción enviando a Teams: {e}")
