# Ajuste de Curvas - Integração com Artigo
# Autor: Code Copilot

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Função modelo baseada no artigo (linear)
def modelo(x, a, b):
    return a * x + b

# Dados experimentais fictícios baseados no artigo
# Substitua pelos dados do artigo, se disponíveis
x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
y_experimental = np.array([5, 8, 11, 15, 19, 24, 28, 33, 38, 44, 50])  # Dados simulados

# Ajuste da curva usando o método dos mínimos quadrados
parametros_iniciais = [1, 1]  # Estimativas iniciais para a, b
parametros_otimizados, covariancia = curve_fit(modelo, x, y_experimental, p0=parametros_iniciais)

# Parâmetros ajustados
a_otimizado, b_otimizado = parametros_otimizados
print(f"Parâmetros ajustados: a={a_otimizado:.2f}, b={b_otimizado:.2f}")

# Gerar valores ajustados
y_ajustado = modelo(x, a_otimizado, b_otimizado)

# Calcular o erro quadrático médio (MSE)
mse = np.mean((y_experimental - y_ajustado) ** 2)
print(f"Erro quadrático médio (MSE): {mse:.2f}")

# Visualizar os dados e o ajuste
plt.scatter(x, y_experimental, label="Dados experimentais", color="blue", alpha=0.7)
plt.plot(x, y_ajustado, label=f"Curva ajustada: y = {a_otimizado:.2f}x + {b_otimizado:.2f}", color="red")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.title("Ajuste de Curvas - Integração com Artigo")
plt.grid(True)
plt.show()                  