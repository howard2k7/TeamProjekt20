import pygame as pg

SCREEN_WIDTH = 500
SCREEN_HIGHT = 500

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

def printControllerInfo(gamepad):
	print(gamepad.get_name())
	print("Axis:" + str(gamepad.get_numaxes()))
	print("Buttoncount: " + str(gamepad.get_numbuttons()))
	print("Hatcount: " + str(gamepad.get_numhats()))

class Player(pg.sprite.Sprite):
	def __init__(self):
		super(Player, self).__init__()
		self.surf = pg.Surface((75, 25))
		self.surf.fill((255, 255, 255))
		self.rect = self.surf.get_rect()

	def update(self, pressed_keys):
		if pressed_keys[K_UP]:
			self.rect.move_ip(0, -5)
		if pressed_keys[K_DOWN]:
			self.rect.move_ip(0, 5)
		if pressed_keys[K_LEFT]:
			self.rect.move_ip(-5, 0)
		if pressed_keys[K_RIGHT]:
			self.rect.move_ip(5, 0)

		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.right > SCREEN_WIDTH:
			self.rect.right = SCREEN_WIDTH
		if self.rect.top <= 0:
			self.rect.top = 0
		if self.rect.bottom >= SCREEN_HIGHT:
			self.rect.bottom = SCREEN_HIGHT

	def update_controller(self, gamepad):
		if gamepad.get_button(11):
			self.rect.move_ip(0,-5)
		if gamepad.get_button(12):
			self.rect.move_ip(0,5)
		if gamepad.get_button(13):
			self.rect.move_ip(-5,0)
		if gamepad.get_button(14):
			self.rect.move_ip(5,0)



if __name__ == "__main__":

	pg.init()
	fps = pg.time.Clock()

	controller_count = pg.joystick.get_count()

	if controller_count < 1:
		print("No game controller(s) found!")
		exit()
	else:
		controller = pg.joystick.Joystick(0)
		controller.init()
		printControllerInfo(controller)

	Robot = Player()

	screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HIGHT])
	running = True



	while running:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				running = False
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					running = False

		pressed_keys = pg.key.get_pressed()

		'''for i in range (0,15):
			if controller.get_button(i):
				print("Pressing: " + str(i))'''
		Robot.update_controller(controller)
		Robot.update(pressed_keys)

		#Robot.controller_update(controller)

		screen.fill((0,0,0))
		surf = pg.Surface((50,50))

		#surf.fill((255,255,255))
		#rect = surf.get_rect()

		screen.blit(Robot.surf, Robot.rect)

		pg.display.flip()

		fps.tick(60)

	pg.quit()


