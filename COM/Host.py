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

SCREEN_WIDTH = 500
SCREEN_HIGHT = 500


class Player(pg.sprite.Sprite):
	def __init__(self):
		super(Player, self).__init__()
		self.surf = pg.Surface((75, 25))
		self.surf.fill((255, 255, 255))
		self.rect = self.surf.get_rect()


	def move(self, button):
		if button == "UP":
			print("Moving up")
			self.rect.move_ip(0,-5)
		if button == "DOWN":
			print("Moving down")
			self.rect.move_ip(0,5)
		if button == "LEFT":
			print("Moving left")
			self.rect.move_ip(-5,0)
		if button == "RIGHT":
			print("Moving right")
			self.rect.move_ip(5,0)


class Host:

	lastPressed = ""

	def channel(self):
		while True:
			try:
				self.lastPressed = msgpack.unpackb(self.socket.recv())

				if (self.lastPressed == "SYN"):
					self.socket.send(msgpack.packb("ACK"))

			except KeyboardInterrupt:
				break

	def __init__(self):
		pg.init()
		self.fps = pg.time.Clock()

		self.Robot = Player()

		self.screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HIGHT])

		self.running = True

		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PAIR)
		self.socket.bind("tcp://*:5555")

		self.control = Thread(target=self.channel, args=())
		self.control.start()

		self.playing()

	def playing(self):

		counter = 0

		while self.running:

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
			if self.lastPressed == "QUIT":
				self.running = False
			elif self.lastPressed == "SYN":
				pass
			else:
				self.Robot.move(self.lastPressed)
				self.lastPressed = ""

			self.screen.fill((0, 0, 0))
			self.surf = pg.Surface((50, 50))

			self.screen.blit(self.Robot.surf, self.Robot.rect)

			pg.display.flip()

			self.fps.tick(30)

		pg.quit()