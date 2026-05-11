
import random
import numpy as np

# --- POTENCIAL BINARIO (0 o 1) ---
def sistema_binario():
    # El estado es determinista: 0 o 1

    estado = random.choice([0, 1])

    return f"Estado Binario: {estado} (Definido)"

# --- POTENCIAL CUÁNTICO (Superposición) ---
def sistema_cuantico():
    # El estado es una probabilidad (Amplitud de probabilidad)
    # Representamos la superposición como una suma de estados |0> y |1>
    # psi = alpha|0> + beta|1> donde |alpha|^2 + |beta|^2 = 1
    
    alpha = 0.6 # Probabilidad de ser 0: 36%
    beta = 0.8  # Probabilidad de ser 1: 64%
    
    # Al medir, la naturaleza elige basada en las probabilidades
    medicion = np.random.choice([0, 1], p=[alpha**2, beta**2])
    
    return f"Estado Cuántico (Superposición): {alpha}|0> + {beta}|1> -> Medición: {medicion}"

print(sistema_binario())
print(sistema_cuantico())


def sistema_cuantico_simulado():

    #amplitudes(no son probabilidades aun)
    amplitud_0=0.6
    amplitud_1=0.8

    #convertir a probabilidades(Regla de Born)
    prob_0 = abs(amplitud_0)**2
    prob_1 = abs(amplitud_1)**2

    #simular la medicion(colapso de la funcion de onda)
    resultado = np.random.choice([0,1], p=[prob_0, prob_1])

    return resultado




