import requests
import json

def test_raw_card():
    print("--- DIAGNÓSTICO V2: FORMATO DIRECTO ---")
    url = "https://defaulte4f11f0114dc4099b8cfc1fab2e970.1f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/8632fd868b1c4bf7bebb9e72fb3fbd1c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=rFJMJrHBhmec71Fd4aS0niRoUsglYEKZJ9WHDFONU_8"
    
    headers = {"Content-Type": "application/json"}

    # --- TEST 4: Raw Adaptive Card (Sin wrapper) ---
    print("\n[TEST 4] Enviando Raw Adaptive Card (Directo)...")
    payload_4 = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "🔔 TEST 4: Raw Adaptive Card",
                "size": "Large",
                "weight": "Bolder",
                "color": "Good"
            },
            {
                "type": "TextBlock",
                "text": "Si ves esto, tu Worklow espera la tarjeta 'cruda' directamente (sin envoltorio)."
            }
        ]
    }
    
    try:
        r = requests.post(url, json=payload_4, headers=headers)
        print(f"Respuesta HTTP: {r.status_code}")
        print(f"Cuerpo: {r.text}")
        
        if r.status_code == 202:
            print("\n✅ El servidor aceptó la solicitud.")
            print("⏳ Espera unos segundos y mira si aparece el mensaje 'TEST 4' en Teams.")
        else:
            print("\n❌ Error: El servidor rechazó la solicitud.")
            
    except Exception as e:
        print(f"Error técnico: {e}")

if __name__ == "__main__":
    test_raw_card()
