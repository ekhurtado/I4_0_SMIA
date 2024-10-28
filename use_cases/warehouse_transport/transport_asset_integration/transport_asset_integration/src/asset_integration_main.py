import sys

from flask import Flask, request, jsonify

from AssetServicesInfo import AssetServicesInfo

app = Flask(__name__)


@app.route('/')
def main():
    return 'Hello! I am the Asset Integration element for a ROS-based transport robot.\n'


@app.route('/robotproperties/', methods=['GET'])
def get_all_robot_properties():
    return jsonify(AssetServicesInfo.PROPERTIES_DATA)


@app.route('/robotproperties/<string:property_name>', methods=['GET', 'POST'])
def get_robot_property(property_name):
    if request.method == 'GET':
        property_info = AssetServicesInfo.PROPERTIES_DATA.get(property_name)
        if not property_info:
            return jsonify({"status": "error", "message": "Property not found"}), 404

        if "requires" in property_info:
            for param in property_info["requires"]:
                if param not in request.args:
                    return jsonify({"status": "error", "message": f"Missing required parameter '{param}'"}), 400

        # If all required parameters are present, return the property info
        return jsonify({"status": "success", "property": property_info, "parameters": request.args})
    if request.method == 'POST':
        # TODO
        print("This HTTP request is POST method")
        return "OK", 200


@app.route('/robotactions/<string:action_name>', methods=['GET'])
def execute_robot_action(action_name):
    action_info = AssetServicesInfo.ACTIONS_DATA.get(action_name)
    if not action_info:
        return jsonify({"status": "error", "message": "Action not found"}), 404

    if "requires" in action_info:
        for param in action_info["requires"]:
            if param not in request.args:
                return jsonify({"status": "error", "message": f"Missing required parameter '{param}'"}), 400

    # If all required parameters are present, return the property info
    return jsonify({"status": "success", "property": action_info, "parameters": request.args})


if __name__ == '__main__':
    app.run(debug=True)
