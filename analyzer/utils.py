import psutil

def parse_metrics(metrics_text):
    """Converte o texto de métricas em dicionário estruturado"""
    methods = {}
    current_method = None
    
    for line in metrics_text.split('\n'):
        if line.startswith('Método:'):
            current_method = line.split(': ')[1].strip()
            methods[current_method] = {}
        elif line.startswith('Parâmetros:'):
            params = line.split(': ')[1].strip('[]')
            methods[current_method]['theta'] = [float(x) for x in params.split(', ')]
        elif line.startswith('Tempo:'):
            methods[current_method]['tempo'] = float(line.split(': ')[1].replace('s', ''))
        elif line.startswith('Resíduo:'):
            methods[current_method]['residuo'] = float(line.split(': ')[1])
    
    return methods

def is_diagonally_dominant(A):
    """Verifica se a matriz é diagonalmente dominante"""
    for i in range(len(A)):
        row_sum = sum(abs(A[i][j]) for j in range(len(A)) if j != i)
        if abs(A[i][i]) <= row_sum:
            return False
    return True

def monitor_resources():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_used": psutil.virtual_memory().used
    }