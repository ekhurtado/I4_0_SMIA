import json
import random

from assetconnection.AssetConnection import AssetConnection


class HTTPAssetConnection(AssetConnection):
    """
    This class implements the asset connection for HTTP protocol.
    TODO desarrollarlo mas
    """

    def __init__(self):
        super().__init__()
        self.architecture_style = AssetConnection.ArchitectureStyle.CLIENTSERVER

    def configure_connection(self, configuration_data):
        # TODO BORRAR (es solo para pruebas, esta como el AAS Core de ROS, usando un fichero JSON como intermediario para el gateway)
        self.ros_topic = configuration_data['ros_topic']

    def connect_with_asset(self):
        pass

    def send_msg_to_asset(self, msg):
        # TODO BORRAR (es solo para pruebas, esta como el AAS Core de ROS, usando un fichero JSON como intermediario para el gateway)
        current_interaction_id = str(random.randint(0, 10000))
        gw_request_obj = {'aasID': 'transportrobot001',
                          'interactionID': current_interaction_id,
                          'ros_topic': self.ros_topic,
                          'ros_msg': msg
                          }
        gw_requests_file_path = '/ros_aas_core_archive/requests.json'
        f = open(gw_requests_file_path)
        gw_requests_json = json.load(f)
        f.close()
        gw_requests_json['requests'].append(gw_request_obj)
        with open('/ros_aas_core_archive/requests.json', "w") as outfile:
            json.dump(gw_requests_json, outfile)

    def receive_msg_from_asset(self):
        pass