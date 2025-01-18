import json
import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import os

os.environ["LOKY_MAX_CPU_COUNT"] = "4"

def load_logs(log_file):
    """Carrega os logs do arquivo JSON."""
    with open(log_file, "r") as f:
        return json.load(f)

def preprocess_logs(logs):
    """Transforma os logs em um array NumPy para clustering."""
    data = []
    for log in logs:
        try:
            ip_last_byte = int(log["ip"].split(".")[-1])
            data.append([float(log["size"]), ip_last_byte])
        except (KeyError, ValueError) as e:
            print(f"Erro ao processar log {log}: {e}")
    if not data:
        print("Nenhum dado válido para realizar o clustering.")
        return None
    return np.array(data, dtype=float)

def apply_clustering(data, n_clusters=3):
    """Aplica o algoritmo MiniBatchKMeans para clustering."""
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)
    
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, max_iter=300)
    kmeans.fit(data_scaled)
    return kmeans, data_scaled, scaler

def visualize_clusters(data, kmeans, original_data, add_jitter=True):
    """Visualiza os resultados do clustering."""
    if add_jitter:
        jitter = np.random.uniform(-0.5, 0.5, size=original_data[:, 1].shape)
        original_data[:, 1] += jitter

    plt.figure(figsize=(12, 6))
    plt.scatter(original_data[:, 0], original_data[:, 1], 
                c=kmeans.labels_, cmap="viridis", alpha=0.7, label="Clusters")
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
                color="red", marker="x", s=150, label="Centers")
    plt.title("Clustering dos Fluxos")
    plt.xlabel("Tamanho do Arquivo (KB)")
    plt.ylabel("Último Byte do IP (com jitter)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    log_file = "logs.json"  
    logs = load_logs(log_file)
    data = preprocess_logs(logs)

    if data is not None and len(data) > 0:
        kmeans, data_scaled, scaler = apply_clustering(data, n_clusters=4)  
        visualize_clusters(data, kmeans, data)
    else:
        print("Nenhum dado válido para realizar o clustering.")
