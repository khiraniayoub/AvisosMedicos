import requests
import json

def test_minimal():
    print("--- DIAGNÓSTICO V4: VERSIÓN MÍNIMA ---")
    
    # URL CANAL NUEVO (PROPORCIONADA POR TI)
    url = "https://defaulte4f11f0114dc4099b8cfc1fab2e970.1f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/57226b97d6cf4688a86cb0f23854be83/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=Ju_DsWZjPtTQIziNymZctRsL6oU6tlTh4q3Q_YYzs8Y"
    
    headers = {"Content-Type": "application/json"}

    # Payload extremadamente básico (Adaptive Card v1.0)
    # A veces v1.4 actua raro en canales antiguos o flow restringidos
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🔔 AVISO DE PRUEBA (V1.0)"
                        }
                    ]
                }
            }
        ]
    }

    print("Enviando tarjeta V1.0 mínima...")
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status: {r.status_code}")
        if r.status_code == 202:
            print("✅ Enviado.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_minimal()
