"""
gerar_dataset_xapp.py - Dataset de ataques focados no xApp (O-RAN)
Gera 1200 timestamps (20 min) com 7 classes de ataque ao xApp

Classes:
    0 = NORMAL
    1 = OVERLOAD_FABRICATE - load falso >200 força HANDOVER
    2 = LATENCY_POISON - latencia >800ms nos workers
    3 = HANDOVER_STORM - 50 celulas com decisao HANDOVER
    4 = ADVERSARIAL_NOISE - ruido adversarial contra ML (IDS Evasion)
    5 = GRADIENT_MASKING - distribuicao normal falsa (IDS Evasion)
    6 = TIME_DRIFTING - alteracao gradual de metricas (IDS Evasion)
"""

import csv
import random
import math
from datetime import datetime, timedelta

random.seed(42)

TIMESTEPS = 1200
BASE = datetime(2026, 5, 19, 14, 0, 0)

# Distribuicoes de referencia (comportamento normal)
REF_LOAD_MEAN = 100
REF_LOAD_STD = 25
REF_LAT_MEAN = 12
REF_LAT_STD = 3
REF_USERS_MEAN = 32
REF_USERS_STD = 10

def gerar_registro(t, attack_id, drift=0.0):
    """Gera um registro baseado no tipo de ataque"""
    ts = (BASE + timedelta(seconds=t)).isoformat()
    
    # Valores base (normal)
    cell_load_mbps = round(random.gauss(REF_LOAD_MEAN, REF_LOAD_STD), 1)
    cell_capacity_mbps = 100
    connected_users = int(random.gauss(REF_USERS_MEAN, REF_USERS_STD))
    a1_policy_active = False
    
    w0 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
    w1 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
    w2 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
    w3 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
    
    temp_bbu = round(random.uniform(40, 44), 1)
    attack_name = "NORMAL"
    
    # Lista de IDs de workers (para flood)
    worker_ids_pool = [f"flood-worker-{i}" for i in range(1, 501)]
    
    # === MODIFICACOES POR TIPO DE ATAQUE ===
    
    if attack_id == 1:  # OVERLOAD_FABRICATE
        attack_name = "OVERLOAD_FABRICATE"
        cell_load_mbps = random.randint(210, 280)
        connected_users = random.randint(8, 20)
        # Latencia normal para nao levantar suspeita
        w0 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
    
    elif attack_id == 2:  # LATENCY_POISON
        attack_name = "LATENCY_POISON"
        cell_load_mbps = round(random.gauss(REF_LOAD_MEAN, REF_LOAD_STD), 1)
        # 30% worker0 com latencia altissima
        if random.random() < 0.3:
            w0 = round(random.uniform(800, 3000), 2)
        else:
            w0 = round(random.gauss(REF_LAT_MEAN, REF_LAT_STD), 2)
        # 15% worker1 tambem
        if random.random() < 0.15:
            w1 = round(random.uniform(500, 2000), 2)
    
    elif attack_id == 3:  # HANDOVER_STORM
        attack_name = "HANDOVER_STORM"
        cell_load_mbps = random.randint(180, 300)
        connected_users = random.randint(5, 15)
    
    elif attack_id == 4:  # ADVERSARIAL_NOISE
        attack_name = "ADVERSARIAL_NOISE"
        epsilon = 0.15 + 0.05 * math.sin(t * 0.1)
        cell_load_mbps = round(REF_LOAD_MEAN + epsilon * REF_LOAD_STD * 2.5, 1)
        connected_users = max(5, int(REF_USERS_MEAN - epsilon * REF_USERS_STD * 3))
        w0 = round(REF_LAT_MEAN + epsilon * 4 + random.gauss(0, 0.5), 2)
        temp_bbu = round(42 + epsilon * 10 + random.gauss(0, 0.3), 1)
        cell_capacity_mbps = 100
    
    elif attack_id == 5:  # GRADIENT_MASKING
        attack_name = "GRADIENT_MASKING"
        if random.random() < 0.7:
            cell_load_mbps = round(random.gauss(REF_LOAD_MEAN, REF_LOAD_STD), 1)
            connected_users = int(random.gauss(REF_USERS_MEAN, REF_USERS_STD))
        else:
            cell_load_mbps = round(REF_LOAD_MEAN + random.uniform(1.5, 2.0) * REF_LOAD_STD, 1)
            connected_users = max(5, int(REF_USERS_MEAN - random.uniform(1.2, 1.8) * REF_USERS_STD))
    
    elif attack_id == 6:  # TIME_DRIFTING
        attack_name = "TIME_DRIFTING"
        cell_load_mbps = round(REF_LOAD_MEAN + drift * 0.5, 1)
        connected_users = max(1, int(REF_USERS_MEAN - drift * 0.2))
        w0 = round(REF_LAT_MEAN + drift * 0.05, 2)
    
    # === CALCULOS DERIVADOS ===
    util_pct = round((cell_load_mbps / cell_capacity_mbps) * 100, 1)
    
    if cell_load_mbps > cell_capacity_mbps * 1.5:
        cell_status = "overload"
    elif cell_load_mbps > cell_capacity_mbps:
        cell_status = "high"
    else:
        cell_status = "normal"
    
    xapp_decision = "HANDOVER" if util_pct > 100 else "KEEP"
    avg_latency = round((w0 + w1 + w2 + w3) / 4, 2)
    
    return {
        "timestamp": ts,
        "segundo": t,
        "attack_id": attack_id,
        "attack_name": attack_name,
        "is_attack": 1 if attack_id != 0 else 0,
        "cell_load_mbps": cell_load_mbps,
        "cell_capacity_mbps": cell_capacity_mbps,
        "util_pct": util_pct,
        "connected_users": connected_users,
        "cell_status": cell_status,
        "xapp_decision": xapp_decision,
        "worker0_latency_ms": w0,
        "worker1_latency_ms": w1,
        "worker2_latency_ms": w2,
        "worker3_latency_ms": w3,
        "avg_latency_ms": avg_latency,
        "temp_bbu_celsius": temp_bbu,
        "a1_policy_active": a1_policy_active,
        "anomaly_score": round(abs(cell_load_mbps - REF_LOAD_MEAN) / REF_LOAD_STD, 2)
    }

# ===== GERACAO DO DATASET =====
rows = []

# Timeline:
#   0-179:   NORMAL (3 min)
#   180-359: OVERLOAD_FABRICATE (3 min)
#   360-539: NORMAL (3 min)
#   540-719: LATENCY_POISON (3 min)
#   720-899: HANDOVER_STORM (3 min)
#   900-959: ADVERSARIAL_NOISE (1 min)
#   960-1019: GRADIENT_MASKING (1 min)
#   1020-1079: TIME_DRIFTING (1 min)
#   1080-1199: NORMAL (2 min)

drift_accum = 0.0
drift_dir = 1

for t in range(TIMESTEPS):
    # Drift para TIME_DRIFTING
    drift_accum += drift_dir * 0.5
    if drift_accum > 100: drift_dir = -1
    elif drift_accum < 0: drift_dir = 1
    
    if t < 180:
        attack_id = 0
    elif 180 <= t < 360:
        attack_id = 1
    elif 360 <= t < 540:
        attack_id = 0
    elif 540 <= t < 720:
        attack_id = 2
    elif 720 <= t < 900:
        attack_id = 3
    elif 900 <= t < 960:
        attack_id = 4
    elif 960 <= t < 1020:
        attack_id = 5
    elif 1020 <= t < 1080:
        attack_id = 6
    else:
        attack_id = 0
    
    rows.append(gerar_registro(t, attack_id, drift_accum))

# ===== ESCRITA CSV =====
with open("dataset_xapp_ataques.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

# ===== ESTATISTICAS =====
from collections import Counter
counts = Counter(r['attack_id'] for r in rows)

print(f"[+] Dataset xApp gerado: dataset_xapp_ataques.csv")
print(f"    Total: {len(rows)} registros ({TIMESTEPS//60} min)")
print(f"\n--- Distribuicao ---")
print(f"  0 - NORMAL:               {counts[0]:>4}")
print(f"  1 - OVERLOAD_FABRICATE:   {counts[1]:>4}")
print(f"  2 - LATENCY_POISON:       {counts[2]:>4}")
print(f"  3 - HANDOVER_STORM:       {counts[3]:>4}")
print(f"  4 - ADVERSARIAL_NOISE:    {counts[4]:>4}")
print(f"  5 - GRADIENT_MASKING:     {counts[5]:>4}")
print(f"  6 - TIME_DRIFTING:        {counts[6]:>4}")

print(f"\n--- Timeline ---")
timeline = [
    (0, 179, "NORMAL"),
    (180, 359, "OVERLOAD_FABRICATE"),
    (360, 539, "NORMAL"),
    (540, 719, "LATENCY_POISON"),
    (720, 899, "HANDOVER_STORM"),
    (900, 959, "ADVERSARIAL_NOISE"),
    (960, 1019, "GRADIENT_MASKING"),
    (1020, 1079, "TIME_DRIFTING"),
    (1080, 1199, "NORMAL"),
]
for inicio, fim, nome in timeline:
    print(f"  {inicio:>4}-{fim:<4}: {nome}")