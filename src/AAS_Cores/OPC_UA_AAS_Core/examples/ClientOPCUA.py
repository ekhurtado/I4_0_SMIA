"""Author: Maite López Mena"""

import time

from opcua import Client

#Instanciar un cliente OPC UA
client = Client("opc.tcp://192.168.1.71:4840")

# Establecer conexión con el servidor
client.connect()

# Obtener nodos necesarios
node_AuxInit = client.get_node("ns=4;i=9")
node_Marcha = client.get_node("ns=4;i=7")

# ------- Simular arranque de máquina ------- #
# Simular pulso de "AuxInit"
node_AuxInit.set_value(True)
time.sleep(1)
node_AuxInit.set_value(False)

# Simular pulso de "Marcha"
node_Marcha.set_value(True)
time.sleep(1)
node_Marcha.set_value(False)
time.sleep(2)

print("MACHINE READY TO TAKE REQUESTS!")