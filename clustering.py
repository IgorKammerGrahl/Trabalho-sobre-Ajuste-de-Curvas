# Arquivo: pipeline_analise_trafego_com_visualizacao.py

import os
os.environ["LOKY_MAX_CPU_COUNT"] = "2"  # Define o número de núcleos para 2

import pandas as pd
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import matplotlib.pyplot as plt

def categorizar_fluxos(fluxos):
    """
    Categoriza os registros de fluxos como completos ou incompletos com base no protocolo e nas flags.
    """
    fluxos_categorizados = []
    for fluxo in fluxos:
        if fluxo["protocolo"] == "TCP":
            if "SYN" in fluxo["flags"] and "FIN" in fluxo["flags"]:
                fluxos_categorizados.append((fluxo, "completo"))
            else:
                fluxos_categorizados.append((fluxo, "incompleto"))
        elif fluxo["protocolo"] == "UDP":
            fluxos_categorizados.append((fluxo, "completo"))
    return fluxos_categorizados


def agrupar_fluxos_por_programa(fluxos):
    """
    Agrupa os fluxos por IP de destino, porta de destino e protocolo.
    """
    fluxos_agrupados = {}
    for fluxo in fluxos:
        chave = (fluxo["ip_destino"], fluxo["porta_destino"], fluxo["protocolo"])
        if chave not in fluxos_agrupados:
            fluxos_agrupados[chave] = []
        fluxos_agrupados[chave].append(fluxo)
    return fluxos_agrupados


def aplicar_clusterizacao(fluxos_agrupados):
    """
    Aplica o algoritmo Mini Batch K-Means para agrupar fluxos com demandas semelhantes.
    """
    resultados_cluster = {}
    for programa, fluxos in fluxos_agrupados.items():
        # Extrair dados de demanda (por exemplo, bytes enviados/recebidos)
        demandas = np.array([[fluxo["bytes_enviados"], fluxo["bytes_recebidos"]] for fluxo in fluxos])
        
        # Ajustar o número de clusters dinamicamente
        num_amostras = len(fluxos)
        num_clusters = min(3, num_amostras)  # Máximo de 3 clusters, mas não mais que o número de amostras
        
        if num_clusters > 1:  # Garantir pelo menos 2 amostras para realizar o clustering
            kmeans = MiniBatchKMeans(n_clusters=num_clusters, n_init=10, max_iter=300, random_state=42)
            kmeans.fit(demandas)
            
            # Armazenar resultados
            resultados_cluster[programa] = {
                "clusters": kmeans.labels_,
                "centros": kmeans.cluster_centers_,
                "demandas": demandas
            }
        else:
            # Se houver apenas uma ou duas amostras, evitar o clustering
            print(f"O programa {programa} tem dados insuficientes para clusterização.")
            resultados_cluster[programa] = {
                "clusters": [0] * num_amostras,
                "centros": np.mean(demandas, axis=0, keepdims=True),
                "demandas": demandas
            }
    return resultados_cluster


def visualizar_clusters(resultados_cluster):
    """
    Visualiza os resultados do clustering com gráficos de dispersão.
    """
    for programa, dados in resultados_cluster.items():
        demandas = dados["demandas"]
        labels = dados["clusters"]
        centros = dados["centros"]
        
        plt.figure(figsize=(8, 6))
        dispersao = plt.scatter(demandas[:, 0], demandas[:, 1], c=labels, cmap="viridis", alpha=0.7, label="Fluxos")
        plt.scatter(centros[:, 0], centros[:, 1], color="red", marker="x", s=100, label="Centros dos Clusters")
        plt.title(f"Clusterização para o Programa {programa}")
        plt.xlabel("Bytes Enviados")
        plt.ylabel("Bytes Recebidos")
        plt.legend()
        plt.grid(True)
        plt.show()


# Conjunto de dados de exemplo: Substitua pelos registros reais de fluxos
fluxos = [
    {"protocolo": "TCP", "flags": ["SYN", "FIN"], "ip_destino": "1.1.1.2", "porta_destino": 8000, "bytes_enviados": 761070, "bytes_recebidos": 9727},
    {"protocolo": "TCP", "flags": ["SYN"], "ip_destino": "1.1.1.2", "porta_destino": 8000, "bytes_enviados": 1013472, "bytes_recebidos": 12040},
    {"protocolo": "TCP", "flags": ["SYN", "FIN"], "ip_destino": "1.1.1.2", "porta_destino": 8000, "bytes_enviados": 1775569, "bytes_recebidos": 22170},
    {"protocolo": "TCP", "flags": ["SYN", "FIN"], "ip_destino": "1.1.1.2", "porta_destino": 9000, "bytes_enviados": 409906, "bytes_recebidos": 7330},
    {"protocolo": "TCP", "flags": ["SYN"], "ip_destino": "1.1.1.2", "porta_destino": 9000, "bytes_enviados": 817707, "bytes_recebidos": 13326},
    {"protocolo": "TCP", "flags": ["SYN", "FIN"], "ip_destino": "1.1.1.2", "porta_destino": 9000, "bytes_enviados": 1633532, "bytes_recebidos": 25436},
]

# Execução do pipeline
fluxos_categorizados = categorizar_fluxos(fluxos)
fluxos_completos = [fluxo for fluxo, status in fluxos_categorizados if status == "completo"]
fluxos_agrupados = agrupar_fluxos_por_programa(fluxos_completos)
resultados_cluster = aplicar_clusterizacao(fluxos_agrupados)

# Visualizar os resultados do clustering
visualizar_clusters(resultados_cluster)
