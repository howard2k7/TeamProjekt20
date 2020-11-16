import pygame as pg
import joystick as joy

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

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
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False
		joy.printPressedButton(gamepad,buttons)

		pg.display.flip()
		clock.tick(30)

