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