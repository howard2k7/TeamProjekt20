import pygame
import math

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()
try:
    while True:
        events = pygame.event.get()
        running = True
        info = ('-round(j.get_axis(0), 1)', ' -round(j.get_axis(1), 1')
        print= info



except KeyboardInterrupt:
    print("EXITING NOW")
    j.quit()