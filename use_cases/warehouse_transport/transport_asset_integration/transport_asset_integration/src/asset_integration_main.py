import signal
import sys
import time

from flask import Flask, request, jsonify, Response

from AssetServicesInfo import AssetServicesInfo
from ROSAssetIntegration import ROSAssetIntegration

app = Flask(__name__)

asset_integration = ROSAssetIntegration()
asset_integration.run_asset_integration()

@app.route('/')
def main():
    return 'Hello! I am the Asset Integration element for a ROS-based transport robot.\n'


@app.route('/robotproperties/', methods=['GET'])
def get_all_robot_properties():
    return jsonify(AssetServicesInfo.PROPERTIES_DATA)


@app.route('/robotproperties/<string:property_name>', methods=['GET', 'POST'])
def get_robot_property(property_name):
    if request.method == 'GET':
        if not check_request_parameter(property_name, 'property'):
            return jsonify({"status": "error", "message": "Property not found"}), 404

        print("Since the request data is valid, the service will be processed")
        service_id = asset_integration.add_new_service_to_process({'type': 'GET', 'data': property_name})
        service_result = get_service_result(service_id)
        print("The service has been processed: property {} has value {}.".format(service_result['data'], service_result['value']))
        if service_result['value']:
            return create_response_message(request, True, service_result['value'])
        else:
            return create_response_message(request, False, service_result['value'])
    if request.method == 'POST':
        # TODO
        print("This HTTP request is POST method")
        return "OK", 200


@app.route('/robotactions/<string:action_name>', methods=['GET'])
def execute_robot_action(action_name):
    if not check_request_parameter(action_name, 'action'):
        return jsonify({"status": "error", "message": "Action not found"}), 404

    # If all required parameters are present, the action can be executed
    print("Since the request data is valid, the action will be executed")
    service_id = asset_integration.add_new_service_to_process({'type': 'GET', 'data': action_name, 'parameters': request.args})
    service_result = get_service_result(service_id)
    print("The service has been processed: action {} with result {}.".format(service_result['data'],
                                                                             service_result['result']))

    success = service_result['result'] == 'SUCCESS'
    return create_response_message(request, success, service_result['result'])



def check_request_parameter(parameter_name, parameter_type):
    if parameter_type == 'property':
        return parameter_name in AssetServicesInfo.PROPERTIES_DATA
    elif parameter_type == 'action':
        action_info = AssetServicesInfo.ACTIONS_DATA.get(parameter_name)
        if not action_info:
            return False

        if "requires" in action_info:
            for param in action_info["requires"]:
                if param not in request.args:
                    return False
        return True


def create_response_message(request_info, success, data):
    # Check the 'Accept' header to determine response format
    accept_header = request_info.headers.get('Accept', 'text/plain')  # Default to text/plain if no header is provided
    # Define possible response formats based on 'Accept' header
    response = None
    if 'application/json' in accept_header:
        # JSON response
        response = jsonify({
            "status": "success",
            "data": data
        })
        response.headers['Content-Type'] = 'application/json'

    elif 'text/html' in accept_header:
        # HTML response
        html_content = f"""
            <html>
                <body>
                    <p>Status: success</p>
                    <p>Data: {data}</p>
                </body>
            </html>
            """
        response = Response(html_content, mimetype='text/html')

    elif 'text/plain' in accept_header:
        # Plain text response
        text_content = f"{data}"
        response = Response(text_content, mimetype='text/plain')

    if success:
        return response, 200
    else:
        return response, 400

def get_service_result(service_id):
    service_result = False
    while not service_result:
        # Service not processed yet
        time.sleep(1)
        service_result = asset_integration.get_processed_service(service_id)
    return service_result


def handler(sig_num, frame):
    # print("Gestor de señales llamado con la señal " + str(sig_num))
    # print("Comprueba el número de señal en https://en.wikipedia.org/wiki/Signal_%28IPC%29#Default_action")

    print('Exiting the program')
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)
    print("Program started. Type Ctrl-C to exit.\n")
    app.run(host='0.0.0.0')

