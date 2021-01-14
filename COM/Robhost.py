'''

	Host for GamePad Control @ Robot Side

	Author: Fabian Schäfle
	Projekt: PINI 20/21

	Demo with moving block in PyGame

	The code
	is documentation
	enough

'''

import pygame as pg
import zmq
from threading import Thread
import msgpack

class Host:

	lastPressed = ""

	def channel(self):
		print("channel")
		while True:
			try:
				self.lastPressed = msgpack.unpackb(self.socket.recv())
				print(self.lastPressed)
				if (self.lastPressed == "SYN"):
					print("SYN")
					self.socket.send(msgpack.packb("ACK"))

			except KeyboardInterrupt:
				break

	def __init__(self):

		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PAIR)
		self.socket.bind("tcp://*:5555")

		self.control = Thread(target=self.channel, args=())
		self.control.start()

