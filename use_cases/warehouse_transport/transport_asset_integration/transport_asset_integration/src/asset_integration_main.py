import sys

from flask import Flask, request, jsonify, Response

from AssetServicesInfo import AssetServicesInfo
from ROSAssetIntegration import ROSAssetIntegration

app = Flask(__name__)

asset_integration = ROSAssetIntegration()


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

        property_value = asset_integration.get_property(property_name)
        if property_value:
            return create_response_message(request, True, property_value)
        else:
            return create_response_message(request, False, property_value)
    if request.method == 'POST':
        # TODO
        print("This HTTP request is POST method")
        return "OK", 200


@app.route('/robotactions/<string:action_name>', methods=['GET'])
def execute_robot_action(action_name):
    if not check_request_parameter(action_name, 'action'):
        return jsonify({"status": "error", "message": "Action not found"}), 404

    # If all required parameters are present, the action can be executed
    asset_integration.perform_action(action_name)

    return jsonify({"status": "success", "action": action_name, "parameters": request.args})


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


if __name__ == '__main__':
    app.run(debug=True)
