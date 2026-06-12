import csv
import random
from datetime import datetime, timedelta

random.seed(42)

TIMESTEPS = 600
BASE = datetime(2026, 5, 19, 14, 0, 0)

# Configuração dos ataques por tipo
XAPP_ATTACKS = {
    1: "OVERLOAD_FABRICATE",
    2: "LATENCY_POISON"
}

RAPP_ATTACKS = {
    3: "ENERGY_POLICY_INJECTION",
    4: "RESOURCE_DRAIN"
}

# Fases do cenário:
# 0-179:   Normal
# 180-359: Ataque xApp (OVERLOAD_FABRICATE)
# 360-479: Ataque xApp (LATENCY_POISON)
# 480-539: Normal
# 540-599: Ataque rApp (ENERGY_POLICY_INJECTION)

def get_attack_phase(t):
    """Retorna (attack_id, attack_name, target) para o timestamp t"""
    if 180 <= t < 360:
        return (1, "OVERLOAD_FABRICATE", "xapp")
    elif 360 <= t < 480:
        return (2, "LATENCY_POISON", "xapp")
    elif 540 <= t < 600:
        return (3, "ENERGY_POLICY_INJECTION", "rapp")
    else:
        return (0, "NORMAL", None)

rows_xapp = []
rows_rapp = []

for t in range(TIMESTEPS):
    ts = (BASE + timedelta(seconds=t)).isoformat()
    attack_id, attack_name, target = get_attack_phase(t)
    is_attack = 1 if attack_id != 0 else 0
    
    # ============================================================
    # DADOS COMPARTILHADOS (base para ambos datasets)
    # ============================================================
    capacity = 100
    
    # Temperatura BBU (base)
    temp_bbu = round(random.uniform(40, 44), 1)
    alarme_energia = False
    
    # ============================================================
    # DATASET xApp - Foco em telemetria de célula e workers
    # ============================================================
    if target == "xapp":
        if attack_id == 1:  # OVERLOAD_FABRICATE
            cell_load_mbps = random.randint(210, 280)
            connected_users = random.randint(8, 20)
            cell_status = "overload"
            util_pct = round((cell_load_mbps / capacity) * 100, 1)
            xapp_decision = "HANDOVER"
            policy_active = False
            
            # Workers com latência normal (para não misturar ataques)
            w0 = round(random.gauss(12, 3), 2)
            w1 = round(random.gauss(12, 3), 2)
            w2 = round(random.gauss(12, 3), 2)
            w3 = round(random.gauss(12, 3), 2)
            
        elif attack_id == 2:  # LATENCY_POISON
            cell_load_mbps = random.randint(60, 120)
            connected_users = random.randint(20, 45)
            cell_status = "normal" if cell_load_mbps <= 100 else "overload"
            util_pct = round((cell_load_mbps / capacity) * 100, 1)
            xapp_decision = "HANDOVER" if util_pct > 100 else "KEEP"
            policy_active = random.choice([True, False])
            
            # Worker 0 com latência envenenada (40% das vezes)
            if random.random() < 0.4:
                w0 = round(random.uniform(800, 3000), 2)
            else:
                w0 = round(random.gauss(12, 3), 2)
            w1 = round(random.gauss(12, 3), 2)
            w2 = round(random.gauss(12, 3), 2)
            w3 = round(random.gauss(12, 3), 2)
        
        else:  # NORMAL (sem ataque xApp)
            cell_load_mbps = random.randint(50, 150)
            connected_users = random.randint(15, 50)
            cell_status = "overload" if cell_load_mbps > 100 else "normal"
            util_pct = round((cell_load_mbps / capacity) * 100, 1)
            xapp_decision = "HANDOVER" if util_pct > 100 else "KEEP"
            policy_active = random.choice([True, False])
            
            w0 = round(random.gauss(12, 3), 2)
            w1 = round(random.gauss(12, 3), 2)
            w2 = round(random.gauss(12, 3), 2)
            w3 = round(random.gauss(12, 3), 2)
        
        avg_latency_ms = round((w0 + w1 + w2 + w3) / 4, 2)
        
        row_xapp = {
            "timestamp": ts,
            "segundo": t,
            "attack_id": attack_id if target == "xapp" else 0,
            "attack_name": attack_name if target == "xapp" else "NORMAL",
            "is_attack": 1 if target == "xapp" and attack_id != 0 else 0,
            "cell_load_mbps": cell_load_mbps,
            "cell_capacity_mbps": capacity,
            "util_pct": util_pct,
            "connected_users": connected_users,
            "cell_status": cell_status,
            "xapp_decision": xapp_decision,
            "policy_active": policy_active,
            "worker0_latency_ms": w0,
            "worker1_latency_ms": w1,
            "worker2_latency_ms": w2,
            "worker3_latency_ms": w3,
            "avg_latency_ms": avg_latency_ms,
            "temp_bbu_celsius": temp_bbu,
            "alarme_energia": alarme_energia
        }
        rows_xapp.append(row_xapp)
    
    # ============================================================
    # DATASET rApp - Foco em políticas A1 e decisões de energia
    # ============================================================
    else:
        # Dados normais de célula (podem ser influenciados pelo rApp)
        if attack_id == 3:  # ENERGY_POLICY_INJECTION
            # rApp atacando: alterna política rapidamente
            cell_load_mbps = random.randint(50, 120)
            connected_users = random.randint(10, 30)
            cell_status = "normal"
            util_pct = round((cell_load_mbps / capacity) * 100, 1)
            xapp_decision = "KEEP"
            
            # Política A1 sendo manipulada (alterna a cada registro)
            a1_policy_value = random.choice([True, False])
            policy_active = a1_policy_value
            policy_stability = "unstable"
            energy_saving_mode = "forced_toggle"
            capacity_override = 80 if a1_policy_value else 100
            
            # Workers normais (ataque é no rApp)
            w0 = round(random.gauss(12, 3), 2)
            w1 = round(random.gauss(12, 3), 2)
            w2 = round(random.gauss(12, 3), 2)
            w3 = round(random.gauss(12, 3), 2)
            
            # Pode gerar alarme de energia se política muda muito
            alarme_energia = True if random.random() < 0.3 else False
            
        else:  # NORMAL (sem ataque rApp)
            cell_load_mbps = random.randint(50, 150)
            connected_users = random.randint(15, 50)
            cell_status = "overload" if cell_load_mbps > 100 else "normal"
            util_pct = round((cell_load_mbps / capacity) * 100, 1)
            xapp_decision = "HANDOVER" if util_pct > 100 else "KEEP"
            
            policy_active = random.choice([True, False])
            a1_policy_value = policy_active
            policy_stability = "stable"
            energy_saving_mode = "normal"
            capacity_override = 100
            
            w0 = round(random.gauss(12, 3), 2)
            w1 = round(random.gauss(12, 3), 2)
            w2 = round(random.gauss(12, 3), 2)
            w3 = round(random.gauss(12, 3), 2)
            
            alarme_energia = False
        
        avg_latency_ms = round((w0 + w1 + w2 + w3) / 4, 2)
        
        row_rapp = {
            "timestamp": ts,
            "segundo": t,
            "attack_id": attack_id if target == "rapp" else 0,
            "attack_name": attack_name if target == "rapp" else "NORMAL",
            "is_attack": 1 if target == "rapp" and attack_id != 0 else 0,
            "cell_load_mbps": cell_load_mbps,
            "cell_capacity_mbps": capacity,
            "util_pct": util_pct,
            "connected_users": connected_users,
            "cell_status": cell_status,
            "xapp_decision": xapp_decision,
            "policy_active": policy_active,
            "a1_policy_value": a1_policy_value,
            "policy_stability": policy_stability,
            "energy_saving_mode": energy_saving_mode,
            "capacity_override": capacity_override,
            "worker0_latency_ms": w0,
            "worker1_latency_ms": w1,
            "worker2_latency_ms": w2,
            "worker3_latency_ms": w3,
            "avg_latency_ms": avg_latency_ms,
            "temp_bbu_celsius": temp_bbu,
            "alarme_energia": alarme_energia
        }
        rows_rapp.append(row_rapp)

# ============================================================
# ESCREVE DATASET xApp
# ============================================================
if rows_xapp:
    with open("oran_xapp_dataset.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_xapp[0].keys())
        w.writeheader()
        w.writerows(rows_xapp)

    print(f"[+] Dataset xApp gerado: oran_xapp_dataset.csv")
    print(f"    Total: {len(rows_xapp)} registros")
    print(f"    Normal: {sum(1 for r in rows_xapp if r['is_attack']==0)}")
    print(f"    OVERLOAD_FABRICATE: {sum(1 for r in rows_xapp if r['attack_id']==1)}")
    print(f"    LATENCY_POISON: {sum(1 for r in rows_xapp if r['attack_id']==2)}")

# ============================================================
# ESCREVE DATASET rApp
# ============================================================
if rows_rapp:
    with open("oran_rapp_dataset.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows_rapp[0].keys())
        w.writeheader()
        w.writerows(rows_rapp)

    print(f"\n[+] Dataset rApp gerado: oran_rapp_dataset.csv")
    print(f"    Total: {len(rows_rapp)} registros")
    print(f"    Normal: {sum(1 for r in rows_rapp if r['is_attack']==0)}")
    print(f"    ENERGY_POLICY_INJECTION: {sum(1 for r in rows_rapp if r['attack_id']==3)}")

# ============================================================
# RESUMO COMPLETO DA TIMELINE
# ============================================================
print(f"\n--- Timeline de Ataques (10 minutos / 600 segundos) ---")
print(f"   0-179 (3 min):  NORMAL - Sem ataques")
print(f" 180-359 (3 min):  xApp - OVERLOAD_FABRICATE (carga falsa >200Mbps)")
print(f" 360-479 (2 min):  xApp - LATENCY_POISON (worker com alta latência)")
print(f" 480-539 (1 min):  NORMAL - Período de recuperação")
print(f" 540-599 (1 min):  rApp - ENERGY_POLICY_INJECTION (política A1 instável)")

print(f"\n--- Campos específicos por dataset ---")
print(f"   xApp: cell_load, cell_capacity, util_pct, xapp_decision, workers_latency")
print(f"   rApp: a1_policy_value, policy_stability, energy_saving_mode, capacity_override")