import time
import os
import urllib
import json
import socket

ric_host = os.getenv('RIC_HOST', 'localhost')
my_id = socket.gethostname()
url = f"http://{ric_host}:8080"

print(f"--- APP WORKER BENCHMARK ({my_id}) ---")

while True:
    try:
        start_time = time.time() # T0

        # Ciclo de leitura e escrita
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())

        latency_ms = (time.time() - start_time) * 1000 # T1 - T0

        report = {
            "id": my_id,
            "latency_ms": latency_ms,
            "type": "benchmark"
        }

        data_bytes = json.dumps(report).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method="POST")
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=2) as r: pass

    except Exception as e:
        print(f"Erro: {e}")

    time.sleep(1) # Frequencia de teste (1Hz)