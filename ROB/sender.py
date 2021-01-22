import math

import zmq
import msgpack

__PORT = "5556"

context = zmq.Context()

socket = context.socket(zmq.PAIR)
socket.connect("tcp://127.0.0.1:"+__PORT)

while True:
    velocityInput = input("Geschwindigkeit angeben(0 bis 1): ")
    degreeInput = input("Winkel angeben: ")
    heightInput = input("Höhe angeben(0 bis 1): ")
    socket.send(msgpack.packb([float(velocityInput), float(degreeInput) * (math.pi) / 180, float(heightInput)]))
