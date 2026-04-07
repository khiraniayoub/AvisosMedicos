import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TeamsTester")

def test_payloads():
    print("--- DIAGNÓSTICO DE TEAMS ---")
    print("Este script probará 3 formatos diferentes para ver cuál acepta tu canal.")
    
    url = input("Por favor, pega tu URL de Webhook aquí: ").strip()
    if not url:
        print("URL vacía. Abortando.")
        return

    headers = {"Content-Type": "application/json"}

    # --- TEST 1: Texto Simple ---
    print("\n[TEST 1] Enviando Texto Simple...")
    payload_1 = {
        "text": "🔔 TEST 1: Texto Simple (Si ves esto, el formato simple funciona)"
    }
    try:
        r = requests.post(url, json=payload_1, headers=headers)
        print(f"Respuesta: {r.status_code}")
        print(f"Contenido: {r.text}")
    except Exception as e:
        print(f"Error HTTP: {e}")

    # --- TEST 2: Adaptive Card (Moderno) ---
    print("\n[TEST 2] Enviando Adaptive Card (Moderno)...")
    payload_2 = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🔔 TEST 2: Adaptive Card",
                            "size": "Large",
                            "weight": "Bolder"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Si ves esto, el formato Moderno funciona."
                        }
                    ]
                }
            }
        ]
    }
    try:
        r = requests.post(url, json=payload_2, headers=headers)
        print(f"Respuesta: {r.status_code}")
    except Exception as e:
        print(f"Error HTTP: {e}")

    # --- TEST 3: MessageCard (Legacy) ---
    print("\n[TEST 3] Enviando MessageCard (Legacy)...")
    payload_3 = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.teams.card.o365connector",
                "content": {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "summary": "Test Legacy",
                    "themeColor": "0076D7",
                    "title": "🔔 TEST 3: MessageCard",
                    "text": "Si ves esto, el formato Legacy (antiguo) funciona."
                }
            }
        ]
    }
    try:
        r = requests.post(url, json=payload_3, headers=headers)
        print(f"Respuesta: {r.status_code}")
    except Exception as e:
        print(f"Error HTTP: {e}")

    print("\n--- FIN DEL TEST ---")
    print("Por favor, mira tu Teams y dime qué mensajes (1, 2 o 3) han llegado.")

if __name__ == "__main__":
    test_payloads()
