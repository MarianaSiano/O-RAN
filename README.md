# O-RAN

## Rodar a Arquitetura O-RAN

Para rodar a arquitetura O-RAN, está no PDF que está junto do repositório

## Como Rodar o Ataque

### Opção 1: Rodar como um pod dentro do Cluster

````bash
# Salva o script como atacar_oran.py

# Cria um pod temporario para executar o ataque
kubectl run attacker-pod --image=python:3.11-slim --restart=Never -- /bin/sh -c "sleep 3600"

# Copia o script para o pod
kubectl cp atacar_oran.py attacker-pod:/atacar_oran.py

# Executa o ataque
kubectl exec -it attacker-pod -- python /atacar_oran.py ric-service 8080

# Para ver os logs do ataque em outro terminal:
kubectl logs -f attacker-pod
````

### Opção 2: Rodar fora do cluster (na sua máquina com acesso ao service)

````bash
# Se tiver o service exposto via NodePort ou port-forward:
kubectl port-forward svc/ric-service 8080:8080 &

# Em outro terminal:
python3 atacar_oran.py localhost 8080
````

### Opção 3: Usar um pod Debian/Ubuntu dentro do cluster

````bash
# Cria um pod com ferramentas de rede
kubectl run pentest-pod --image=kalilinux/kali-rolling --restart=Never -- /bin/bash -c "apt update && apt install -y python3 netcat-traditional && sleep 3600"

# Copia o script
kubectl cp atacar_oran.py pentest-pod:/atacar_oran.py

# Roda
kubectl exec -it pentest-pod -- python3 /atacar_oran.py ric-service 8080
````

## O que cada ataque faz (monitore nos logs)

Enquanto o ataque roda, abra 3 terminais para ver o efeito

````bash
# Terminal 1 - Logs do RIC (vai mostrar os ataques chegando)
kubectl logs -f -l app=ric-platform

# Terminal 2 - Logs do xApp (vai mostrar decisoes HANDOVER loucas)
kubectl logs -f -l app=xapp-functional

# Terminal 3 - Logs do rApp (vai mostrar politica mudando sozinha)
kubectl logs -f -l app=rapp
````

No RIC você verá:

````bash
[DADO_CIENTIFICO] App:worker-comprometido-847 | Latencia:3.21ms
[DADO_CIENTIFICO] App:bench-worker-2 | Latencia:1234.56ms  <-- ENVENENADO
[INTERFACE A1] Nova Politica Recebida: Economia=True
[INTERFACE A1] Nova Politica Recebida: Economia=False  <-- ALTERNANDO RAPIDO
````

No xApp você verá:

````bash
HANDOVER (utilizacao 247% - IMPOSSIVEL!)
HANDOVER (utilizacao 253%)
HANDOVER (utilizacao 231%)  <-- OVERLOAD FABRICATE DETECTAVEL
````

No rApp você verá:

````bash
Policy alternando a cada 2s sem controle legitimo
Capacity caindo para 50 sem autorizacao
````