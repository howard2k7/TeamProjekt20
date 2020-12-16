

import pygame as pg
import json, os


# Prints some Information about the used hardware controller
def printGamepadInformation(index, gamepad):
	print("Using Gamepad " + str(index))
	print("_________________")
	print(gamepad.get_name())
	print("Buttons: " + str(gamepad.get_numbuttons()))
	print("Axis: " + str(gamepad.get_numaxes()))
	print("Hats: " + str(gamepad.get_numhats()))


# Initializing the first gamepad (Needs an initialized PyGame Instance
def initializeJoystick():
	if pg.joystick.get_count() < 1:
		print("Could'nt find any gamepads\nPlease connect a gamepad and try again")
		exit()
	else:
		joystick = pg.joystick.Joystick(0)
		joystick.init()
		printGamepadInformation(0, joystick)


		if joystick.get_name() == "Nintendo Switch Pro Controller":
			with open(os.path.join("nintendo.json"), 'r+') as file:
				buttons = json.load(file)
				buttons = {int(key): value for key,value in buttons.items()}

		if joystick.get_name() == "PS4 Controller":
			with open(os.path.join("ps4.json"), 'r+') as file:
				buttons = json.load(file)
				buttons = {int(key): value for key,value in buttons.items()}

		return joystick, buttons

# Prints the name of the pressed buttons as mapped in json file
def printPressedButton(joystick, buttons):
	buttonCount = joystick.get_numbuttons()
	for i in range(buttonCount):
		if joystick.get_button(i):
			if i in buttons:
				print("Button pressed: %s " %buttons[i])
				return i
			else:
				print("Button not mapped, button pressed : %s" %i)
				return i
	return -1

	# TODO: reading hat for Pro Controller
	'''			
def buttonPressed(joystick, buttons):
	buttonCount = 
	'''

# Printing the button which is pressed (used for testButtonMapping
def printAllPressedButton(joystick):
	buttonCount = joystick.get_numbuttons()
	hatCount = joystick.get_numhats()
	for i in range(buttonCount):
		if joystick.get_button(i):
			print("Button: " + str(i) + " is pressed")
	for i in range(hatCount):
		hatValue = joystick.get_hat(i)

		if (hatValue[0] != 0) or (hatValue[1] != 0):
			print("Hatvalue : " + str(joystick.get_hat(i)))



# Initializes PyGame and starts a loop for printing any button you press on the controller in the console
# TODO: Automatic Json from button pressed after asking for each button: up, down, left right and so on
def testButtonMapping():
	# Init PyGame and setting variable for running gameloop
	pg.init()
	running = True

	if pg.joystick.get_count() < 1:
		print("Could'nt find any gamepads\nPlease connect a gamepad and try again")
		exit()
	else:
		joystick = pg.joystick.Joystick(0)
		joystick.init()
		printGamepadInformation(0, joystick)

	clock = pg.time.Clock()


	screen = pg.display.set_mode([40, 40])

	# Main PyGame Loop, 30 FPS
	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					running = False
		printAllPressedButton(joystick)


		pg.display.flip()
		clock.tick(30)