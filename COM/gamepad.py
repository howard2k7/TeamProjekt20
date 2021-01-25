'''
	Client for GamePad Control @ Control Side

	Author: Fabian Schäfle
	Projekt: PINI 20/21

	The code
	is documentation
	enough
'''


import pygame as pg
import json, os
import zmq, math
from threading import Thread
import msgpack


class Gamepad:

	connectedPad = ""
	buttonPressed = ""
	delayHelper = 0

	def __init__(self, ipAddress, mother):

		self.mother = mother
		pg.init()

		self.connectionEst = False
		self.running = True
		self.clock = pg.time.Clock()

		# Init Gamepad
		self.gamepad, self.buttons = self.initializeJoystick()
		# print(self.buttons)

		# Init connection
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PAIR)
		self.socket.connect("tcp://"+str(ipAddress)+":5555")
		# self.socket.connect("tcp://127.0.0.1:5555")

		# Init return channel
		self.backChannel = Thread(target=self.backReport, args=())
		self.backChannel.start()

		# Vars
		self.speed = 0.0
		self.angle = 0

	def __del__(self):
		self.backChannel.join()

	def checkConnection(self):
		try:
			self.socket.send(msgpack.packb("SYN"))
		except KeyboardInterrupt:
			print("SocketError")


	def backReport(self):
		while True:
			try:
				input = msgpack.unpackb(self.socket.recv())
				print(input)
				if input == "button":
					print(self.buttonPressed)
				if input == "ACK":
					self.connectionEst = True
			except KeyboardInterrupt:
				break

	def getConnectionStatus(self):
		if self.connectionEst == True:
			return True
		else:
			return False


	def initializeJoystick(self):

		buttons = {}
		if pg.joystick.get_count() < 1:
			self.mother.write("Could'nt find any gamepads")
			self.mother.write("Please connect a gamepad and try again")
		else:
			joystick = pg.joystick.Joystick(0)
			joystick.init()
			self.connectedPad = joystick.get_name()
			if self.connectedPad == "Nintendo Switch Pro Controller":

				with open(os.path.join("nintendo.json"), 'r+') as file:
					buttons = json.load(file)
					buttons = {int(key): value for key, value in buttons.items()}

			if self.connectedPad == "PS4 Controller":
				with open(os.path.join("ps4.json"), 'r+') as file:
					buttons = json.load(file)
					buttons = {int(key): value for key, value in buttons.items()}

			if self.connectedPad == "XInput Controller #1":
				with open(os.path.join("F310.json"), 'r+') as file:
					buttons = json.load(file)
					buttons = {int(key): value for key, value in buttons.items()}

			return joystick, buttons

	def printGamepadInformation(self, index, gamepad):
		self.mother.write("Using Gamepad " + str(index))
		self.mother.write("_________________")
		self.mother.write(gamepad.get_name())
		self.mother.write("Buttons: " + str(gamepad.get_numbuttons()))
		self.mother.write("Axis: " + str(gamepad.get_numaxes()))
		self.mother.write("Hats: " + str(gamepad.get_numhats()))

	def printPressedButton(self, joystick, buttons):
		buttonCount = joystick.get_numbuttons()
		for i in range(buttonCount):
			if joystick.get_button(i):
				if i in buttons:
					self.buttonPressed = buttons[i]
					#print("Button pressed: %s " % buttons[i])
					return i
				else:
					self.buttonPressed = i
					#print("Button not mapped, button pressed : %s" % i)
					return i
		return -1

	def axis(self, gamepad):
		# Geschwindigkeit(a):

		a = gamepad.get_axis(1)  # mit a als Y-Achse
		a = -round(a, 1)  # rundet auf die erste Nachkommastelle

		b = gamepad.get_axis(0)  # mit b als X-Achse
		b = -round(b, 1)

		# Winkel
		c = round(math.atan2(a, b) * 180 / (math.pi) - 90, 0)  #
		if c < 0:
			c += 360

		c = round(c, 0)  # rundet auf ganze Zahl

		# Geschwindigkeit
		a = round(math.sqrt(b * b + a * a), 1)

		if a >= 1.0:
			a = 1.0

		if a == 0:
			c = 0.0

		return abs(a), c

	def checkDelay(self):
		if self.delayHelper > 0:
			if self.delayHelper < 7:
				self.delayHelper = self.delayHelper + 1
			else:
				self.delayHelper = 0

	def setNextHeight(self, actual):
		if actual == "Höhe 1":
			self.mother.selectedHeight.set("Höhe 2")
		elif actual == "Höhe 2":
			self.mother.selectedHeight.set("Höhe 3")
		elif actual == "Höhe 3":
			self.mother.selectedHeight.set("Höhe 1")

	def getControlSignals(self):
		# Init Gamepad
		gamepad, buttons = self.initializeJoystick()

		#self.screen = pg.display.set_mode([40, 40])
		self.printGamepadInformation(0, gamepad)

		while self.running:

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						self.running = False

			somethingPressed = self.printPressedButton(gamepad, buttons)
			if (somethingPressed > -1):
				if somethingPressed == 15:
					self.running = False
				if somethingPressed in buttons.keys():
					if buttons[somethingPressed] == "X":
						actualHeight = self.mother.selectedHeight.get()
						if self.delayHelper == 0:
							self.setNextHeight(actualHeight)
							self.delayHelper = 1
					else:
						self.socket.send(msgpack.packb(buttons[somethingPressed]))
						self.mother.write2(buttons[somethingPressed])
				else:
					self.socket.send(msgpack.packb("Unknown key pressed!"))

			self.speed, self.angle = self.axis(gamepad)
			#if (self.angle == 90.0):
				#self.socket.send(msgpack.packb([self.mother.pace * 0, 0, 0.1])) #self.angle * (math.pi) / 180
			#else:	#(self.speed > 0.09) or (self.angle)
				#self.socket.send(msgpack.packb([ * self.speed , self.angle * (math.pi) / 180, 1.0]))
			self.socket.send(msgpack.packb([self.mother.pace * self.speed, self.angle * (math.pi) / 180, 0.1]))
			self.mother.write2("Speed: " + str(1) + " Angle: " + str(self.angle))
				#print("Speed " + str(self.speed) + " Winkel: " + str(self.angle))
			#pg.display.flip()

			## TODO: Change to Array for more than 1 valuechange (Start, End e.t)
			self.checkDelay()
			self.clock.tick(30)
		pg.quit()
		self.backChannel.join()



