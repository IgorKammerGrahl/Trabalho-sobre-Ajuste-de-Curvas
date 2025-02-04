# metodos_numericos.py

def gauss_pivoteamento(A, b):
    """
    Implementa a Eliminação Gaussiana com pivoteamento parcial para resolver sistemas lineares.
    
    Metodologia:
    1. Pivoteamento parcial para estabilidade numérica
    2. Eliminação progressiva para forma triangular superior
    3. Retrosubstituição para obtenção da solução
    
    Parâmetros:
    A - Matriz de coeficientes (n x n)
    b - Vetor de termos independentes (n)
    
    Retorna:
    x - Vetor solução (n)
    """
    n = len(A)
    
    # Verificação de dimensionalidade rigorosa
    if len(A) != len(b) or any(len(row) != n for row in A):
        raise ValueError("Dimensões incompatíveis entre A e b")
    
    # Cria matriz aumentada para operações diretas
    M = [linha + [bi] for linha, bi in zip(A, b)]
    
    for i in range(n):
        # Pivoteamento parcial: seleciona linha com maior valor absoluto na coluna atual
        max_row = max(range(i, n), key=lambda k: abs(M[k][i]))
        M[i], M[max_row] = M[max_row], M[i]
        
        # Verificação de singularidade numérica
        if abs(M[i][i]) < 1e-10:
            raise ValueError("Matriz singular detectada durante o pivoteamento")
            
        # Fase de eliminação
        for j in range(i+1, n):
            factor = M[j][i] / M[i][i]
            # Atualização otimizada da linha
            for k in range(i, n+1):
                M[j][k] -= factor * M[i][k]
    
    # Retrosubstituição com precisão melhorada
    x = [0] * n
    for i in range(n-1, -1, -1):
        soma = sum(M[i][j] * x[j] for j in range(i+1, n))
        x[i] = (M[i][n] - soma) / M[i][i]
    
    return x


def vetor_norma(v):
    return sum(vi**2 for vi in v) ** 0.5

def produto_escalar(v1, v2):
    return sum(x*y for x,y in zip(v1, v2))

def jacobi(A, b, max_iter=10000, tol=1e-10, damping=0.8):
    """
    Implementa o método de Jacobi com pré-condicionamento e fator de amortecimento.
    
    Metodologia:
    1. Pré-condicionamento diagonal para melhorar condicionamento
    2. Iterações simultâneas com amortecimento para estabilidade
    3. Critério de parada baseado na convergência máxima
    
    Parâmetros:
    A - Matriz de coeficientes
    b - Vetor de termos independentes
    max_iter - Número máximo de iterações
    tol - Tolerância para convergência
    damping - Fator de amortecimento (0.8 = 80% novo valor, 20% anterior)
    """
    n = len(A)
    x = [0.0 for _ in range(n)]
    
    # Pré-condicionamento adaptativo
    diag = [A[i][i] if A[i][i] != 0 else 1e-10 for i in range(n)]
    scaled_A = [[A[i][j]/diag[i] for j in range(n)] for i in range(n)]
    scaled_b = [b[i]/diag[i] for i in range(n)]
    
    # Loop principal de iterações
    for _ in range(max_iter):
        x_new = []
        max_diff = 0.0  # Monitora a maior mudança
        
        for i in range(n):
            # Cálculo da nova estimativa
            sigma = sum(scaled_A[i][j] * x[j] for j in range(n) if j != i)
            x_new_i = scaled_b[i] - sigma
            
            # Aplicação de damping para estabilização numérica
            x_new_i = damping * x_new_i + (1 - damping) * x[i]
            
            x_new.append(x_new_i)
            max_diff = max(max_diff, abs(x_new_i - x[i]))
            
        x = x_new
        
        # Critério de parada por convergência
        if max_diff < tol:
            break
            
    return x

def gauss_seidel(A, B, max_iter=5000, tol=1e-12):
    """
    Implementa o método de Gauss-Seidel com atualização in-place e verificação de convergência.
    
    Metodologia:
    1. Atualizações sequenciais usando valores já calculados
    2. Monitoramento contínuo da convergência
    3. Verificação de singularidade numérica
    
    Parâmetros:
    A - Matriz de coeficientes
    B - Vetor de termos independentes
    max_iter - Número máximo de iterações
    tol - Tolerância absoluta para convergência
    """
    n = len(B)
    x = [1.0] * n  # Inicialização conservadora
    
    for _ in range(max_iter):
        x_antigo = x.copy()
        max_diff = 0.0  # Norma infinito da diferença
        
        for i in range(n):
            # Soma usando valores atualizados (j < i) e antigos (j > i)
            soma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            
            # Verificação rigorosa de singularidade
            if abs(A[i][i]) < 1e-12:
                raise ValueError(f"Elemento diagonal zero em A[{i}][{i}]")
                
            novo_valor = (B[i] - soma) / A[i][i]
            diff = abs(novo_valor - x[i])
            max_diff = max(max_diff, diff)
            x[i] = novo_valor  # Atualização in-place
        
        # Critério de parada adaptativo
        if max_diff < tol:
            break
    
    return x
