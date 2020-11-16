import pygame as pg
from COM import joystick as joy

if __name__ == "__main__":

	pg.init()
	clock = pg.time.Clock()

	# Init Gamepad
	gamepad, buttons = joy.initializeJoystick()
	print(buttons)

	running = True
	screen = pg.display.set_mode([40,40])


	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == pg.KEYDOWN:
				if event.key == pg.K_ESCAPE:
					running = False
		joy.printPressedButton(gamepad,buttons)

		pg.display.flip()
		clock.tick(30)

