import time
import os

# Pega o endereço do RIC injetado pelo Kubernetes
ric_host = os.getenv('RIC_HOST', 'localhost')

print(f"--- INICIANDO xApp (Near-RT) ---")
print(f"Alvo detectado (RIC): {ric_host}")

while True:
    # Simula uma decisão de controle (ex: Mudar usuário de antena)
    print(f"[xApp] Enviando comando 'TRAFFIC STEERING' via interface E2 para {ric_host}...")
    time.sleep(5)