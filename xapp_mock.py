import time
import os
import urllib.request
import json

ric_host = os.getenv('RIC_HOST', 'localhost')
url = f"http://{ric_host}:8080"
print(f"--- xApp TRAFFIC STEERING INICIADO ---")

while True:
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())
        
        util = (data['load'] / data['capacity']) * 100
        decision = "HANDOVER" if util > 100 else "KEEP"
        
        report = {"id": "xapp-traffic", "decision": decision}
        data_bytes = json.dumps(report).encode('utf-8')
        req = urllib.request.Request(url, data=data_bytes, method="POST")
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req) as r: pass

    except: pass
    time.sleep(2)