import matplotlib.pyplot as plt
import time
import json
import os
import math
from metodos_numericos import gauss_pivoteamento, jacobi, gauss_seidel
from clustering import preprocess_logs, apply_clustering

print("=== INICIANDO AJUSTE DE CURVAS ===", flush=True)

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
    """Ajuste com 4 parâmetros (incluindo cluster)."""
    if isinstance(X, (list, tuple)):
        X = [list(row) for row in X]
    if isinstance(y, (list, tuple)):
        y = list(y)
    
    n = len(X)
    if n < 4:
        raise ValueError("Número insuficiente de pontos para ajuste")
    
    # Validação de dimensionalidade
    if any(len(row) != 3 for row in X):
        raise ValueError("Cada elemento de X deve ter 3 características")
    
    # Matriz de projeto: [tamanho, taxa, cluster, 1]
    A = [[row[0], row[1], row[2], 1] for row in X]
    
    # Cálculo de ATA e ATB
    ATA = [[0.0]*4 for _ in range(4)]
    ATB = [0.0]*4
    
    # Preenchimento das matrizes
    for i in range(4):
        for j in range(4):
            ATA[i][j] = sum(a[i] * a[j] for a in A)
        ATB[i] = sum(a[i] * y_val for a, y_val in zip(A, y))
    
    # Regularização adaptativa (sem numpy)
    lambda_reg_value = 1e-1 * n  # Volte ao valor original mas com verificação
    min_diagonal = 1e-4 * n
    for i in range(4):
        ATA[i][i] += lambda_reg_value
        # Garante dominância diagonal
        row_sum = sum(abs(ATA[i][j]) for j in range(4) if j != i)
        if ATA[i][i] < row_sum:
            ATA[i][i] += row_sum * 1.1  # Torna diagonal dominante
    
    # Resolver sistema
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
        theta = [0, 0, 0, 0]  # 4 elementos para os 4 parâmetros
    
    return theta


def is_finite(x):
    # Verifica se x não é NaN (já que NaN != NaN) e se não é infinito
    return x == x and x != float('inf') and x != -float('inf')

def comparar_metodos(X, y):
    """Compara os métodos numéricos para ajuste de curvas."""
    metodos = ['gauss', 'jacobi', 'gauss_seidel']
    resultados = {}
    
    for metodo in metodos:
        try:
            # Validação preliminar dos dados
            if not X or any(len(row) != 3 for row in X):
                raise ValueError("Dados de entrada inválidos ou inconsistentes")
            
            inicio = time.time()
            theta = ajuste_minimos_quadrados(X, y, metodo)
            
            # Verificação numérica rigorosa
            if any(not math.isfinite(t) for t in theta):
                invalid = [t for t in theta if not math.isfinite(t)]
                raise ValueError(f"Parâmetros não finitos detectados: {invalid}")
                
            # Verificação de magnitude dos parâmetros
            if any(abs(t) > 1e6 for t in theta):
                large_params = [t for t in theta if abs(t) > 1e6]
                raise ValueError(f"Parâmetros com magnitude excessiva: {large_params}")
            
            tempo = time.time() - inicio
            
            # Cálculo do resíduo com tratamento seguro
            residuo = 0.0
            count = 0
            invalid_predictions = 0
            
            for i, x_row in enumerate(X):
                try:
                    # Verificação da estrutura dos dados
                    if len(x_row) != 3:
                        raise ValueError(f"Elemento X[{i}] com dimensão inválida: {len(x_row)}")
                    
                    pred = (theta[0] * x_row[0] + 
                            theta[1] * x_row[1] + 
                            theta[2] * x_row[2] + 
                            theta[3])
                    
                    # Verificação da predição
                    if not math.isfinite(pred):
                        invalid_predictions += 1
                        continue
                        
                    residuo += (y[i] - pred)**2
                    count += 1
                
                except (IndexError, TypeError) as e:
                    print(f"Erro no ponto {i}: {str(e)}")
                    continue
            
            if invalid_predictions > 0:
                print(f"Aviso: {invalid_predictions} predições inválidas descartadas")
                
            if count < len(X)//2:
                raise ValueError(f"Mais de 50% dos pontos inválidos ({count}/{len(X)} válidos)")
                
            if count == 0:
                raise ValueError("Nenhum ponto válido para cálculo do resíduo")
                
            residuo = (residuo/count)**0.5  # RMSE normalizado
            
            resultados[metodo] = {
                'theta': theta,
                'tempo': tempo,
                'residuo': residuo,
                'pontos_validos': f"{count}/{len(X)}"
            }
            
        except Exception as e:
            print(f"Erro crítico em {metodo}: {str(e)}")
            traceback.print_exc()
            resultados[metodo] = {
                'theta': [0, 0, 0, 0],
                'tempo': -1,
                'residuo': -1,
                'erro': str(e)
            }
    
    return resultados

def plot_resultados(X, y, resultados, caminho_saida='/app/output/resultados.png'):
    """Salva os gráficos em arquivo usando apenas listas nativas."""
    plt.figure(figsize=(15, 10))
    
    # Filtrar métodos válidos
    metodos_validos = [m for m, res in resultados.items() if res['residuo'] > 0]
    if not metodos_validos:
        print("Nenhum método válido para plotar!")
        return
    
    # Dados reais
    x1 = [row[0] for row in X]
    x2 = [row[1] for row in X]
    clusters = [row[2] for row in X]
    
    # Criar subplots
    ax1 = plt.subplot(121, projection='3d')
    ax2 = plt.subplot(122)

    # Funções auxiliares sem numpy
    def linspace(start, stop, n):
        return [start + (stop - start) * i / (n-1) for i in range(n)]
    
    def meshgrid(x_vals, y_vals):
        return [[x for _ in y_vals] for x in x_vals], [[y for y in y_vals] for _ in x_vals]
    
    # Gerar superfícies manualmente
    for metodo in metodos_validos:
        res = resultados[metodo]
        X1 = linspace(min(x1), max(x1), 20)
        X2 = linspace(min(x2), max(x2), 20)
        grid_x, grid_y = meshgrid(X1, X2)
        
        # Calcular Z manualmente
        Z = []
        for i in range(len(grid_x)):
            z_row = []
            for j in range(len(grid_x[0])):
                z = (res['theta'][0] * grid_x[i][j] + 
                     res['theta'][1] * grid_y[i][j] + 
                     res['theta'][2] * 0 +  # Cluster fixo para simplificar
                     res['theta'][3])
                z_row.append(z)
            Z.append(z_row)
        
        # Gráfico de dispersão 2D:
        ax1.scatter(x1, x2, y, c=clusters, cmap='viridis')
        ax1.set_xlabel('Tamanho (KB)')
        ax1.set_ylabel('Req/min')

    ax1.scatter(x1, x2, y, c=clusters, cmap='viridis')
    ax1.set_xlabel('Tamanho (KB)')
    ax1.set_ylabel('Req/min')
    ax1.set_zlabel('Latência (ms)')

    # Gráfico 2D
    tempos = [resultados[m]['tempo'] for m in metodos_validos]
    ax2.bar(metodos_validos, tempos, color=['blue','green','orange'])
    ax2.set_title('Tempo por Método')
    ax2.set_ylabel('Segundos')

    plt.tight_layout()
    
    try:
        plt.savefig(caminho_saida, dpi=150)
        print(f"Gráfico salvo em {caminho_saida}")
    except Exception as e:
        print(f"Erro ao salvar gráfico: {str(e)}")
        raise
    finally:
        plt.close()

if __name__ == "__main__":
    print("=== INICIANDO ANALYZER ===")
    experiment_id = os.getenv("EXPERIMENT_ID", "default")
    print(f"Experiment ID: {experiment_id}")
    
    try:
        # Pipeline principal com try externo
        output_dir = os.path.join("/app/output", experiment_id)
        print(f"[DEBUG] Output dir: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        print("[DEBUG] Carregando dados...")
        X, y = carregar_dados()
        
        print(f"[DEBUG] Dados carregados. X: {len(X)}, y: {len(y)}")
        
        # Verificação de dados
        if not X or not y:
            raise ValueError("Dados vazios ou inválidos")
            
        print("[DEBUG] Processando métodos...")
        resultados = comparar_metodos(X, y)
        
        print("[DEBUG] Salvando métricas...")
        with open(f"{output_dir}/metricas.txt", 'w') as f:
            for metodo, res in resultados.items():
                f.write(
                    f"Método: {metodo}\n"
                    f"Parâmetros: {res['theta']}\n"
                    f"Tempo: {res['tempo']:.4f}s\n"
                    f"Resíduo: {res['residuo']:.4f}\n\n"
                )
                
        print("[DEBUG] Gerando gráficos...")
        plot_resultados(X, y, resultados, f"{output_dir}/resultados.png")
        
        print(f"✅ Análise concluída! Resultados em {output_dir}")
        
    except Exception as e:
        print(f"⛔ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()  # Adiciona stack trace
        exit(1)

print("Gráficos salvos com sucesso!", flush=True)
