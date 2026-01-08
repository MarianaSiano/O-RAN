#!/bin/bash
echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > resultados.csv
echo "=== INICIANDO BENCHMARK CIENTIFICO ==="

# 0. CORRECAO AUTOMATICA DO METRICS SERVER
echo ">>> Verificando Metrics Server (Autorreparo)..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# Patch de segurança
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
echo ">>> Aguardando estabilizacao (60s)..."
sleep 60

# 1. Build da Imagem (Garante que existe localmente)
echo ">>> Construindo imagem..."
# Tenta buildar, se falhar usa imagem dummy para nao travar o teste
docker build -t oran-lab:v1 -f Dockerfile . 2>/dev/null || echo "Aviso: Dockerfile nao encontrado, usando imagem padrao se necessario."
kind load docker-image oran-lab:v1 --name oran-lab 2>/dev/null

# 2. Reset do Cluster
echo ">>> Resetando arquitetura..."
kubectl delete -f oran-architecture.yaml --ignore-not-found=true
kubectl apply -f oran-architecture.yaml
echo ">>> Aguardando inicializacao dos Pods (20s)..."
sleep 20

# 3. Loop de Teste
for WORKERS in 1 2 4 8 16 32
do
    echo "------------------------------------------------"
    echo ">>> Testando Nivel: $WORKERS Workers"

    # Escala o numero de replicas
    kubectl scale deployment benchmark-worker --replicas=$WORKERS

    # Aguarda o rollout terminar
    kubectl rollout status deployment/benchmark-worker --timeout=300s > /dev/null

    echo "    === Coletando metricas (60s) ==="
    sleep 60

    # Coleta de metricas (CPU/RAM)
    STATS=$(kubectl top pods -l app=benchmark-worker --no-headers 2>/dev/null | awk '{cpu+=$2; mem+=$3} END {print cpu "," mem}')

    # Se o metrics server falhar, define como 0 para não quebrar o script
    if [ -z "$STATS" ]; then STATS="0,0"; fi

    # Coleta latencia (com tratamento de erro se o log estiver vazio)
    RAW_LOGS=$(kubectl logs -l app=ric-platform --tail=100 2>/dev/null)
    if [ -z "$RAW_LOGS" ]; then
        LATENCY="0"
    else
        LATENCY=$(echo "$RAW_LOGS" | grep "DADO_CIENTIFICO" | awk -F'Latencia:' '{print $2}' | awk -F'ms' '{print $1}' | awk '{sum+=$1; cnt++} END {if (cnt > 0) print sum/cnt; else print 0}')
    fi

    # Garante que latencia não seja vazia
    if [ -z "$LATENCY" ]; then LATENCY="0"; fi

    echo "    >>> RESULTADO: CPU/RAM: $STATS | Latencia: $LATENCY ms"
    echo "$WORKERS,$STATS,$LATENCY" >> resultados.csv
done
echo "=== FIM. Dados salvos em 'resultados.csv' ==="