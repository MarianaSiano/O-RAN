import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar dados
try:
    df = pd.read_csv('resultados.csv')
    print("Dados carregados com sucesso.")
    print(df) # Mostra no terminal para conferencia
except:
    print("Erro: Arquivo 'resultados.csv' não encontrado.")
    exit()

# --- GRAFICO 1: CPU ---
plt.figure(figsize=(8, 6))
plt.plot(df['workers'], df['cpu_total_m'], marker='o', color='tab:blue', linewidth=2)
plt.title('Consumo Total de CPU')
plt.xlabel('Número de Workers')
plt.ylabel('CPU (mCore)')
plt.grid(True, linestyle='--')
plt.savefig('grafico_cpu.png')
plt.close()
print(">>> Salvo: grafico_cpu.png")

# --- GRAFICO 2: RAM ---
plt.figure(figsize=(8, 6))
plt.plot(df['workers'], df['ram_total_mi'], marker='s', color='tab:green', linewidth=2)
plt.title('Consumo Total de RAM')
plt.xlabel('Número de Workers')
plt.ylabel('Memória (MiB)')
plt.grid(True, linestyle='--')
plt.savefig('grafico_ram.png')
plt.close()
print(">>> Salvo: grafico_ram.png")

# --- GRAFICO 3: LATENCIA ---
plt.figure(figsize=(8, 6))
plt.plot(df['workers'], df['latencia_media_ms'], marker='^', color='tab:red', linewidth=2)
plt.title('Latência Média (RTT)')
plt.xlabel('Número de Workers')
plt.ylabel('Tempo (ms)')
plt.grid(True, linestyle='--')
plt.savefig('grafico_latencia.png')
plt.close()
print(">>> Salvo: grafico_latencia.png")

print("\n=== Todos os gráficos foram gerados separadamente! ===")