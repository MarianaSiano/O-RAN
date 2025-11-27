import time
import os

ric_host = os.getenv('RIC_HOST', 'localhost')

print(f"--- INICIANDO rApp (Non-RT) ---")
print(f"Conectado ao RIC em: {ric_host}")

while True:
    # Simula envio de política (ex: Desligar antenas ociosas a noite)
    print(f"[rApp] Analisando histórico e enviando POLÍTICA DE ENERGIA via interface A1...")
    time.sleep(10)