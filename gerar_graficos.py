import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregar dados
try:
    df = pd.read_csv('resultados.csv')
    print("Dados carregados com sucesso")
except:
    print("Erro: Arquivo 'resultados.csv' não encontrado")
    exit()

# 2. Configurar a figura
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle('Benchmark O-RAN: Escalabilidade (1-128 Workers)', fontsize=16)

# Gráfico 1: CPU
ax1.plot(df['workers'], df['cpu_total_m'], marker='o', color='tab:blue')
ax1.set_title('CPU Total (mCore)')
ax1.set_xlabel('Workers')
ax1.grid(True, linestyle='--')

# Grafico 2: RAM
ax2.plot(df['workers'], df['ram_total_mi'], marker='s', color='tab:green')
ax2.set_title('Memoria Total (MiB)')
ax2.set_xlabel('Workers')
ax2.grid(True, linestyle='--')

# Grafico 3: Latencia
ax3.plot(df['workers'], df['latencia_media_ms'], marker='^', color='tab:red')
ax3.set_title('Latencia Media (ms)')
ax3.set_xlabel('Workers')
ax3.grid(True, linestyle='--')

plt.tight_layout()
plt.savefig('graficos_benchmark.png')
print(">>> Graficos salvos em 'graficos_benchmark.png'")