# Importar las librerías necesarias de Qiskit
from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit
from qiskit import Aer, execute

# 1. Crear un registro cuántico con 1 cúbit y uno clásico con 1 bit
qr = QuantumRegister(1, 'q')
cr = ClassicalRegister(1, 'c')
circuito = QuantumCircuit(qr, cr)

# 2. Aplicar la compuerta Hadamard (H) para poner el cúbit en superposición
circuito.h(qr[0])

# 3. Medir el cúbit y guardar el resultado en el registro clásico
circuito.measure(qr[0], cr[0])

# 4. Ejecutar el circuito en un simulador local
simulador = Aer.get_backend('qasm_simulator')
resultado = execute(circuito, simulador, shots=1024).result()

# 5. Imprimir los resultados de las mediciones
conteos = resultado.get_counts(circuito)
print("Resultados de la medición:", conteos)
