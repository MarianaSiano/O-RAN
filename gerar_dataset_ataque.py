import csv
import random
from datetime import datetime, timedelta

random.seed(42)

TIMESTEPS = 600
BASE = datetime(2026, 5, 19, 14, 0, 0)

rows = []
for t in range(TIMESTEPS):
    ts = (BASE + timedelta(seconds=t)).isoformat()
    
    # Fases: 0-179 normal, 180-359 ataque, 360-539 normal, 540-599 ataque
    if 180 <= t < 360 or t >= 540:
        # MODO ATAQUE
        attack_id = 1 if t < 360 else 2
        attack_name = "OVERLOAD_FABRICATE" if t < 360 else "ENERGY_POLICY_INJECTION"
        load = random.randint(210, 280)  # Load falso >200
        capacity = 100
        users = random.randint(8, 20)  # Poucos usuarios (inconsistente)
        policy_active = False
        cell_status = "overload"
        util_pct = round((load / capacity) * 100, 1)
        xapp_decision = "HANDOVER"
        
        # Latencia dos workers (ataque: worker0 com valores altos as vezes)
        if t >= 540 and random.random() < 0.4:
            w0 = round(random.uniform(500, 2500), 2)  # Latencia envenenada
        else:
            w0 = round(random.gauss(12, 3), 2)
        
        w1 = round(random.gauss(12, 3), 2)
        w2 = round(random.gauss(12, 3), 2)
        w3 = round(random.gauss(12, 3), 2)
        avg_lat = round((w0 + w1 + w2 + w3) / 4, 2)
        
        # rApp - politica alterada no ataque 2
        if t >= 540:
            a1_policy = random.choice([True, False])  # Alternando sem controle
        else:
            a1_policy = False
        
        temp_bbu = round(random.uniform(42, 45), 1)
        alarme = False
        
    else:
        # MODO NORMAL
        attack_id = 0
        attack_name = "NORMAL"
        load = random.randint(50, 150)
        capacity = 100
        users = random.randint(15, 50)
        policy_active = random.choice([True, False])
        cell_status = "overload" if load > 100 else "normal"
        util_pct = round((load / capacity) * 100, 1)
        xapp_decision = "HANDOVER" if util_pct > 100 else "KEEP"
        
        w0 = round(random.gauss(12, 3), 2)
        w1 = round(random.gauss(12, 3), 2)
        w2 = round(random.gauss(12, 3), 2)
        w3 = round(random.gauss(12, 3), 2)
        avg_lat = round((w0 + w1 + w2 + w3) / 4, 2)
        
        a1_policy = policy_active
        temp_bbu = round(random.uniform(40, 44), 1)
        alarme = False
    
    is_attack = 1 if attack_id != 0 else 0
    
    row = {
        "timestamp": ts,
        "segundo": t,
        "attack_id": attack_id,
        "attack_name": attack_name,
        "is_attack": is_attack,
        "cell_load_mbps": load,
        "cell_capacity_mbps": capacity,
        "util_pct": util_pct,
        "connected_users": users,
        "cell_status": cell_status,
        "xapp_decision": xapp_decision,
        "policy_active": policy_active,
        "a1_policy_value": a1_policy,
        "worker0_latency_ms": w0,
        "worker1_latency_ms": w1,
        "worker2_latency_ms": w2,
        "worker3_latency_ms": w3,
        "avg_latency_ms": avg_lat,
        "temp_bbu_celsius": temp_bbu,
        "alarme_energia": alarme
    }
    rows.append(row)

# Escreve CSV
with open("oran_attack_dataset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f"[+] Dataset gerado: oran_attack_dataset.csv")
print(f"    Total: {len(rows)} registros")
print(f"    Normal (attack_id=0): {sum(1 for r in rows if r['attack_id']==0)}")
print(f"    Ataque 1 - OVERLOAD_FABRICATE: {sum(1 for r in rows if r['attack_id']==1)}")
print(f"    Ataque 2 - ENERGY_POLICY_INJECTION: {sum(1 for r in rows if r['attack_id']==2)}")

# Resumo
print(f"\n--- Timeline dos Ataques ---")
print(f"  0-179:  NORMAL (3 min)")
print(f" 180-359: ATAQUE 1 - OVERLOAD_FABRICATE (3 min)")
print(f" 360-539: NORMAL (3 min)")
print(f" 540-599: ATAQUE 2 - ENERGY_POLICY_INJECTION + LATENCY POISON (1 min)")