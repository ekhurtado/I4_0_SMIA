"""This class contains some utils methods related to OPC UA."""
import time

import opcua.ua
from opcua import Client


def sendDataOPCUA(nServ, targetPos):
    # En este método se realiza toda la lógica de lectura/escritura de nodos
    # publicados en la interfaz del servidor OPC UA
    # --------------------------------------------------------------------------------
    # Instanciar cliente
    print("Sending command through OPC UA...")
    client = Client("opc.tcp://192.168.1.71:4840")  # TODO se podria añadir este metodo en la clase AASCore y utilizar el cliente de la clase
    # Establecer conexión con servidor OPCUA
    client.connect()

    # Obtener el servicio y la posición a procesar
    target = int(targetPos)
    serviceType = nServ

    print("The service type is " + str(serviceType) + " and the target " + str(target))

    # Instanciar nodos con los que se realizarán las operaciones rw
    node_Reset = client.get_node("ns=4;i=8")
    node_CogerDejar = client.get_node("ns=4;i=10")
    node_Posicion = client.get_node("ns=4;i=66")
    node_ServiceFinished = client.get_node("ns=4;i=5")
    node_AlmacenOcupacion = client.get_node("ns=4;i=11")

    # --------- Prod. Normal ------------
    # Escribir tipo de servicio solicitado
    #     * INTRODUCIR ( CogerDejar = 1 )
    if serviceType == 'INTRODUCE':
        node_CogerDejar.set_value(True)
    else:
        #   * EXTRAER ( CogerDejar = 0 )
        node_CogerDejar.set_value(False)

    # Escribir posición objetivo de la solicitud
    node_Posicion.set_value(target, varianttype=opcua.ua.VariantType.Int16)

    # Comprobar si la acción es realizable
    ok = servicePossible(node_AlmacenOcupacion, serviceType, target)

    # Si no existen impedimentos para la puesta en marcha
    if ok:
        print("The service is possible to perform.")
        # Simular pulso de Reset
        node_Reset.set_value(True)
        time.sleep(1)
        node_Reset.set_value(False)

        # Crear una variable que notifica del estado del proceso.
        # Cuando haya terminado la tarea, se pondrá en True
        finished = False

        while not finished:
            finished = node_ServiceFinished.get_value()

        print("          + SERVICE FINISHED!")

        # Devolver señal de tarea FINALIZADA
        return "FINISHED"
    else:
        # Si no existen impedimentos para la puesta en marcha
        # Simular pulso de Reset
        node_Reset.set_value(True)
        time.sleep(1)
        node_Reset.set_value(False)

        # Devolver señal de ERROR
        return "ERROR"


def servicePossible(node_AlmacenOcupacion, service, target):
    # Este método permite saber si la operación solicitada puede realizarse
    # o si existe algún problema que no permita su puesta en marcha.

    print("Checking if the service is possible...")
    # Obtener matriz de ocupación del almacén
    warehouseOcupation = node_AlmacenOcupacion.get_value()

    # Si se quiere INTRODUCIR Y la posición está ocupada
    if service == 'INTRODUCE' and warehouseOcupation[target - 1] == True:
        return False
    # Si se quiere EXTRAER Y la posición está vacía
    if service == 'EXTRACT' and warehouseOcupation[target - 1] == False:
        return False
    return True
