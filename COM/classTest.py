import Gamepad as gp

print("Do it")
myGamepad = gp.Gamepad("tcp://127.0.0.1:5555")
myGamepad.getControlSignals()
print("Before del")
del myGamepad
print("After del")

