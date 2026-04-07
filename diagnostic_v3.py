import requests
import json
import time

def test_brute_force():
    print("--- DIAGNÓSTICO V3: FUERZA BRUTA ---")
    print("Microsoft ha quitado los 'Conectores', así que tenemos que acertar")
    print("con el formato exacto que espera tu 'Workflow'.")
    
    url = "https://defaulte4f11f0114dc4099b8cfc1fab2e970.1f.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/8632fd868b1c4bf7bebb9e72fb3fbd1c/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=rFJMJrHBhmec71Fd4aS0niRoUsglYEKZJ9WHDFONU_8"
    headers = {"Content-Type": "application/json"}

    # Lista de intentos con diferentes estructuras JSON
    intentos = [
        ("TEST 5 (Propiedad 'content')", {"content": "🔔 TEST 5: Funciona usando 'content'"}),
        ("TEST 6 (Propiedad 'message')", {"message": "🔔 TEST 6: Funciona usando 'message'"}),
        ("TEST 7 (Propiedad 'text')", {"text": "🔔 TEST 7: Funciona usando 'text'"}),
        ("TEST 8 (Propiedad 'body')", {"body": "🔔 TEST 8: Funciona usando 'body'"}),
        ("TEST 9 (Solo String)", "🔔 TEST 9: String plano")
    ]

    print(f"\nProbando con URL: {url[:30]}...")

    for nombre, payload in intentos:
        print(f"\nEnviando {nombre}...")
        try:
            r = requests.post(url, json=payload, headers=headers)
            print(f"Status: {r.status_code}")
            if r.status_code == 202:
                print("✅ Enviado (Posible éxito)")
            else:
                print("❌ Rechazado")
        except Exception as e:
            print(f"Error: {e}")
        
        # Esperar un poco entre intentos para no saturar
        time.sleep(1)

    print("\n--- FIN ---")
    print("Por favor, mira si ha llegado CUALQUIERA de los mensajes (Test 5, 6, 7, 8 o 9).")

if __name__ == "__main__":
    test_brute_force()
