import matplotlib.pyplot as plt
import time
import json
import os
import math
import traceback
from metodos_numericos import gauss_pivoteamento, jacobi, gauss_seidel
from clustering import preprocess_logs, apply_clustering

print("=== INICIANDO AJUSTE DE CURVAS ===", flush=True)

# Função nova para cálculo de métricas de erro
def calcular_metricas_erro(y_true, y_pred):
    """Calcula MAE, RMSE e R²."""
    if len(y_true) != len(y_pred) or len(y_true) == 0:
        return {'mae': 0, 'rmse': 0, 'r2': 0}
    
    n = len(y_true)
    mae = sum(abs(a - b) for a, b in zip(y_true, y_pred)) / n
    mse = sum((a - b)**2 for a, b in zip(y_true, y_pred)) / n
    rmse = math.sqrt(mse)
    
    y_mean = sum(y_true) / n
    ss_total = sum((a - y_mean)**2 for a in y_true)
    ss_res = sum((a - b)**2 for a, b in zip(y_true, y_pred))
    
    r2 = 1 - (ss_res / ss_total) if ss_total != 0 else 0
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2
    }

# Função nova para validação dos resultados
def validar_resultados(resultados):
    """Realiza validação cruzada dos resultados obtidos."""
    relatorio = {
        'checks': [],
        'metodos_comparacao': {}
    }
    
    metodos = [m for m in resultados if resultados[m]['erro'] is None]
    
    if len(metodos) > 1:
        try:
            dif_rmse = abs(resultados[metodos[0]]['rmse'] - resultados[metodos[1]]['rmse'])
            relatorio['checks'].append({
                'check': 'Consistência entre métodos',
                'status': 'OK' if dif_rmse < 0.001 else 'ALERTA',
                'detalhes': f"Diferença de RMSE: {dif_rmse:.4f}"
            })
        except:
            pass
    
    for metodo in metodos:
        try:
            r2 = resultados[metodo]['r2']
            status = 'OK' if r2 > 0.7 else 'ALERTA'
            relatorio['checks'].append({
                'check': f'Qualidade do Ajuste ({metodo})',
                'status': status,
                'detalhes': f"R² = {r2:.4f} (>= 0.7 considerado bom)"
            })
        except:
            pass
    
    return relatorio

def carregar_dados():
    """Carrega dados do experimento atual"""
    experiment_id = os.getenv("EXPERIMENT_ID", "default")
    caminho = f"/app/input/{experiment_id}/requests_log.json"
    
    print(f"DEBUG: Buscando dados em {caminho}")
    
    try:
        with open(caminho, 'r') as f:
            logs = json.load(f)
        print(f"✓ Registros brutos: {len(logs)}")
        
        X_raw, clusters, y = preprocess_logs(logs)
        
        # Verificações detalhadas
        print(f"[DEBUG] Tamanho de X_raw: {len(X_raw)}")
        print(f"[DEBUG] Tamanho de clusters: {len(clusters)}")
        print(f"[DEBUG] Tamanho de y: {len(y)}")
        
        if len(X_raw) == 0:
            raise ValueError("Nenhum dado válido após pré-processamento")
        if len(X_raw) != len(clusters):
            raise ValueError(f"Inconsistência: X_raw ({len(X_raw)}) vs clusters ({len(clusters)})")
        if len(X_raw) != len(y):
            raise ValueError(f"Inconsistência: X_raw ({len(X_raw)}) vs y ({len(y)})")
            
        # Combinação correta das características
        X = [[x[0], x[1], clusters[i]] for i, x in enumerate(X_raw)]
        
        return X, y
        
    except Exception as e:
        print(f"ERRO: Falha ao carregar dados ({str(e)})")
        exit(1)

def ajuste_minimos_quadrados(X, y, metodo='gauss'):
    """
    Implementa ajuste por mínimos quadrados regularizado com múltiplos métodos numéricos.
    
    Metodologia:
    1. Construção da matriz de projeto com termo de bias
    2. Regularização adaptativa baseada na escala do problema
    3. Seleção de método numérico com tratamento de erros
    
    Parâmetros:
    X - Matriz de características [tamanho, taxa, cluster]
    y - Vetor de valores observados
    metodo - Algoritmo numérico a ser utilizado
    
    Retorna:
    theta - Parâmetros do modelo ajustado
    """
    n = len(X)
    if n < 4:
        raise ValueError("Número insuficiente de pontos para ajuste")
    
    # Construção da matriz de projeto aumentada
    A = [[row[0], row[1], row[2], 1] for row in X]
    
    # Construção do sistema normal equations
    ATA = [[0.0]*4 for _ in range(4)]
    ATB = [0.0]*4
    
    # Preenchimento eficiente das matrizes
    for i in range(4):
        for j in range(4):
            ATA[i][j] = sum(a[i] * a[j] for a in A)
        ATB[i] = sum(a[i] * y_val for a, y_val in zip(A, y))
    
    # Regularização adaptativa com controle de condicionamento
    lambda_reg_value = 1e-1 * n
    for i in range(4):
        ATA[i][i] += lambda_reg_value
        row_sum = sum(abs(ATA[i][j]) for j in range(4) if j != i)
        if ATA[i][i] < row_sum:
            ATA[i][i] += row_sum * 1.1  # Garante dominância diagonal
    
    # Seleção do método numérico com tratamento de erros
    try:
        if metodo == 'gauss':
            theta = gauss_pivoteamento(ATA, ATB)
        elif metodo == 'jacobi':
            theta = jacobi(ATA, ATB)
        elif metodo == 'gauss_seidel':
            theta = gauss_seidel(ATA, ATB)
        else:
            raise ValueError(f"Método desconhecido: {metodo}")
    except Exception as e:
        print(f"Erro no método {metodo}: {str(e)}")
        theta = [0, 0, 0, 0]
    
    return theta

def comparar_metodos(X, y):
    """
    Rotina de comparação sistemática de métodos numéricos.
    
    Metodologia:
    1. Execução controlada de cada método
    2. Validação rigorosa dos resultados
    3. Cálculo de métricas de desempenho comparativas
    4. Tratamento robusto de exceções
    
    Parâmetros:
    X - Dados de entrada
    y - Valores observados
    
    Retorna:
    resultados - Dicionário com métricas comparativas
    """
    metodos = ['gauss', 'jacobi', 'gauss_seidel']
    resultados = {}
    
    for metodo in metodos:
        try:
            # Validação inicial dos dados
            if not X or any(len(row) != 3 for row in X):
                raise ValueError("Dados de entrada inválidos")
            
            # Execução cronometrada
            inicio = time.time()
            theta = ajuste_minimos_quadrados(X, y, metodo)
            
            # Verificação de sanidade dos parâmetros
            if any(not math.isfinite(t) for t in theta):
                raise ValueError("Parâmetros não finitos detectados")
                
            if any(abs(t) > 1e6 for t in theta):
                raise ValueError("Parâmetros com magnitude excessiva")
            
            tempo = time.time() - inicio
            
            # Cálculo das predições com filtragem de valores inválidos
            y_pred = []
            y_true_valid = []
            invalid_count = 0
            
            for i, x_row in enumerate(X):
                try:
                    pred = (theta[0] * x_row[0] + 
                            theta[1] * x_row[1] + 
                            theta[2] * x_row[2] + 
                            theta[3])
                    
                    if not math.isfinite(pred):
                        invalid_count += 1
                        continue
                        
                    y_pred.append(pred)
                    y_true_valid.append(y[i])
                
                except Exception as e:
                    invalid_count += 1
            
            # Cálculo das métricas de erro
            metricas = calcular_metricas_erro(y_true_valid, y_pred)
            
            # Armazenamento dos resultados
            resultados[metodo] = {
                'theta': theta,
                'tempo': tempo,
                'mae': metricas['mae'],
                'rmse': metricas['rmse'],
                'r2': metricas['r2'],
                'pontos_validos': f"{len(y_pred)}/{len(X)}",
                'erro': None
            }
            
        except Exception as e:
            # Tratamento completo de erros
            resultados[metodo] = {
                'theta': [0, 0, 0, 0],
                'tempo': -1,
                'mae': -1,
                'rmse': -1,
                'r2': -1,
                'pontos_validos': "0/0",
                'erro': str(e)
            }
    
    return resultados

def plot_resultados(X, y, resultados, caminho_saida):
    """Salva os gráficos em arquivo."""
    plt.figure(figsize=(15, 10))
    
    metodos_validos = [m for m, res in resultados.items() if res['erro'] is None]
    if not metodos_validos:
        return
    
    # Gráfico 3D
    ax1 = plt.subplot(121, projection='3d')
    x1 = [row[0] for row in X]
    x2 = [row[1] for row in X]
    clusters = [row[2] for row in X]
    
    ax1.scatter(x1, x2, y, c=clusters, cmap='viridis')
    ax1.set_xlabel('Tamanho (KB)')
    ax1.set_ylabel('Req/min')
    ax1.set_zlabel('Latência (ms)')
    
    # Gráfico de Métricas
    ax2 = plt.subplot(122)
    metodos = [m for m in metodos_validos]
    rmses = [resultados[m]['rmse'] for m in metodos]
    maes = [resultados[m]['mae'] for m in metodos]
    
    bar_width = 0.35
    index = range(len(metodos))
    
    ax2.bar(index, rmses, bar_width, label='RMSE')
    ax2.bar([i + bar_width for i in index], maes, bar_width, label='MAE')
    
    ax2.set_xlabel('Métodos')
    ax2.set_ylabel('Valor')
    ax2.set_title('Comparação de Métricas de Erro')
    ax2.set_xticks([i + bar_width/2 for i in index])
    ax2.set_xticklabels(metodos)
    ax2.legend()
    
    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=150)
    plt.close()

if __name__ == "__main__":
    print("=== INICIANDO ANALYZER ===")
    experiment_id = os.getenv("EXPERIMENT_ID", "default")
    output_dir = os.path.join("/app/output", experiment_id)
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Carregar e processar dados
        X, y = carregar_dados()
        resultados = comparar_metodos(X, y)
        
        # Salvar métricas
        with open(f"{output_dir}/metricas.txt", 'w') as f:
            for metodo, res in resultados.items():
                f.write(
                    f"Método: {metodo}\n"
                    f"Parâmetros: {res['theta']}\n"
                    f"MAE: {res['mae']:.4f}\n"
                    f"RMSE: {res['rmse']:.4f}\n"
                    f"R²: {res['r2']:.4f}\n"
                    f"Pontos válidos: {res['pontos_validos']}\n"
                    f"Tempo: {res['tempo']:.4f}s\n\n"
                )
        
        # Gerar gráficos
        plot_resultados(X, y, resultados, f"{output_dir}/resultados.png")
        
        # Gerar e salvar relatório de validação
        relatorio = validar_resultados(resultados)
        with open(f"{output_dir}/relatorio_validacao.json", 'w') as f:
            json.dump(relatorio, f, indent=4)
        
        print(f"✅ Análise concluída! Resultados em {output_dir}")
        
    except Exception as e:
        print(f"⛔ ERRO CRÍTICO: {str(e)}")
        traceback.print_exc()
        exit(1)

print("Processamento finalizado com sucesso!", flush=True)