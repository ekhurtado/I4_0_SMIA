import time
from threading import Thread

from opcua import Client

from smia.utilities import Interactions_utils
from smia.utilities import printFile
from smia.utilities import create_response_json_object
from smia.utilities.KafkaInfo import KafkaInfo
from smia.utilities import sendDataOPCUA


class AASCore:
    """
    This class contains all the information about the AAS Core
    """

    state = None
    ready = False
    WIP = False
    machine_plan = []
    processed_services = {}
    manager_status = None
    interaction_id_num = 0

    # OPC UA client
    client = None

    def __init__(self):
        self.state = 'IDLE'
        self.ready = False
        self.WIP = False
        self.machine_plan = []
        self.processed_services = {}
        self.manager_status = 'Unknown'

        self.client = None

        self.interaction_id_num = 0

    def increase_interaction_id_num(self):
        self.interaction_id_num += 1

    def get_interaction_id(self):
        return 'core-' + str(self.interaction_id_num)

    def initialize_aas_core(self):
        """This method executes the required tasks to initialize the AAS Core. In this case, create the connection and
        execute a necessary ROS nodes."""

        print("Initializing the AAS Core...")

        # A ROS node corresponding to the AAS Core is executed.
        # Instanciar cliente
        self.client = Client("opc.tcp://192.168.1.71:4840")
        # Establecer conexión con servidor OPCUA
        try:
            self.client.connect()
        except OSError as e:
            print("OSError: " + str(e))
            print("The OPC UA server is not available, waiting 5 seconds and trying to connect again...")
            time.sleep(5)
            self.initialize_aas_core()
        print("OPC UA client connected.")

        # Obtener nodos necesarios
        node_AuxInit = self.client.get_node("ns=4;i=9")
        node_Marcha = self.client.get_node("ns=4;i=7")

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

        print("WAREHOUSE MACHINE READY TO TAKE REQUESTS!")

    def run_aas_core(self):

        print("AAS Core running...")
        # AASArchive_utils.change_status('Running')
        self.send_status_change_to_manager('Running')

        # Each function will have its own thread of execution
        thread_func1 = Thread(target=self.handle_data_to_machine, args=())
        thread_func2 = Thread(target=self.handle_data_from_machine, args=())

        thread_func1.start()
        thread_func2.start()

    def handle_data_to_machine(self):
        """This method handles the message and data to the machine. Thus, it obtains the interaction requests by the
        AAS Manager and send to necessary command to the asset."""

        kafka_consumer_manager_partition = Interactions_utils.create_interaction_kafka_consumer('i4-0-smia-manager')

        # while True:
        print("Listening for manager messages in topic " + KafkaInfo.KAFKA_TOPIC)
        for msg in kafka_consumer_manager_partition:
            # TODO analizar los mensajes de peticiones del AAS Manager
            # msgReceived = get_next_svc_request()

            print("El consumidor del manager (partition 0) de Kafka ha recibido algo!")
            print("   |__ msg: " + str(msg))

            msg_key = msg.key.decode("utf-8")
            msg_json_value = msg.value

            printFile('opc_ua_log.txt', msg)
            printFile('opc_ua_log.txt', str(self.processed_services))

            if msg_key == 'manager-status':
                print("The AAS Core has received an update of the AAS Manager status.")
                self.manager_status = msg_json_value['status']
                if self.manager_status != 'Initializing':
                    print("AAS Manager has initialized, so the AAS Core can go to running state.")

            elif msg_key == 'manager-service-request':
                if self.manager_status != 'Initializing' and self.manager_status != 'idle':
                    # Only if the AAS Manager is ready the AAS Core will work
                    if msg_json_value['interactionID'] in self.processed_services:
                        print("The request with interaction_id [" + msg_json_value['interactionID'] +
                              "] has already been performed")
                        break
                    else:
                        machine_plan = [msg_json_value['serviceData']['serviceParams']['target']]
                        print("InteractionID: " + str(msg_json_value['interactionID']))
                        printFile('opc_ua_log.txt', "InteractionID: " + str(msg_json_value['interactionID']))

                        # Si ha llegado alguna peticion, se envia el comando a traves del pub y pubCoord
                        if len(machine_plan) > 0 and self.WIP == False:

                            # Coge la primera tarea de la lista
                            task = machine_plan[0]

                            # Identifica el tipo de tarea
                            taskType = task.split(":")[0]
                            # Obtiene la posición del almacén
                            target = task.split(":")[1]

                            # Si el servicio es "INTRODUCE"
                            if taskType == "INTRODUCE":
                                # Se marca como 'ocupado'
                                self.WIP = True

                                print("         + Sending task: MACHINE AGENT >>> GATEWAY AGENT OPCUA")
                                print("     [!] Introducing package into shelf No.  " + str(target) + " [!]")
                                print("               + Sending data to OPC UA Server...")

                                result = sendDataOPCUA(taskType, target)
                                if result == "FINISHED":
                                    print("+-----------------------------------------------------+")
                                    print("| Package SUCCESSFULLY STORED in AUTOMATED WAREHOUSE  |")

                                    self.processed_services[msg_json_value['interactionID']] = msg_json_value
                                    printFile('opc_ua_log.txt', 'SERVICE DONE!!!  - id:' + str(msg_json_value['interactionID']))

                                    # Send the response of the service to the AAS Manager
                                    self.send_svc_response_to_manager(svc_req_json=msg_json_value)

                                else:
                                    print("+-----------------** ERROR **-------------------+")
                                    print("| Shelf No. " + str(target) + " already OCCUPIED!! |")
                                    print("+-----------------------------------------------+")

                                self.WIP = False

                            else:  # Si el servicio es "EXTRACT"
                                # Se marca como 'ocupado'
                                self.WIP = True

                                print("         + Sending task: MACHINE AGENT >>> GATEWAY AGENT OPCUA")
                                print("     [!] Extracting box from shelf No. " + str(target) + " [!]")
                                print("               + Sending data to OPC UA Server...")

                                result = sendDataOPCUA(taskType, target)
                                if result == "FINISHED":
                                    print("+---------------------------------------------------------+")
                                    print("| Package SUCCESSFULLY EXTRACTED from AUTOMATED WAREHOUSE |")
                                    print("|   |____Establishing communication with [MACHINE AGENT]:machineagent@blah.im")

                                    self.processed_services[msg_json_value['interactionID']] = msg_json_value
                                    printFile('opc_ua_log.txt', 'SERVICE DONE!!!  - id:' + str(msg_json_value['interactionID']))

                                    # Send the response of the service to the AAS Manager
                                    self.send_svc_response_to_manager(svc_req_json=msg_json_value)

                                else:
                                    print("\n+-----------------** ERROR **-------------------+")
                                    print("|             Shelf No. " + str(target) + " is EMPTY!!            |")
                                    print("+-----------------------------------------------+")

                                self.WIP = False

            elif msg_key == 'manager-service-response':
                print("The AAS Core has received a response from the AAS Manager")
                # TODO
            else:
                print("Option not available")

    def handle_data_from_machine(self):
        """This method handles the message and data from the transport."""
        # TODO ver si tiene sentido
        pass

    # Interaction methods
    # -------------------
    def send_status_change_to_manager(self, new_status):
        """
        This method sends the status message to the Manager to notify that the state of the AAS Core has changed.
        """
        result = Interactions_utils.send_interaction_msg_to_manager(client_id='i4-0-smia-core',
                                                                    msg_key='core-status',
                                                                    msg_data={
                                                                        'interactionID': self.get_interaction_id(),
                                                                        'status': new_status})
        if result != "OK":
            print("The AAS Manager-Core interaction is not working: " + str(result))
        else:
            print("The AAS Core has notified the AAS Manager that its initialization has been completed.")


    def send_svc_response_to_manager(self, svc_req_json):
        """
        This method sends the response of the service to the AAS Manager .
        """
        # Send the response to the AAS Manager
        response_json = create_response_json_object(svc_req_json)
        printFile('opc_ua_log.txt', str(response_json))
        # add_new_svc_response(response_json)
        result = Interactions_utils.send_interaction_msg_to_manager(
            client_id='i4-0-smia-core',
            msg_key='core-service-response',
            msg_data=response_json)
        if result != "OK":
            print("The AAS Manager-Core interaction is not working: " + str(result))
        else:
            print(
                "The AAS Core has notified the AAS Manager that the service has been"
                " completed.")





