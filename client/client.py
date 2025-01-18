import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
import json  

URL = "http://server:5000/file"

TOTAL_REQUESTS = 500
CONCURRENT_CLIENTS = 50
LOG_FILE = "requests_log.json"

time.sleep(5) 

def generate_random_file_size():
    """Gera tamanhos de arquivos mais aleatórios, incluindo outliers."""
    base_size = random.uniform(10, 1000)  
    if random.random() < 0.05:
        return random.uniform(1000, 5000)  
    return round(base_size, 2)  

def simulate_request(client_id):
    """Simula uma requisição de cliente ao servidor."""
    size = generate_random_file_size()
    start_time = time.time()
    try:
        response = requests.get(f"{URL}/{int(size)}") 
        elapsed_time = time.time() - start_time
        log_entry = {
            "client_id": client_id,
            "file_size": size,
            "status_code": response.status_code,
            "elapsed_time": elapsed_time,
        }
        return log_entry
    except Exception as e:
        return {
            "client_id": client_id,
            "file_size": size,
            "status_code": None,
            "elapsed_time": None,
            "error": str(e),
        }

def save_logs(logs):
    """Salva os logs das requisições em JSON."""
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def main():
    """Executa múltiplas requisições simultaneamente."""
    logs = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_CLIENTS) as executor:
        for i, log_entry in enumerate(executor.map(simulate_request, range(TOTAL_REQUESTS))):
            logs.append(log_entry)
            print(f"Requisição {i + 1}/{TOTAL_REQUESTS} concluída: {log_entry}")
    save_logs(logs)
    print(f"Logs salvos em {LOG_FILE}")

if __name__ == "__main__":
    main()
