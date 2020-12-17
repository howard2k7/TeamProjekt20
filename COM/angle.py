import pygame
import math


pygame.init()
j = pygame.joystick.Joystick(0)
j.init()

#Geschwindigkeit(a):

a = j.get_axis(1) #mit a als Y-Achse
a = -round(a,1) #rundet auf die erste Nachkommastelle
#a = -a
print(abs(a)) #abs a gibt die Geschwindigkeit von 0 bis 1 an

b = j.get_axis(0) #mit b als X-Achse
b = -round(b,1)



#Winkel
c = round(math.atan2(a,b)*180/(math.pi)-90 ,0) #
if c < 0:
    c += 360
c = round(c, 0) #rundet auf ganze Zahl
print(c)

gp = j.get_name()
print(gp)





