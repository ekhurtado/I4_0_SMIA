#!/usr/bin/env python
import os
import subprocess

import rospy
from std_msgs.msg import String

import json
import time

processed_requests = {}
ros_master_uris = {}
aas_core_id = None
status_subscriber = None

def main():

    try:
        req_file = open('/ros_aas_core_archive/requests.json', 'x')
    except FileExistsError as e:
        req_file = open('/ros_aas_core_archive/requests.json', 'w')
    json.dump({'requests': []}, req_file)
    req_file.close()

    try:
        status_file = open('/ros_aas_core_archive/status.json', 'x')
    except FileExistsError as e:
        status_file = open('/ros_aas_core_archive/status.json', 'w')
    json.dump({'status': 'IDLE'}, status_file)
    status_file.close()

    # TODO old version
    # rospy.init_node('ROS_AAS_Core_Gateway', anonymous=True)
    #
    # # Each function will have its own thread of execution
    # thread_func1 = Thread(target=process_requests, args=())
    # thread_func2 = Thread(target=status_callback, args=())
    # thread_func1.start()
    # thread_func2.start()

    # TODO new version (multiple AAS Cores for ROS)
    # Define the MASTER URI for all cores
    global ros_master_uris
    ros_master_uris['aas-ros-test01'] = 'http://192.168.1.62:11311'
    ros_master_uris['transportrobot001'] = 'http://192.168.1.62:11311'
    ros_master_uris['aas-ros-test02'] = 'http://192.168.1.64:11311'

    # Execute logic to get and process all requests
    process_requests_from_all_cores()

def status_callback():
    print("Obtaining status information...")
    # global status_subscriber
    # status_subscriber = rospy.Subscriber('/status', String, callback)
    rospy.Subscriber('/status', String, callback)


def callback(data):
    # Este método se ejecutará cada vez que se publiquen datos por el tópico /status
    print("[TURTLEBOT3 - NEW STATE] :" + str(data.data))

    # Actualiza el estado del transporte
    state = str(data.data)
    update_status_file(state)

def update_status_file(state):
    global aas_core_id
    status_json = {'status': {aas_core_id: state}}
    status_file = open('/ros_aas_core_archive/status.json', 'w')
    json.dump(status_json, status_file)
    status_file.close()
    print("Status file updated.")

def check_status_received_by_core(aas_id, interaction_id):
    while True:
        status_json = file_to_json('/ros_aas_core_archive/status.json')
        try:
            if status_json[aas_id][interaction_id] == 'completed':
                print("The service has been completed, so the robot has reached the target coordinates.")
                return
        except Exception as e:
            print("For now the AAS Core has not written the status of the service, waiting for 2 seconds...")
            time.sleep(2)


def process_requests():
    while True:
        all_req_received = get_all_requests()
        global processed_requests

        for req_received in all_req_received:

            if (req_received is not None) and (req_received['interactionID'] not in processed_requests):
                print("  --> NEW REQUEST!")
                ros_topic = req_received['ros_topic']
                ros_msg = req_received['ros_msg']

                print("ROS TOPIC: " + str(ros_topic) + " , ROS_MSG: " + str(ros_msg))
                pub = rospy.Publisher(ros_topic, String, queue_size=10)
                print("Publisher created")

                time.sleep(1)
                print("Sending message...")
                pub.publish(ros_msg)
                time.sleep(1)
                print("Message sent")

                processed_requests.append(req_received['interactionID'])

        time.sleep(5)

def process_requests_from_all_cores():
    while True:
        all_req_received = get_all_requests()
        global processed_requests

        for req_received in all_req_received:
            # print("Nueva request")
            # print("AASID {}".format(req_received['aasID']))
            # print("InterID {}".format(req_received['interactionID']))
            # print("TODOS: {}".format(processed_requests))

            if req_received['aasID'] in processed_requests:
                if req_received['interactionID'] in processed_requests[req_received['aasID']]:
                    continue
                else:
                    process_request(req_received)
            else:
            # if (req_received is not None) and (req_received['interactionID'] not in processed_requests):
                process_request(req_received)

        time.sleep(1)


def process_request(request_data):
    print("  --> New request received from AAS with id [{}]".format(request_data['aasID']))
    global aas_core_id
    aas_core_id = request_data['aasID']
    global ros_master_uris
    print("Changing environmental variable for ROS MASTER URI...")
    os.environ["ROS_MASTER_URI"] = ros_master_uris[request_data['aasID']]
    # Using subprocess to execute a command in the host to change the environmental variable (with 'os.environ' the
    # variable only changes in the environment of the Python process)
    ros_master_uri = ros_master_uris[request_data['aasID']]
    command = f'export ROS_MASTER_URI={ros_master_uri} && echo $ROS_MASTER_URI'
    print("COMMAND: " + command)
    subprocess.run(command, shell=True, check=True)
    print("Environmental variable for ROS MASTER URI changed to {}.".format(ros_master_uris[request_data['aasID']]))

    # Create the ros node
    rospy.init_node('ROS_AAS_Core_Gateway', anonymous=True)

    # Get the information about ROS
    ros_topic = request_data['ros_topic']
    ros_msg = request_data['ros_msg']

    if ros_topic == '/coordinate':
        update_status_file('waiting')
        # Create the status subscriber
        status_callback()
    print("ROS TOPIC: " + str(ros_topic) + " , ROS_MSG: " + str(ros_msg))

    # Publish the message
    pub = rospy.Publisher(ros_topic, String, queue_size=10)
    print("Publisher created")
    time.sleep(1)
    print("Sending message...")
    pub.publish(ros_msg)
    print("Message sent")

    if ros_topic == '/coordinateIDLE':
        # In this case, the node must send the coordinates and check the status immediately
        add_request_data_as_processed(request_data)
        process_requests_from_all_cores()
    time.sleep(1)

    # Now, the gateway will wait until the status is received by the AAS Core
    check_status_received_by_core(aas_id=request_data['aasID'],
                                  interaction_id=request_data['interactionID'])

    # The status subscriber is unsubscribed
    # global status_subscriber
    # status_subscriber.unregister()
    add_request_data_as_processed(request_data)

    # Shutdown the ros node
    rospy.signal_shutdown("node completed")
    print(" --> Service completed!")


def add_request_data_as_processed(request_data):
    global processed_requests
    if request_data['aasID'] not in processed_requests:
        processed_requests[request_data['aasID']] = {request_data['interactionID']}
    else:
        processed_requests[request_data['aasID']].update({request_data['interactionID']})


def get_all_requests():
    print("Obtaining all requests from AAS Core.")
    svc_requests_file_path = '/ros_aas_core_archive/requests.json'
    svc_requests_json = file_to_json(svc_requests_file_path)
    # if len(svc_requests_json['requests']) != 0:
    #     return svc_requests_json['requests'][len(svc_requests_json['requests']) - 1]
    # else:
    #     return None
    return  svc_requests_json['requests']


def file_to_json(file_path):
    f = open(file_path)
    try:
        content = json.load(f)
        f.close()
    except json.JSONDecodeError as e:
        print("Invalid JSON syntax:" + str(e))
        return None
    return content


def update_json_file(file_path, content):
    """
    This method updates the content of a JSON file.

    Args:
        file_path (str): the path to the JSON file.
        content (dict): the content of the JSON file.
    """
    with open(file_path, "w") as outfile:
        json.dump(content, outfile)

if __name__ == '__main__':
    print('Gateway to link the AAS Core and ROS simulation resources')
    print('Gateway starting...')
    main()
    # print('Gateway ending...')
