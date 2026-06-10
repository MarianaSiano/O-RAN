#!/usr/bin/env python3
"""
gerar_dataset_rapp.py - Dataset de ataques focados no rApp (O-RAN)
Gera 1200 timestamps (20 min) com 7 classes de ataque ao rApp

Classes:
    0 = NORMAL
    1 = ENERGY_POLICY_TOGGLE - alterna politica True/False a cada 2s
    2 = RESOURCE_DRAIN - força capacity_override=50
    3 = POLICY_FLOOD - inunda com centenas de políticas
    4 = ENERGY_DEPRIVATION - bloqueia economia (força False)
    5 = POLICY_CONFUSION - politicas conflitantes simultaneas
    6 = DATA_CAMOUFLAGE - politicas mascaradas como legítimas (IDS Evasion)
"""

import csv
import random
import math
from datetime import datetime, timedelta

random.seed(42)

TIMESTEPS = 1200
BASE = datetime(2026, 5, 19, 14, 0, 0)

def gerar_registro(t, attack_id):
    """Gera um registro baseado no tipo de ataque ao rApp"""
    ts = (BASE + timedelta(seconds=t)).isoformat()
    
    # Valores base (comportamento normal)
    cell_load_mbps = round(random.gauss(100, 25), 1)
    cell_capacity_mbps = 100
    connected_users = int(random.gauss(32, 10))
    a1_policy_value = False
    a1_policy_reason = "NONE"
    a1_policy_scope = "NONE"
    a1_policy_priority = "none"
    num_active_policies = 0
    policy_change_rate = 0.0
    temp_bbu = round(random.uniform(40, 44), 1)
    bbu_power_w = round(random.uniform(800, 1200), 1)
    
    w0 = round(random.gauss(12, 3), 2)
    w1 = round(random.gauss(12, 3), 2)
    w2 = round(random.gauss(12, 3), 2)
    w3 = round(random.gauss(12, 3), 2)
    
    attack_name = "NORMAL"
    policy_conflict_flag = 0
    anomalous_policy_count = 0
    
    # === MODIFICACOES POR TIPO DE ATAQUE ===
    
    if attack_id == 1:  # ENERGY_POLICY_TOGGLE
        attack_name = "ENERGY_POLICY_TOGGLE"
        # Alterna a cada 2 segundos (a cada 2 timestamps)
        a1_policy_value = (t // 2) % 2 == 0
        a1_policy_reason = "ENERGY_SAVING_OVERRIDE"
        a1_policy_scope = "UE_GROUP_1"
        a1_policy_priority = "high"
        num_active_policies = 1
        policy_change_rate = 0.5  # Muda a cada 2s
        cell_capacity_mbps = 80 if a1_policy_value else 100
    
    elif attack_id == 2:  # RESOURCE_DRAIN
        attack_name = "RESOURCE_DRAIN"
        a1_policy_value = True
        a1_policy_reason = "ENERGY_SAVING_CRITICAL"
        a1_policy_scope = "UE_GROUP_ALL"
        a1_policy_priority = "critical"
        num_active_policies = 1
        policy_change_rate = 0.05
        cell_capacity_mbps = 50  # Capacity reduzido pela metade!
        bbu_power_w = round(random.uniform(500, 700), 1)  # Menos energia
    
    elif attack_id == 3:  # POLICY_FLOOD
        attack_name = "POLICY_FLOOD"
        # Muitas politicas ativas simultaneamente
        a1_policy_value = random.choice([True, False])
        a1_policy_reason = random.choice(["ENERGY_SAVING", "LOAD_BALANCING", "QOS", "SPECTRUM"])
        a1_policy_scope = f"UE_GROUP_{random.randint(1, 100)}"
        a1_policy_priority = random.choice(["low", "medium", "high", "critical"])
        num_active_policies = random.randint(50, 200)  # Muitas politicas!
        policy_change_rate = random.uniform(5, 20)
        anomalous_policy_count = random.randint(10, 50)
    
    elif attack_id == 4:  # ENERGY_DEPRIVATION
        attack_name = "ENERGY_DEPRIVATION"
        a1_policy_value = False  # Forca economia DESLIGADA
        a1_policy_reason = "ENERGY_SAVING_OVERRIDE"
        a1_policy_scope = "UE_GROUP_ALL"
        a1_policy_priority = "critical"
        num_active_policies = 1
        policy_change_rate = 0.0  # Fixa (nao alterna)
        cell_capacity_mbps = 100  # Capacidade maxima (sem economia)
        bbu_power_w = round(random.uniform(1100, 1400), 1)  # Mais energia!
    
    elif attack_id == 5:  # POLICY_CONFUSION
        attack_name = "POLICY_CONFUSION"
        # Politicas conflitantes: mesmo scope com valores opostos
        a1_policy_value = random.choice([True, False])
        a1_policy_reason = "CONFLICT_TEST"
        a1_policy_scope = f"UE_GROUP_{random.randint(1, 5)}"
        a1_policy_priority = random.choice(["high", "medium"])
        num_active_policies = random.randint(2, 8)
        policy_change_rate = random.uniform(1, 3)
        policy_conflict_flag = 1
        cell_capacity_mbps = random.choice([80, 100])  # Instavel
    
    elif attack_id == 6:  # DATA_CAMOUFLAGE
        attack_name = "DATA_CAMOUFLAGE"
        # Parece normal mas tem intencao maliciosa
        a1_policy_value = random.choice([True, False])
        a1_policy_reason = "ENERGY_SAVING_SCHEDULED"
        a1_policy_scope = "UE_GROUP_1"
        a1_policy_priority = random.choice(["low", "medium"])
        num_active_policies = 1
        policy_change_rate = random.uniform(0.2, 0.5)
        cell_capacity_mbps = 80 if a1_policy_value else 100
    
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
        "a1_policy_value": a1_policy_value,
        "a1_policy_reason": a1_policy_reason,
        "a1_policy_scope": a1_policy_scope,
        "a1_policy_priority": a1_policy_priority,
        "num_active_policies": num_active_policies,
        "policy_change_rate": round(policy_change_rate, 2),
        "policy_conflict_flag": policy_conflict_flag,
        "anomalous_policy_count": anomalous_policy_count,
        "temp_bbu_celsius": temp_bbu,
        "bbu_power_w": bbu_power_w,
        "anomaly_score": round(abs(cell_load_mbps - 100) / 25, 2)
    }

# ===== GERACAO DO DATASET =====
rows = []

# Timeline:
#   0-179:   NORMAL (3 min)
#   180-359: ENERGY_POLICY_TOGGLE (3 min)
#   360-539: NORMAL (3 min)
#   540-719: RESOURCE_DRAIN (3 min)
#   720-899: POLICY_FLOOD (3 min)
#   900-959: ENERGY_DEPRIVATION (1 min)
#   960-1019: POLICY_CONFUSION (1 min)
#   1020-1079: DATA_CAMOUFLAGE (1 min)
#   1080-1199: NORMAL (2 min)

for t in range(TIMESTEPS):
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
    
    rows.append(gerar_registro(t, attack_id))

# ===== ESCRITA CSV =====
with open("dataset_rapp_ataques.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

# ===== ESTATISTICAS =====
from collections import Counter
counts = Counter(r['attack_id'] for r in rows)

print(f"[+] Dataset rApp gerado: dataset_rapp_ataques.csv")
print(f"    Total: {len(rows)} registros ({TIMESTEPS//60} min)")
print(f"\n--- Distribuicao ---")
print(f"  0 - NORMAL:                  {counts[0]:>4}")
print(f"  1 - ENERGY_POLICY_TOGGLE:    {counts[1]:>4}")
print(f"  2 - RESOURCE_DRAIN:          {counts[2]:>4}")
print(f"  3 - POLICY_FLOOD:            {counts[3]:>4}")
print(f"  4 - ENERGY_DEPRIVATION:      {counts[4]:>4}")
print(f"  5 - POLICY_CONFUSION:        {counts[5]:>4}")
print(f"  6 - DATA_CAMOUFLAGE:         {counts[6]:>4}")

print(f"\n--- Timeline ---")
timeline = [
    (0, 179, "NORMAL"),
    (180, 359, "ENERGY_POLICY_TOGGLE"),
    (360, 539, "NORMAL"),
    (540, 719, "RESOURCE_DRAIN"),
    (720, 899, "POLICY_FLOOD"),
    (900, 959, "ENERGY_DEPRIVATION"),
    (960, 1019, "POLICY_CONFUSION"),
    (1020, 1079, "DATA_CAMOUFLAGE"),
    (1080, 1199, "NORMAL"),
]
for inicio, fim, nome in timeline:
    print(f"  {inicio:>4}-{fim:<4}: {nome}")