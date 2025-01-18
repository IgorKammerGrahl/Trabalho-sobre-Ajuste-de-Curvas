from flask import Flask, request, send_file
import json
import os
from datetime import datetime
import random

app = Flask(__name__)

logs = []
LOG_FILE = "logs.json"

def save_logs():
    """Salva os logs em formato JSON."""
    print("Salvando logs:", logs)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def clean_files():
    """Remove arquivos antigos na pasta 'files'."""
    folder = "files"
    if os.path.exists(folder):
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))

@app.route('/file/<int:size>', methods=['GET'])
def send_file_route(size):
    global logs

    varied_size = size + random.randint(-int(size * 0.1), int(size * 0.1))  
    file_path = f"files/{varied_size}kb.txt"
    os.makedirs("files", exist_ok=True)

    if not os.path.exists(file_path) or os.path.getsize(file_path) != varied_size * 1024:
        with open(file_path, "w") as f:
            f.write("0" * (varied_size * 1024))

    log_entry = {
        "ip": request.remote_addr,
        "size": varied_size,
        "timestamp": datetime.now().isoformat()
    }
    logs.append(log_entry)
    save_logs()

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    clean_files()
    app.run(host="0.0.0.0", port=5000)
