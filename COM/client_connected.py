# Client for controlling the Robot via server

import pygame as pg
import joystick as joy
import zmq
from threading import Thread
#import threading

#connected = threading.Condition()

def interrupts(socket, conn):
	while conn < 10:
		try:
			if socket.recv_string() == "i":
				print("Got i")
				conn = conn + 1
	#		if socket.recv_string() == "HereIAm!":
	#			connected.acquire()
	#			connected.notify()
	#			connected.release()
	#			conn = True
		except KeyboardInterrupt:
			break


if __name__ == "__main__":

	pg.init()

	clock = pg.time.Clock()

	# Init Gamepad
	gamepad, buttons = joy.initializeJoystick()
	print(buttons)

	# Init connection
	connected = 0
	context = zmq.Context()
	socket = context.socket(zmq.PAIR)
	socket.connect("tcp://127.0.0.1:5555")

	listen_thread = Thread(target=interrupts, args=(socket, connected,))
	listen_thread.start()

	#connected.acquire()
	#connected.wait()


	running = True

	screen = pg.display.set_mode([40,40])


	while running:
		button = ""
		somethingPressed = -1
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					running = False
		somethingPressed = joy.printPressedButton(gamepad,buttons)
		if somethingPressed == 15:
			running = False

		if (somethingPressed > -1):
			if somethingPressed in buttons.keys():
				socket.send_string("Pressed: " + buttons[somethingPressed])
			else:
				socket.send_string("Unknown key pressed!")

		print(connected)
		pg.display.flip()
		clock.tick(1)

