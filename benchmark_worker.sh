#!/bin/bash
echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > resultados.csv
echo "=== INICIANDO BENCHMARK EM ARQUITETURA COMPLETA ==="

# 1. Build da Imagem Unificada (Garante que todos os scripts estao la)
echo ">>> Construindo imagem unificada..."
docker build -t oran-lab:v1 -f Dockerfile . > /dev/null
kind load docker-image oran-lab:v1 --name oran-lab

# 2. Aplica seu YAML Completo
echo ">>> Aplicando arquitetura completa..."
kubectl delete -f oran-architecture.yaml --ignore-not-found=true
kubectl apply -f oran-architecture.yaml
echo ">>> Aguardando start inicial (15s)..."
sleep 15

# 3. Loop de Teste (Afeta apenas o benchmark-worker)
for WORKERS in 1 2 4 8 16 32 64 128
do
    echo "------------------------------------------------"
    echo ">>> Testando Nivel: $WORKERS Workers de Benchmark"

    # Escalar APENAS o worker de benchmark (Deixa os outros quietos)
    kubectl scale deployment benchmark-worker --replicas=$WORKERS > /dev/null

    # Aguardar Convergencia 
    kubectl rollout status deployment/benchmark-worker --timeout=300s > /dev/null

    # Coleta de Dados
    echo "   ... Coletando metricas (45s)..."
    sleep 45

    # Coleta CPU/RAM (Filtra APENAS pelo label do benchmark)
    STATS=$(kubectl top pods -l app=bench-worker --no-headers 2>/dev/null | awk '{cpu+=$2; mem+=$3} END {print cpu "," mem}')
    
    if [ -z "$STATS" ]; then STATS="0,0"; fi

    # Coleta Latencia (O RIC processa dados de todos, filtramos pelo log cientifico)
    LATENCY=$(kubectl logs -l app=ric-platform --tail=100 | grep "DADO_CIENTIFICO" | awk -F'Latencia:' '{print $2}' | awk '{sum+=$1; cnt++} END {if (cnt > 0) print sum/cnt; else print 0}')

    echo "   >>> RESULTADO: CPU/RAM: $STATS | Latencia: $LATENCY ms"
    echo "$WORKERS,$STATS,$LATENCY" >> resultados.csv
done

echo "=== FIM. Verifique 'resultados.csv' ==="
cat resultados.csv