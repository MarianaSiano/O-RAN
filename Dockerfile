# =============================================================================
# Dockerfile — RIC Platform Benchmark Workers
# Construção: docker build -t ric-benchmark:latest .
# =============================================================================

# --- Estágio base ---
FROM python:3.12-slim AS base

# Evita criar arquivos .pyc e buffer de stdout (já que CMD usa -u)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copia dependências primeiro (cache layer separado)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# --- Estágio de produção (multi-stage) ---
FROM python:3.12-slim

# Metadados da imagem (OCI labels)
LABEL org.opencontainers.image.title="RIC Platform Benchmark" \
    org.opencontainers.image.description="Worker de benchmark para testes de escalabilidade ORAN" \
    org.opencontainers.image.version="1.0.0" \
    org.opencontainers.image.created="2026-06-25" \
    org.opencontainers.image.source="https://github.com/seu-org/ric-benchmark" \
    org.opencontainers.image.licenses="MIT"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RIC_HOST=${RIC_HOST:-localhost} \
    PYTHONPATH=/app

WORKDIR /app

# Copia apenas o runtime do estágio base
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

# Cria usuário não-root e grupo
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --ingroup appgroup --no-create-home appuser \
    && chown -R appuser:appgroup /app

# Copia os scripts com ownership correto
COPY --chown=appuser:appgroup \
    ric_mestre.py \
    xapp_mock.py \
    app_worker.py \
    rapp_mock.py \
    ./

# Healthcheck: verifica se o processo responde
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/ric_mestre.py') else 1)"

# Sinal de parada limpo
STOPSIGNAL SIGTERM

# Muda para usuário não-root
USER appuser:appgroup

# Comando padrão
CMD ["python", "-u", "ric_mestre.py"]