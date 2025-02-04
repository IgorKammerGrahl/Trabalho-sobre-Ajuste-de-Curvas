import json
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os
import time

os.environ["LOKY_MAX_CPU_COUNT"] = "4"

print("=== INICIANDO CLUSTERING ===", flush=True)

def load_logs(log_file='/app/input/requests_log.json'):
    max_retries = 20
    retries = 0
    
    while retries < max_retries:
        try:
            with open(log_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Aguardando logs... (Tentativa {retries+1}/{max_retries})", flush=True)
            retries += 1
            time.sleep(3)
    
    raise FileNotFoundError("Arquivo de logs não encontrado após todas as tentativas")

def preprocess_logs(logs):
    """
    Pré-processamento de logs com validação robusta e clusterização adaptativa.
    
    Metodologia:
    1. Limpeza e normalização de dados
    2. Validação de limites físicos
    3. Clusterização dinâmica baseada na densidade dos dados
    
    Parâmetros:
    logs - Lista de registros brutos
    
    Retorna:
    X - Dados pré-processados [tamanho, latência]
    clusters - Rótulos de cluster atribuídos
    y - Valores de latência processados
    """
    X = []
    y = []
    invalid_count = 0

    for log in logs:
        try:
            # Validação e normalização robusta
            fs = log.get('file_size', 0)
            et = log.get('elapsed_time', 0)
            
            # Normalização defensiva
            size = float(fs) if fs not in [None, ""] else 0.1
            latency = float(et) if et not in [None, ""] else 0.001
            
            # Aplicação de limites físicos realistas
            size = max(0.1, min(size, 100000))  # Entre 0.1KB e 100MB
            latency = max(0.001, min(latency, 300))  # Entre 1ms e 5min
            
            X.append([size, latency])
            y.append(latency)
            
        except Exception as e:
            invalid_count += 1
            
    # Clusterização adaptativa por densidade
    if len(X) < 10:
        return [], [], y
    
    try:
        # Determinação dinâmica do número de clusters
        n_clusters = min(5, len(X)//100)
        kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            n_init=10,
            random_state=42
        )
        clusters = kmeans.fit_predict(X)
        return X, clusters.tolist(), y
    except Exception as e:
        return X, [0]*len(X), y
    
def apply_clustering(X):
    """Clustering otimizado para grandes datasets"""
    from sklearn.cluster import MiniBatchKMeans
    
    if len(X) < 10:
        return [0] * len(X)  # Retorna cluster único
        
    # Determina número máximo de clusters
    n_clusters = min(5, len(X)//10)  # Máximo 5 clusters
    
    try:
        kmeans = MiniBatchKMeans(
            n_clusters=n_clusters,
            n_init=10,
            batch_size=100
        )
        return kmeans.fit_predict(X).tolist()
    except Exception as e:
        print(f"Erro no clustering: {str(e)}")
        return [0] * len(X)

if __name__ == "__main__":
    try:
        logs = load_logs()
        if not logs:
            raise ValueError("Arquivo de logs vazio!")
            
        data = preprocess_logs(logs)
        
        if data is None or len(data) == 0:
            raise ValueError("Dados pré-processados inválidos!")
                
    except Exception as e:
        print(f"ERRO CRÍTICO: {str(e)}", flush=True)
        exit(1)

print("Processamento concluído!", flush=True)