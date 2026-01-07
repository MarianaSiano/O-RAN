#!/bin/bash
echo "workers,cpu_total_m,ram_total_mi,latencia_media_ms" > resultados.csv
echo "=== INICIANDO BENCHMARK CIENTIFICO ==="

# 0. CORRECAO AUTOMATICA DO METRICS SERVER
echo ">>> Verificando Metrics Server (Autorreparo)..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
echo ">>> Aguardando estabilizacao (60s)..."
sleep 60

# 1. Build da Imagem Unificada
echo ">>> Construindo imagem..."
docker build -t oran-lab:v1 -f Dockerfile . > /dev/null
kind load docker-image oran-lab:v1 --name oran-lab

# 2. Reset do Cluster
echo ">>> Resetando arquitetura..."
kubectl delete -f oran-architecture.yaml --ignore-not-found=true
kubectl apply -f oran-architecture.yaml
echo ">>> Aguardando inicializacao (15s)..."
sleep 15

# 3. Loop de Teste
for WORKERS in 1 2 4 8 16 32 64 128
do
    echo "------------------------------------------------"
    echo ">>> Testando Nivel: \$WORKERS Workers"

    kubectl scale deployment benchmark-worker --replicas=\$WORKERS > /dev/null
    kubectl rollout status deployment/benchmark-worker --timeout=300s > /dev/null
    
    echo "   ... Coletando metricas (30s)..."
    sleep 30
    
    STATS=\$(kubectl top pods -l app=bench-worker --no-headers 2>/dev/null | awk '{cpu+=\$2; mem+=\$3} END {print cpu "," mem}')
    if [ -z "\$STATS" ]; then STATS="0,0"; fi
    
    LATENCY=\$(kubectl logs -l app=ric-platform --tail=100 | grep "DADO_CIENTIFICO" | awk -F'Latencia:' '{print \$2}' | awk -F'ms' '{print \$1}' | awk '{sum+=\$1; cnt++} END {if (cnt > 0) print sum/cnt; else print 0}')
    
    echo "   >>> RESULTADO: CPU/RAM: \$STATS | Latencia: \$LATENCY ms"
    echo "\$WORKERS,\$STATS,\$LATENCY" >> resultados.csv
done
echo "=== FIM. Dados salvos em 'resultados.csv' ==="