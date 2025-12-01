import http.server
import socketserver
import random
import json
import threading

PORT = 8080

class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

class TrafficHandler(http.server.SimpleHTTPRequestHandler):
    # Desativa logs de acesso padrão para não poluir o terminal
    def log_message(self, format, *args):
        return

    def do_GET(self):
        # 1. Gera dado sintético
        response = {
            "load": random.randint(50, 150),
            "capacity": 100
        }
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # 2. Recebe o processamento do Worker
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length).decode())
        
        # Loga apenas o resumo para métrica
        print(f"[METRICA] Worker:{data['id']} | Latencia:{data['latency_ms']:.2f}ms | Decisao:{data['decision']}")
        
        self.send_response(200)
        self.end_headers()

print(f"--- RIC MESTRE RODANDO (PORTA {PORT}) ---")
with ThreadingHTTPServer(("", PORT), TrafficHandler) as httpd:
    httpd.serve_forever()