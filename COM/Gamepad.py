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
import zmq
from threading import Thread




class Gamepad:

	connectedPad = ""
	buttonPressed = ""

	def __init__(self, ipAddress):
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
		self.socket.connect(ipAddress)
		# self.socket.connect("tcp://127.0.0.1:5555")

		# Init return channel
		self.backChannel = Thread(target=self.backReport, args=())
		self.backChannel.start()

	def __del__(self):
		self.backChannel.join()

	def checkConnection(self):
		try:
			self.socket.send_string("SYN")
		except KeyboardInterrupt:
			print("SocketError")


	def backReport(self):
		while True:
			try:
				input = self.socket.recv_string()
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
		if pg.joystick.get_count() < 1:
			print("Could'nt find any gamepads\nPlease connect a gamepad and try again")
			exit()
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

			return joystick, buttons

	def printGamepadInformation(self, index, gamepad):
		print("Using Gamepad " + str(index))
		print("_________________")
		print(gamepad.get_name())
		print("Buttons: " + str(gamepad.get_numbuttons()))
		print("Axis: " + str(gamepad.get_numaxes()))
		print("Hats: " + str(gamepad.get_numhats()))

	def printPressedButton(self, joystick, buttons):
		buttonCount = joystick.get_numbuttons()
		for i in range(buttonCount):
			if joystick.get_button(i):
				if i in buttons:
					self.buttonPressed = buttons[i]
					print("Button pressed: %s " % buttons[i])
					return i
				else:
					self.buttonPressed = i
					print("Button not mapped, button pressed : %s" % i)
					return i
		return -1

	def getControlSignals(self):


		# Init Gamepad
		gamepad, buttons = self.initializeJoystick()



		self.screen = pg.display.set_mode([40, 40])

		while self.running:

			for event in pg.event.get():
				if event.type == pg.QUIT:
					self.running = False
				if event.type == pg.KEYDOWN:
					if event.key == pg.K_ESCAPE:
						self.running = False
			somethingPressed = self.printPressedButton(gamepad, buttons)
			if somethingPressed == 15:
				self.running = False

			if (somethingPressed > -1):
				if somethingPressed in buttons.keys():
					self.socket.send_string(buttons[somethingPressed])
				else:
					self.socket.send_string("Unknown key pressed!")

			pg.display.flip()
			self.clock.tick(30)
		pg.quit()
		self.backChannel.join()


