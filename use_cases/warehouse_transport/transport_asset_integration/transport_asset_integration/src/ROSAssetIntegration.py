from threading import Thread

from AssetServices import AssetServices
from AssetServicesInfo import AssetServicesInfo


class ROSAssetIntegration:

    def __init__(self):
        self.asset_services = AssetServices()
        self.services_to_process = []
        self.processed_services = {}
        self.services_id = 0

        self.initialize_asset_integration()

    def add_new_service_to_process(self, service_data):
        current_service_id = self.services_id
        service_data['serviceID'] = current_service_id
        self.services_to_process.append(service_data)
        self.services_id += 1
        return current_service_id

    def add_new_processed_service(self, service_id, service_data):
        self.processed_services[service_id] = service_data

    def pop_service_to_process(self):
        if self.services_to_process:
            return self.services_to_process.pop()
        else:
            return None

    def get_processed_service(self, service_id):
        if service_id not in self.processed_services:
            return None
        else:
            return self.processed_services[service_id]

    def initialize_asset_integration(self):
        print("Initializing the Asset Integration for ROS-based assets...")

        # A ROS node corresponding to the AAS Core is executed.
        self.asset_services.initialize_ros_node()
        print("ROS node for the AssetIntegration initiated.")

        self.asset_services.initialize_publishers()
        print("ROS publishers for the AssetIntegration initiated.")

    def run_asset_integration(self):
        # Each function will have its own thread of execution
        thread_func1 = Thread(target=self.handle_data_to_ros, args=())
        thread_func2 = Thread(target=self.handle_data_from_ros, args=())

        thread_func1.start()
        thread_func2.start()

    def handle_data_to_ros(self):
        """This method handles the message and data to the transport. Thus, it obtains the requests of the HTTP Server
         and send to necessary command to the asset."""
        while True:
            service_to_process = self.pop_service_to_process()
            if service_to_process:
                print("New service to process: {}".format(service_to_process))
                if service_to_process['type'] == 'GET':
                    if service_to_process['data'] in AssetServicesInfo.PROPERTIES_DATA:
                        requested_data = self.get_property(service_to_process['data'])
                        self.add_new_processed_service(service_to_process['serviceID'],
                                                       {'data': service_to_process['data'],
                                                                    'value': requested_data})
                        print("Property-related service finished")
                    elif service_to_process['data'] in AssetServicesInfo.ACTIONS_DATA:
                        action_result = self.perform_action(service_to_process['data'], service_to_process['parameters'])
                        self.add_new_processed_service(service_to_process['serviceID'],
                                                       {'data': service_to_process['data'],
                                                                    'result': action_result})
                        print("Action-related service finished")




    def handle_data_from_ros(self):
        """This method handles the message and data from the transport. Thus, it obtains the data from the asset with a ROS
                Subscriber node and send the necessary interaction command or response to the AAS Manager."""

        # Crea un nodo SUBSCRIBER, que se quedará a la escucha por el tópico /status
        # y notificará al agente del estado del transporte
        self.asset_services.initialize_status_subscriber()


    # ASSET SERVICES
    def get_property(self, property_name):
        return self.asset_services.get_property(property_name)

    def perform_action(self, action_name, parameters):
        return self.asset_services.perform_action(action_name, parameters)
