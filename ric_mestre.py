import http.server
import socketserver
import random
import json
import threading

PORT = 8080
POLICY_ENERGY_SAVING = False

class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

class TrafficHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        global POLICY_ENERGY_SAVING
        capacity = 80 if POLICY_ENERGY_SAVING else 100

        response = {
            "load": random.randint(50, 150),
            "capacity": capacity,
            "policy_active": POLICY_ENERGY_SAVING
        }

        self.send_response(200)

        # CORRIGIDO AQUI: É send_header (com R no final)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_PUT(self):
        global POLICY_ENERGY_SAVING
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length).decode())

        if data.get('type') == 'A1_POLICY':
            POLICY_ENERGY_SAVING = data.get('value', False)
            print(f"[INTERFACE A1] Nova Politica Recebida: Economia={POLICY_ENERGY_SAVING}")

        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length).decode())

        if 'latency_ms' in data:
            print(f"[DADO_CIENTIFICO] App:{data['id']} | Latencia:{data['latency_ms']:.2f}ms")

        self.send_response(200)
        self.end_headers()

print(f"--- RIC MESTRE RODANDO (PORTA {PORT}) ---")
print(f"--- Interfaces A1 (PUT) e E2 (GET/POST) Ativas ---")
with ThreadingHTTPServer(("", PORT), TrafficHandler) as httpd:
    httpd.serve_forever()