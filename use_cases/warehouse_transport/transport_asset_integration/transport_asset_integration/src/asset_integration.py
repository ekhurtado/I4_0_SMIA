import sys

from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def main():
    return 'Hello! I am the Asset Integration element for a ROS-based transport robot.\n'


@app.route('/robotproperties/', methods=['GET', 'POST'])
def get_robot_properties():

    print("Se quiere conseguir una propiedad del robot")

    tend = 'NEG'

    # Falta por hacer

    return 'Tendency of OEE is ' + str(tend) +'\n'



@app.route('/calculate/', methods=['POST'])
def calculate():
    message = ""
    if (function == "processingOEE"):
        message = calculateOEE()

    return message