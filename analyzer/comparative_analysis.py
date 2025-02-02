import json
import matplotlib.pyplot as plt
import glob
import os
from utils import parse_metrics

def load_results(experiment_id):
    path = f"/app/input/{experiment_id}/requests_log.json"  
    with open(path) as f:
        return json.load(f)

def analyze_current_experiment(experiment_id):
    output_dir = f"/app/output/{experiment_id}"
    os.makedirs(output_dir, exist_ok=True)  # <-- Adicione esta linha
    
    data = load_results(experiment_id)
    
    plt.figure(figsize=(12,6))
    plt.hist([r['elapsed_time'] for r in data], bins=50)
    plt.savefig(f'{output_dir}/response_times.png')  # <-- Caminho corrigido
    plt.close()

def load_all_metrics():
    all_metrics = {}
    for exp_dir in glob.glob("/app/output/*"):  # Todos experimentos
        exp_id = os.path.basename(exp_dir)
        with open(f"{exp_dir}/metricas.txt") as f:
            all_metrics[exp_id] = parse_metrics(f.read())
    return all_metrics

def generate_comparative_plots(metrics):
    # Lógica para comparar todos os experimentos
    # Ex: plt.plot(exp1_residues, exp2_residues...)
    plt.savefig("/app/output/comparative_results.png")

if __name__ == "__main__":
    experiment_id = os.getenv("EXPERIMENT_ID", "default")
    analyze_current_experiment(experiment_id)