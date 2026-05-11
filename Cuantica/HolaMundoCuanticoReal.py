#Codigo cuantico Real con Qiskit

from qiskit import QuantumCircuit, execute, AncillaRegister

quancircuit = QuantumCircuit(1, 1 )
quancircuit.h(0)
quancircuit.measure(0,0)

#Ejecutar en simulaldor cuantico REAL
simulador = Aer.get_backend('qasm_simulator')
resultado = execute(quancircuit, backend=simulador, shots=1024).result