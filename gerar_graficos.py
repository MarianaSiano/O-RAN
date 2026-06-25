"""
plot_benchmark.py — Gera gráficos científicos do benchmark de escalabilidade.
Uso: python plot_benchmark.py [--input resultados.csv] [--output benchmark_report.png]
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Configuração Global de Estilo ---
plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "lines.linewidth": 2.2,
    "lines.markersize": 8,
})

# --- Paleta de Cores ---
COLORS = {
    "cpu": "#2196F3",       # Azul material
    "ram": "#4CAF50",       # Verde material
    "latency": "#F44336",   # Vermelho material
    "grid": "#E0E0E0",
    "bg": "#FAFAFA",
}

# --- Funções de plotagem ---

def plot_metric(ax, x, y, color, marker, title, ylabel, unit, fmt=".1f"):
    """Plota uma métrica com estilo padronizado."""
    ax.plot(x, y, color=color, marker=marker, markeredgecolor="white",
            markeredgewidth=0.8, linewidth=2.2, zorder=3)

    # Preenche área sob a curva (gradiente suave)
    ax.fill_between(x, y, alpha=0.08, color=color, zorder=1)

    # Pontos com rótulo
    for xi, yi in zip(x, y):
        if pd.notna(yi):
            ax.annotate(
                f"{yi:{fmt}}",
                (xi, yi),
                textcoords="offset points",
                xytext=(0, 12),
                ha="center",
                fontsize=8,
                color=color,
                fontweight="bold",
            )

    # Rótulos
    ax.set_title(title, fontweight="bold", pad=12)
    ax.set_xlabel("Número de Workers", fontweight="bold")
    ax.set_ylabel(f"{ylabel} ({unit})", fontweight="bold")

    # Grid e fundo
    ax.set_facecolor(COLORS["bg"])
    ax.grid(True, linestyle="--", alpha=0.5, color=COLORS["grid"], zorder=0)
    ax.set_axisbelow(True)

    # Escala x: garante que todos os ticks apareçam
    ax.xaxis.set_major_locator(mticker.FixedLocator(x))
    ax.xaxis.set_major_formatter(mticker.ScalarFormatter())

    return ax


def create_combined_report(df: pd.DataFrame, output_path: str = "benchmark_report.png") -> None:
    """Gera um relatório consolidado com 4 painéis (3 métricas + tabela)."""
    fig = plt.figure(figsize=(18, 12))
    fig.patch.set_facecolor("white")

    # Layout: 2x2 grid com larguras/alturas customizadas
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.30,
                        height_ratios=[1, 1.1])

    ax1 = fig.add_subplot(gs[0, 0])  # CPU
    ax2 = fig.add_subplot(gs[0, 1])  # RAM
    ax3 = fig.add_subplot(gs[1, 0])  # Latência
    ax4 = fig.add_subplot(gs[1, 1])  # Tabela resumo

    x = df["workers"]

    # --- CPU ---
    y_cpu = df["cpu_total_m"]
    plot_metric(ax1, x, y_cpu, COLORS["cpu"], "o",
                "Consumo Total de CPU", "CPU", "mCore")

    # --- RAM ---
    y_ram = df["ram_total_mi"]
    plot_metric(ax2, x, y_ram, COLORS["ram"], "s",
                "Consumo Total de RAM", "Memória", "MiB", fmt=".0f")

    # --- Latência ---
    y_lat = df["latencia_media_ms"]
    plot_metric(ax3, x, y_lat, COLORS["latency"], "^",
                "Latência Média (RTT)", "Tempo", "ms")
    ax3.set_xlabel("Número de Workers", fontweight="bold")

    # --- Tabela resumo ---
    ax4.axis("off")
    table_data = []
    col_labels = ["Workers", "CPU (mC)", "RAM (MiB)", "Latência (ms)"]

    for _, row in df.iterrows():
        table_data.append([
            f"{int(row['workers'])}",
            f"{row['cpu_total_m']:.1f}",
            f"{row['ram_total_mi']:.0f}",
            f"{row['latencia_media_ms']:.2f}",
        ])

    table = ax4.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc="center",
        loc="center",
        colWidths=[0.15, 0.25, 0.25, 0.30],
    )

    # Estilo da tabela
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.6)

    for (row, col), cell in table.get_celld().items():
        if row == 0:  # Cabeçalho
            cell.set_facecolor("#37474F")
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor("#F5F5F5" if row % 2 == 0 else "#FFFFFF")
        cell.set_edgecolor("#BDBDBD")
        cell.set_linewidth(0.8)

    ax4.set_title("Resumo dos Resultados", fontweight="bold",
                fontsize=14, pad=20, color="#37474F")

    # --- Título geral ---
    fig.suptitle(
        "Benchmark de Escalabilidade — RIC Platform",
        fontsize=18,
        fontweight="bold",
        y=0.98,
        color="#1A237E",
    )

    # --- Rodapé ---
    fig.text(
        0.5, 0.01,
        f"Gerado em: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Dados: {output_path}",
        ha="center", fontsize=9, color="#757575",
    )

    plt.savefig(output_path)
    plt.close()
    print(f">>> Relatório consolidado salvo: {output_path}")


def create_individual_charts(df: pd.DataFrame) -> None:
    """Gera gráficos individuais (compatibilidade com versão original)."""
    configs = [
        ("workers", "cpu_total_m",     "grafico_cpu.png",     "Consumo Total de CPU",     "CPU (mCore)",     "o", COLORS["cpu"]),
        ("workers", "ram_total_mi",    "grafico_ram.png",     "Consumo Total de RAM",     "Memória (MiB)",   "s", COLORS["ram"]),
        ("workers", "latencia_media_ms", "grafico_latencia.png", "Latência Média (RTT)",  "Tempo (ms)",      "^", COLORS["latency"]),
    ]

    for xcol, ycol, fname, title, ylabel, marker, color in configs:
        fig, ax = plt.subplots(figsize=(8, 6))
        plot_metric(ax, df[xcol], df[ycol], color, marker, title, ylabel.split(" (")[0],
                    ylabel.split("(")[1].rstrip(")") if "(" in ylabel else "")
        fig.tight_layout()
        fig.savefig(fname)
        plt.close(fig)
        print(f">>> Salvo: {fname}")


def main():
    parser = argparse.ArgumentParser(
        description="Gera gráficos científicos do benchmark de escalabilidade.",
    )
    parser.add_argument(
        "--input", "-i",
        default="resultados.csv",
        help="Arquivo CSV de entrada (default: resultados.csv)",
    )
    parser.add_argument(
        "--output", "-o",
        default="benchmark_report.png",
        help="Arquivo PNG de saída do relatório consolidado (default: benchmark_report.png)",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        help="Gera também gráficos individuais (grafico_cpu.png, etc.)",
    )
    args = parser.parse_args()

    # --- Carrega dados ---
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erro: Arquivo '{args.input}' não encontrado.")
        sys.exit(1)

    df = pd.read_csv(args.input)
    print("Dados carregados com sucesso:")
    print(df.to_string(index=False))

    # Valida colunas obrigatórias
    required_cols = {"workers", "cpu_total_m", "ram_total_mi", "latencia_media_ms"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"Erro: Colunas ausentes no CSV: {missing}")
        sys.exit(1)

    # --- Gera relatório ---
    create_combined_report(df, args.output)

    # --- Gráficos individuais (opcional) ---
    if args.individual:
        create_individual_charts(df)

    print("\n=== Todos os gráficos foram gerados com sucesso! ===")


if __name__ == "__main__":
    main()