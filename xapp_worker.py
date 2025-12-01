import time
import os
import urllib.request
import json

# Pega o endereço do RIC (Mestre)
ric_host = os.getenv('RIC_HOST', 'localhost')
url = f"http://{ric_host}:8080"

print(f"--- xApp (WORKER) INICIADO ---")
print(f"Conectando ao Mestre RIC em: {url}")

while True:
    try:
        # 1. Pede os dados ao RIC (Simula leitura da interface E2)
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        load = data['traffic_load_mbps']
        status = data['status']

        # 2. Toma uma decisão baseada no dado recebido
        if status == "overload":
            print(f"[ALERTA] Tráfego Alto ({load} Mbps)! Executando Balanceamento de Carga...")
        else:
            print(f"[OK] Tráfego Normal ({load} Mbps). Monitorando...")

    except Exception as e:
        print(f"[Erro] Falha ao conectar no RIC: {e}")

    # Simula o tempo de processamento no Near-RT (rápido)
    time.sleep(2)