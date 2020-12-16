# ZeroMQ Client Test

import zmq

print("Connecting to Server")
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:6969")


for request in range(10):
	print("Sending request %s ..." %request)
	socket.send(b"Hello")

	message = socket.recv()
	print("Recieved reply %s [ %s ]" %(request, message))

