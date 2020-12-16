import Gamepad as gp

print("Do it")
myGamepad = gp.Gamepad()
myGamepad.getControlSignals()
print("Before del")
del myGamepad
print("After del")

