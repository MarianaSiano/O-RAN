import time
import os
import urllib.request
import json

ric_host = os.getenv('RIC_HOST', 'localhost')
url = f"http://{ric_host}:8080"

print(f"--- rApp ENERGY SAVER (Non-RT) INICIADO ---")
print(f"--- Conectando via Interface A1 em {url} ---")
state = False

while True:
    try:
        state = not state # Alterna estado (True/False)

        # Mensagem A1 via JSON
        policy = {
            "type": "A1_POLICY",
            "scope": "UE_GROUP_1",
            "value": state
        }

        data_bytes = json.dumps(policy).encode('utf-8')

        # Metodo PUT caracteristico da interface A1
        req = urllib.request.Request(url, data=data_bytes, method="PUT")
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as r:
            print(f"[rApp] Enviado A1 Policy: Economia={state}")

    except Exception as e:
        print(f"Erro ao contatar RIC: {e}")

    time.sleep(15)