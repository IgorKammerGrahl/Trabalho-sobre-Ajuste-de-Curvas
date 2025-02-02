# wait_for_logs.py
import os
import time

LOG_PATH = '/app/input/requests_log.json'  # Path corrigido
TIMEOUT = 300
INTERVAL = 2

def main():
    start_time = time.time()
    last_size = -1
    
    while True:
        if os.path.exists(LOG_PATH):
            current_size = os.path.getsize(LOG_PATH)
            if current_size > last_size:
                print(f"Arquivo detectado (Tamanho: {current_size} bytes)")
                last_size = current_size
                time.sleep(INTERVAL)  # Espera estabilização
            else:
                print("✓ Arquivo estável. Iniciando análise...")
                return
        else:
            elapsed = time.time() - start_time
            if elapsed > TIMEOUT:
                raise TimeoutError(f"Timeout após {TIMEOUT}s")
            print(f"Aguardando... {elapsed:.1f}s")
            time.sleep(INTERVAL)

if __name__ == "__main__":
    main()