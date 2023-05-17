import threading
from queue import Queue
import requests
from flask import Flask, jsonify, request
import socket
import datetime
import pytz

url = "your discord webhook url"

app = Flask(__name__)

def port_scan(port, q, ip_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((ip_address, port))
    if result == 0:
        q.put(port)

@app.route('/portscan/<string:ip_address>', methods=['GET'])
def get_open_ports(ip_address):
    start_port = request.args.get('start_port', default=1, type=int)
    end_port = request.args.get('end_port', default=1024, type=int)
    q = Queue()
    open_ports = []
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=port_scan, args=(port, q, ip_address))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    while not q.empty():
        open_ports.append(q.get())
        est_timezone = pytz.timezone("America/New_York")
        est_time = datetime.datetime.now(est_timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

    req_ip = request.remote_addr
    sendToDiscord = f"""
**```User IP: {req_ip}
Scanning IP: {ip_address}
Open Ports: {open_ports}
Request made at: {est_time}
```**"""

    r=requests.post(url, data={"content": sendToDiscord })
    return jsonify({'open_ports': open_ports})

if __name__ == '__main__':
    app.run(debug=True)
