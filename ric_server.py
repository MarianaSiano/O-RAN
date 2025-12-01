import http.server
import socketserver
import random
import json
import time

PORT = 8080

class TrafficHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Gera um valor de tráfego sintético entre 0 e 100 Mbps
        traffic_volume = random.randint(10, 150)
        
        # Cria a resposta JSON
        response = {
            "cell_id": "gnb-001",
            "traffic_load_mbps": traffic_volume,
            "connected_users": random.randint(5, 50),
            "status": "overload" if traffic_volume > 100 else "normal"
        }

        # Envia a resposta para quem perguntou (xApp)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

print(f"--- RIC (MASTER) INICIADO ---")
print(f"Simulando dados de telemetria E2 na porta {PORT}")

# Inicia o servidor para sempre
with socketserver.TCPServer (("", PORT), TrafficHandler) as httpd:
    httpd.serve_forever()