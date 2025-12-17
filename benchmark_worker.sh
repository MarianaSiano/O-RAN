#!/bin/bash
echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > resultados.csv
echo "=== INICIANDO BENCHMARK CIENTIFICO (App Workers) ==="

# Garante inicio limpo
kubectl delete -f oran-architecture.yaml --ignore-not-found=true
kubectl apply -f oran-architecture.yaml
echo ">>> Inicializando Arquitetura Completa (10s)..."
sleep 10

for WORKERS in 1 2 4 8 16 32 64 128
do
    echo "------------------------------------------------"
    echo ">>> Testando Nivel: $WORKERS Workers"

    # 1. Escalar o WORKER DE TESTE
    kubectl scale deployment benchmark-worker --replicas=$WORKERS > /dev/null

    # 2. Aguardar Convergencia
    kubectl rollout status deployment/benchmark-worker --timeout=300s > /dev/null

    # 3. Coleta de Dados
    echo "   ... Coletando metricas..."
    sleep 15

    # Coleta CPU/RAM (Filtra pelo label do worker)
    # ATENÇÃO: Aqui não tem mais a barra invertida antes do $
    STATS=$(kubectl top pods -l app=bench-worker --no-headers 2>/dev/null | awk '{cpu+=$2; mem+=$3} END {print cpu "," mem}')
    
    if [ -z "$STATS" ]; then STATS="0,0"; fi

    # Coleta Latencia
    LATENCY=$(kubectl logs -l app=ric-platform --tail=50 | grep "Latencia" | awk -F'Latencia:' '{print $2}' | awk -F'ms' '{print $1}' | awk '{sum+=$1; n++} END {if (n > 0) print sum / n; else print 0}')

    echo "   >>> RESULTADO: CPU/RAM: $STATS | Latencia: $LATENCY ms"
    echo "$WORKERS,$STATS,$LATENCY" >> resultados.csv
done

echo "=== FIM. Verifique 'resultados.csv' ==="
cat resultados.csv