#!/bin/bash
echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > resultados.csv
echo "=== INICIANDO BENCHMARK CIENTIFICO (1 a 128 Workers) ==="

# 0. GARANTIA (Roda instantaneo se ja estiver 1/1)
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' > /dev/null 2>&1
kubectl rollout status deployment/metrics-server -n kube-system --timeout=10s > /dev/null 2>&1

# 1. Preparacao
echo ">>> Resetando arquitetura..."
kubectl delete -f oran-architecture.yaml --ignore-not-found=true > /dev/null 2>&1
kubectl apply -f oran-architecture.yaml
echo ">>> Aguardando pods subirem (20s)..."
sleep 20

# 3. Loop de Teste (ATUALIZADO PARA 64 e 128)
for WORKERS in 1 2 4 8 16 32 64 128
do
    echo "------------------------------------------------"
    echo ">>> Testando Nivel: $WORKERS Workers"

    kubectl scale deployment benchmark-worker --replicas=$WORKERS > /dev/null
    kubectl rollout status deployment/benchmark-worker --timeout=300s > /dev/null
    
    echo "    === Coletando metricas (60s) ==="
    sleep 60
    
    # Coleta CPU/MEM (Label corrigido: app=bench-worker)
    STATS=$(kubectl top pods -l app=bench-worker --no-headers 2>/dev/null | awk 'BEGIN {cpu=0; mem=0} {cpu+=$2; mem+=$3} END {print cpu "," mem}')
    
    if [ -z "$STATS" ] || [ "$STATS" == "," ]; then STATS="0,0"; fi
    
    # Coleta Latencia (Com LC_NUMERIC=C para evitar erro de virgula)
    RAW_LOGS=$(kubectl logs -l app=ric-platform --tail=100 2>/dev/null)
    if [ -z "$RAW_LOGS" ]; then
        LATENCY="0"
    else
        LATENCY=$(echo "$RAW_LOGS" | grep "DADO_CIENTIFICO" | awk -F'Latencia:' '{print $2}' | awk -F'ms' '{print $1}' | LC_NUMERIC=C awk '{sum+=$1; cnt++} END {if (cnt > 0) printf "%.2f", sum/cnt; else print 0}')
    fi
    if [ -z "$LATENCY" ]; then LATENCY="0"; fi
    
    echo "    >>> RESULTADO: CPU/RAM: $STATS | Latencia: $LATENCY ms"
    echo "$WORKERS,$STATS,$LATENCY" >> resultados.csv
done

echo "=== FIM. Dados salvos em 'resultados.csv' ==="