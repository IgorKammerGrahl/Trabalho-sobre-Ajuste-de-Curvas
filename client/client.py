import os
import time
import random
import requests
import json
from concurrent.futures import ThreadPoolExecutor

# Configurações via variáveis de ambiente com validação
try:
    TOTAL_REQUESTS = int(os.getenv("TOTAL_REQS", "500"))
    CONCURRENT_CLIENTS = int(os.getenv("CONCURRENT_CLIENTS", "50"))
    EXPERIMENT_ID = os.getenv("EXPERIMENT_ID", "default")
except ValueError as e:
    print(f"ERRO: Variável de ambiente inválida - {str(e)}")
    exit(1)

URL = "http://server:5000/file"
LOG_DIR = f"/app/output/{EXPERIMENT_ID}"
LOG_FILE = f"{LOG_DIR}/requests_log.json"

def generate_file_size():
    """Gera tamanhos de arquivo com distribuição multimodal"""
    try:
        # Distribuições ajustadas para maior variabilidade
        modes = [
            {'type': 'normal', 'mean': 300, 'std': 100, 'prob': 0.5},
            {'type': 'uniform', 'min': 10, 'max': 2000, 'prob': 0.3},
            {'type': 'exponential', 'scale': 1000, 'prob': 0.2}
        ]
        
        choice = random.choices(
            modes, 
            weights=[m['prob'] for m in modes]
        )[0]
        
        if choice['type'] == 'normal':
            return abs(round(random.gauss(choice['mean'], choice['std']), 2))
        elif choice['type'] == 'uniform':
            return round(random.uniform(choice['min'], choice['max']), 2)
        else:
            return round(random.expovariate(1/choice['scale']), 2)
            
    except Exception as e:
        print(f"ERRO na geração de tamanho: {str(e)}")
        return round(random.uniform(10, 1000), 2)

def simulate_request(client_id):
    """Executa uma requisição com tratamento robusto de erros"""
    try:
        size = max(0.1, generate_file_size())  # Garante tamanho mínimo de 0.1 KB
        start_time = time.time()
        
        response = requests.get(f"{URL}/{int(size)}", timeout=3)
        elapsed = max(0.001, round(time.time() - start_time, 4))  # Tempo mínimo de 0.001s
        
        return {
            "client_id": client_id,
            "file_size": size,
            "status_code": response.status_code,
            "elapsed_time": elapsed,
            "error": None
        }
    except Exception as e:
        return {
            "client_id": client_id,
            "file_size": 0.1,  # Valor padrão seguro
            "status_code": 500,
            "elapsed_time": 0.001,  # Valor padrão seguro
            "error": str(e)
        }

def save_logs(logs):
    """Salva logs com verificação de integridade"""
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
            
        print(f"✓ Logs salvos em {LOG_FILE}")
        return True
        
    except Exception as e:
        print(f"✗ ERRO ao salvar logs: {str(e)}")
        return False

def main():
    """Fluxo principal com monitoramento detalhado"""
    print(f"\n=== INICIANDO CLIENTE ===")
    print(f"Experiment ID: {EXPERIMENT_ID}")
    print(f"Requests: {TOTAL_REQUESTS}")
    print(f"Concurrency: {CONCURRENT_CLIENTS}\n")
    
    logs = []
    
    with ThreadPoolExecutor(max_workers=CONCURRENT_CLIENTS) as executor:
        futures = [executor.submit(simulate_request, i) for i in range(TOTAL_REQUESTS)]
        
        for i, future in enumerate(futures):
            try:
                result = future.result(timeout=5)
                logs.append(result)
                
                if (i+1) % 50 == 0:
                    print(f"▶ Progresso: {i+1}/{TOTAL_REQUESTS}")
                    
            except Exception as e:
                print(f"⚠ ERRO na requisição {i+1}: {str(e)}")
                logs.append({
                    "client_id": i,
                    "error": str(e)
                })
    
    if save_logs(logs):
        print(f"\n=== ESTATÍSTICAS ===")
        success = sum(1 for l in logs if l.get('status_code') == 200)
        errors = sum(1 for l in logs if l.get('error'))
        
        print(f"Requisições bem-sucedidas: {success}/{TOTAL_REQUESTS}")
        print(f"Erros registrados: {errors}")
        
        if logs:
            tamanho_medio = round(
                sum(l['file_size'] for l in logs if l['file_size'] is not None) / 
                max(1, TOTAL_REQUESTS), 
                2
            )
            print(f"Tamanho médio: {tamanho_medio} KB")
        else:
            print("Nenhum dado disponível para cálculo do tamanho médio")
    else:
        print("\n✗ A análise não pode ser completada devido a erros de armazenamento")


if __name__ == "__main__":
    main()