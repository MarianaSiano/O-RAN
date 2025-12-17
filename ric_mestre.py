import http.server
import socketserver
import random
import json
import threading

PORT = 8080

class ThreadingHTTPServer (socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

class TrafficHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return # Limpa logs de acesso

    def do_GET(self):
        # Envia dados da rede (Simulação E2)
        response = {
            "load": random.randint(50, 150),
            "capacity": 100
        }
        self.send_response(200)
        self.send_head('Content-type', 'application / json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # Recebe ação dos Apps
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length).decode())

        # Loga para o script de benchmark capturar
        if 'latency_ms' in data:
            print(f"[METRICA] App:{data['id']} | Latencia:{data['latency_ms']:.2f}ms")

        self.send_response(200)
        self.end_headers()

print(f"--- RIC MESTRE RODANDO (PORTA {PORT}) ---")
with ThreadingHTTPServer(("", PORT), TrafficHandler) as httpd:
    httpd.serve_forever()