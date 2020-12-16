# ZeroMQ Server Test

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:6969")

while True:
	message = socket.recv()
	print("Recieved: %s" %message)

	time.sleep(1)
	socket.send(b"World")


