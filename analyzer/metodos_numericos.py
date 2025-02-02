# metodos_numericos.py

def gauss_pivoteamento(A, b):
    n = len(A)
    
    # Verificação de dimensionalidade
    if len(A) != len(b) or any(len(row) != n for row in A):
        raise ValueError("Dimensões incompatíveis entre A e b")
    
    # Cria matriz aumentada
    M = [linha + [bi] for linha, bi in zip(A, b)]
    
    for i in range(n):
        # Pivoteamento parcial
        max_row = max(range(i, n), key=lambda k: abs(M[k][i]))
        M[i], M[max_row] = M[max_row], M[i]
        
        # Verificação de pivô zero
        if abs(M[i][i]) < 1e-10:
            raise ValueError("Matriz singular detectada durante o pivoteamento")
            
        # Eliminação
        for j in range(i+1, n):
            factor = M[j][i] / M[i][i]
            for k in range(i, n+1):
                M[j][k] -= factor * M[i][k]
    
    # Retrosubstituição
    x = [0] * n
    for i in range(n-1, -1, -1):
        x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i+1, n))) / M[i][i]
    
    return x


def vetor_norma(v):
    return sum(vi**2 for vi in v) ** 0.5

def produto_escalar(v1, v2):
    return sum(x*y for x,y in zip(v1, v2))

def jacobi(A, b, max_iter=10000, tol=1e-10, damping=0.8):
    n = len(A)
    x = [0.0 for _ in range(n)]
    
    # Pré-condicionamento
    diag = [A[i][i] if A[i][i] != 0 else 1e-10 for i in range(n)]
    scaled_A = [[A[i][j]/diag[i] for j in range(n)] for i in range(n)]
    scaled_b = [b[i]/diag[i] for i in range(n)]
    
    for _ in range(max_iter):
        x_new = []
        max_diff = 0.0
        
        for i in range(n):
            sigma = sum(scaled_A[i][j] * x[j] for j in range(n) if j != i)
            x_new_i = scaled_b[i] - sigma
            
            # Aplicação de damping para estabilização
            x_new_i = damping * x_new_i + (1 - damping) * x[i]
            
            x_new.append(x_new_i)
            max_diff = max(max_diff, abs(x_new_i - x[i]))
            
        x = x_new
        
        if max_diff < tol:
            break
            
    return x

def gauss_seidel(A, B, max_iter=5000, tol=1e-12):
    n = len(B)
    x = [1.0] * n  # Inicialização mais segura
    
    for _ in range(max_iter):
        x_antigo = x.copy()
        max_diff = 0.0
        
        for i in range(n):
            soma = sum(A[i][j] * x[j] for j in range(n) if j != i)
            
            if abs(A[i][i]) < 1e-12:
                raise ValueError(f"Elemento diagonal zero em A[{i}][{i}]")
                
            novo_valor = (B[i] - soma) / A[i][i]
            diff = abs(novo_valor - x[i])
            if diff > max_diff:
                max_diff = diff
            x[i] = novo_valor
        
        if max_diff < tol:
            break
    
    return x
