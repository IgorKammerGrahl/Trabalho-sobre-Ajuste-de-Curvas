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
    """Processa logs e aplica clustering."""
    X = []
    y = []
    invalid_count = 0

    for log in logs:
        try:
            # Validação mais tolerante
            fs = log.get('file_size', 0)
            et = log.get('elapsed_time', 0)
            
            size = float(fs) if fs not in [None, ""] else 0.1
            latency = float(et) if et not in [None, ""] else 0.001
            
            # Limites físicos realistas
            size = max(0.1, min(size, 100000))  # Entre 0.1KB e 100MB
            latency = max(0.001, min(latency, 300))  # Entre 1ms e 5min
            
            X.append([size, latency])
            y.append(latency)
            
        except Exception as e:
            invalid_count += 1
            
    print(f"✓ Dados válidos: {len(X)}/{len(logs)}")
    print(f"Registros ajustados: {invalid_count}")

    if len(X) < 10:  # Reduzido o limite mínimo
        return [], [], y
    
    # Clusterização adaptativa
    try:
        n_clusters = min(5, len(X)//100)
        kmeans = MiniBatchKMeans(n_clusters=n_clusters, n_init=10)
        clusters = kmeans.fit_predict(X)
        return X, clusters.tolist(), y
    except Exception as e:
        print(f"Erro no clustering: {str(e)}")
        return X, [0]*len(X), y  # Cluster padrão
    
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
        
        # ... resto do código
        
    except Exception as e:
        print(f"ERRO CRÍTICO: {str(e)}", flush=True)
        exit(1)

print("Processamento concluído!", flush=True)