#!/usr/bin/env python
from threading import Thread

import rospy
from std_msgs.msg import String

import json
import time

processed_requests = []


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

    rospy.init_node('ROS_AAS_Core_Gateway', anonymous=True)

    # Each function will have its own thread of execution
    thread_func1 = Thread(target=process_requests, args=())
    thread_func2 = Thread(target=status_callback, args=())

    thread_func1.start()
    thread_func2.start()


def status_callback():
    print("Obtaining status information...")
    rospy.Subscriber('/status', String, callback)


def callback(data):
    # Este método se ejecutará cada vez que se publiquen datos por el tópico /status
    print("[TURTLEBOT3 - NEW STATE] :" + str(data.data))

    # Actualiza el estado del transporte
    state = str(data.data)
    status_json = {'status': state}
    status_file = open('/ros_aas_core_archive/status.json', 'w')
    json.dump(status_json, status_file)
    status_file.close()
    print("Status file updated.")


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


def get_all_requests():
    print("Obtaining the all requests from AAS Core.")
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

if __name__ == '__main__':
    print('Gateway to link the AAS Core and ROS simulation resourcees')
    print('Gateway starting...')
    main()
    print('Gateway ending...')
