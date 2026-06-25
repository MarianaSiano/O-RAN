import time
import os
import json
import socket
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# --- Configurações ---
RIC_HOST = os.getenv('RIC_HOST', 'localhost')
MY_ID = socket.gethostname()
BASE_URL = f"http://{RIC_HOST}:8080"
POLL_INTERVAL = 1.0  # segundos
REQUEST_TIMEOUT = 2  # segundos

# --- logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(f"benchmark-{MY_ID}")

def fetch_data() -> dict | None:
    """Faz GET no endpoint e retorna o JSON decodificado."""
    req = Request(BASE_URL, method="GET")
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read().decode())

def post_report(report: dict) -> None:
    """Envia o relatório de latência via POST."""
    payload = json.dumps(report).encode("utf-8")
    req = Request(BASE_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    with urlopen(req, timeout=REQUEST_TIMEOUT):
        pass

def benchmark_loop() -> None:
    """Loop principal de benchmark a 1 Hz."""
    logger.info("Iniciando benchmark — target=%s | id=%s", BASE_URL, MY_ID)

    while True:
        tick = time.monotonic()

        try:
            # T0 → GET
            start = time.perf_counter()
            data = fetch_data()
            latency_ms = (time.perf_counter() - start) * 1000

            # Monta e envia o relatório
            report = {
                "id": MY_ID,
                "latency_ms": round(latency_ms, 2),
                "type": "benchmark",
            }
            post_report(report)

            logger.info(
                "GET OK | latência=%.2f ms | payload=%s",
                latency_ms, data,
            )

        except HTTPError as e:
            logger.warning("HTTP %d: %s", e.code, e.reason)
        except URLError as e:
            logger.warning("URL error: %s", e.reason)
        except (OSError, json.JSONDecodeError, ValueError) as e:
            logger.error("Erro inesperado: %s", e)

        # Dorme o restante do intervalo (1 Hz preciso)
        elapsed = time.monotonic() - tick
        sleep_time = POLL_INTERVAL - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

if __name__ == "__main__":
    benchmark_loop()