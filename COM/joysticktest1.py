import pygame
import math

pygame.init()
j = pygame.joystick.Joystick(0)
j.init()



try:
    while True:
        events = pygame.event.get()
        running = True
        for event in events:
            if event.type == pygame.JOYAXISMOTION:
                print(event.axis, round(event.value, 1))
            elif event.type == pygame.JOYBALLMOTION:
                print(event.ball, event.rel)
            elif event.type == pygame.JOYBUTTONDOWN:
                print(event.button, 'pressed')
            elif event.type == pygame.JOYBUTTONUP:
                print(event.button, 'released')
            elif event.type == pygame.JOYHATMOTION:
                print(event.hat, event.value)

            mainClock = pygame.time.Clock()
            mainClock.tick(3)



except KeyboardInterrupt:
    print("EXITING NOW")
    j.quit()