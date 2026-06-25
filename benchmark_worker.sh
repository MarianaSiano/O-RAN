# benchmark_workers.sh — Benchmark científico de escalabilidade no Kubernetes
# Mede CPU, RAM e latência média de 1 a 128 workers.
#
# Uso: ./benchmark_workers.sh
#

set -euo pipefail  # Sai em erro, undefined vars e pipes falhos

# --- Configurações ---
readonly CSV_FILE="resultados.csv"
readonly ARCHITECTURE_FILE="oran-architecture.yaml"
readonly APP_LABEL="app=bench-worker"
readonly RIC_LABEL="app=ric-platform"
readonly METRICS_NAMESPACE="kube-system"
readonly SCALE_TIMEOUT=300      # segundos
readonly COLLECTION_TIME=60     # segundos de coleta por rodada
readonly WORKER_VALUES=(1 2 4 8 16 32 64 128)

# --- Cores para output (desliga se não for terminal) ---
if [[ -t 1 ]]; then
    readonly RED='\033[0;31m'
    readonly GREEN='\033[0;32m'
    readonly YELLOW='\033[0;33m'
    readonly CYAN='\033[0;36m'
    readonly NC='\033[0m' # No Color
else
    readonly RED='' GREEN='' YELLOW='' CYAN='' NC=''
fi

log_info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERRO]${NC}  $*"; }
log_step()  { echo -e "${CYAN}[STEP]${NC}  $*"; }

# --- Funções ---
ensure_metrics_server() {
    """Garante que o metrics-server esteja rodando com --kubelet-insecure-tls."""
    log_step "Garantindo metrics-server com --kubelet-insecure-tls..."

    # Verifica se o arg já existe antes de adicionar (idempotente)
    local current_args
    current_args=$(kubectl get deployment metrics-server \
        -n "$METRICS_NAMESPACE" \
        -o jsonpath='{.spec.template.spec.containers[0].args}' 2>/dev/null || echo "")

    if echo "$current_args" | grep -q "kubelet-insecure-tls"; then
        log_info "metrics-server já configurado com --kubelet-insecure-tls"
    else
        kubectl patch deployment metrics-server \
            -n "$METRICS_NAMESPACE" \
            --type='json' \
            -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' \
            >/dev/null
        log_info "Patch aplicado. Aguardando rollout..."
    fi

    kubectl rollout status deployment/metrics-server \
        -n "$METRICS_NAMESPACE" \
        --timeout=30s >/dev/null 2>&1 || log_warn "rollout do metrics-server pode não ter completado"
}

reset_architecture() {
    """Remove e recria a arquitetura ORAN."""
    log_step "Resetando arquitetura ($ARCHITECTURE_FILE)..."
    kubectl delete -f "$ARCHITECTURE_FILE" --ignore-not-found=true >/dev/null
    kubectl apply -f "$ARCHITECTURE_FILE" >/dev/null
    log_info "Arquitetura aplicada. Aguardando pods (20s)..."
    sleep 20
}

scale_workers() {
    """Escala o deployment para N réplicas e aguarda estabilização."""
    local replicas="$1"
    log_step "Escalando benchmark-worker para $replicas réplicas..."
    kubectl scale deployment benchmark-worker --replicas="$replicas" >/dev/null

    if ! kubectl rollout status deployment/benchmark-worker \
        --timeout="${SCALE_TIMEOUT}s" >/dev/null 2>&1; then
        log_warn "Rollout não completou em ${SCALE_TIMEOUT}s — continuando mesmo assim"
    fi
}

collect_cpu_mem() {
    """Coleta CPU e memória total dos workers. Retorna 'cpu_total,mem_total'."""
    local stats
    stats=$(kubectl top pods -l "$APP_LABEL" --no-headers 2>/dev/null \
        | awk 'BEGIN {cpu=0; mem=0} {cpu+=$2; mem+=$3} END {print cpu+0 "," mem+0}')

    if [[ -z "$stats" || "$stats" == "," ]]; then
        log_warn "Nenhuma métrica de CPU/RAM coletada (top pods vazio ou indisponível)"
        echo "0,0"
    else
        echo "$stats"
    fi
}

collect_latency() {
    """Calcula a latência média a partir dos logs do RIC platform."""
    local raw_logs avg_latency

    raw_logs=$(kubectl logs -l "$RIC_LABEL" --tail=100 2>/dev/null || true)

    if [[ -z "$raw_logs" ]]; then
        log_warn "Nenhum log encontrado para label $RIC_LABEL"
        echo "0"
        return
    fi

    # Extrai valores de latência e calcula média com locale C (ponto decimal)
    avg_latency=$(echo "$raw_logs" \
        | grep "DADO_CIENTIFICO" \
        | awk -F'Latencia:' '{print $2}' \
        | awk -F'ms' '{print $1}' \
        | LC_NUMERIC=C awk '
            {sum+=$1; cnt++}
            END {
                if (cnt > 0) printf "%.2f", sum/cnt;
                else print "0"
            }' 2>/dev/null || echo "0")

    echo "$avg_latency"
}

run_benchmark_cycle() {
    """Executa um ciclo completo de benchmark para um número de workers."""
    local workers="$1"
    local cpu_mem latency

    echo "──────────────────────────────────────────────────────────────────"
    log_step "Testando Nível: ${workers} Workers"

    scale_workers "$workers"

    log_info "Coletando métricas por ${COLLECTION_TIME}s..."
    sleep "$COLLECTION_TIME"

    cpu_mem=$(collect_cpu_mem)
    latency=$(collect_latency)

    echo -e "    ${GREEN}► RESULTADO:${NC} CPU/RAM: $cpu_mem | Latência: ${latency} ms"
    echo "$workers,$cpu_mem,$latency" >> "$CSV_FILE"
}

# --- Main ---
main() {
    echo "================================================================"
    echo "  BENCHMARK CIENTÍFICO (1 a ${WORKER_VALUES[-1]} Workers)"
    echo "  Data: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "================================================================"

    # Cria cabeçalho do CSV (sobrescreve arquivo anterior)
    echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > "$CSV_FILE"
    log_info "CSV inicializado: $CSV_FILE"

    # Verifica dependências
    for cmd in kubectl awk grep sleep; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Comando não encontrado: $cmd"
            exit 1
        fi
    done

    # Preparação
    ensure_metrics_server
    reset_architecture

    # Loop principal
    for workers in "${WORKER_VALUES[@]}"; do
        run_benchmark_cycle "$workers"
    done

    echo "================================================================"
    log_info "Benchmark concluído com sucesso!"
    log_info "Resultados salvos em: ${CSV_FILE}"
    cat "$CSV_FILE"
}