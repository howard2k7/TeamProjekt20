from tkinter import *
import threading
import verbindungsTest

main = Tk()
main.geometry("950x500")
main.config(bg="grey")
main.title("Main Interface")
main.resizable(False, False)


def convertString(string):
    helpStr = ""
    for i in range(len(string)):
        if string[i] != "'" and string[i] != "(" and string[i] != ")" and string[i] != ",":
            helpStr = helpStr + string[i]
    return helpStr


def heightSelect():
    height = 0
    write("Befehl: " + selectedHeight.get())
    if selectedHeight.get() == "Höhe 1":
        height = 1
    elif selectedHeight.get() == "Höhe 2":
        height = 2
    elif selectedHeight.get() == "Höhe 3":
        height = 3
        # call heightSelect method with height
    help = verbindungsTest.hoeheStufe(height)
    write(str(help))


def paceSelect():
    pace = 0
    write("Befehl: " + selectedPace.get())
    if selectedPace.get() == "Geschwindigkeit 1":
        pace = 1
    elif selectedPace.get() == "Geschwindigkeit 2":
        pace = 2
    elif selectedPace.get() == "Geschwindigkeit 3":
        pace = 3
        # call paceSelect method with pace
    help = verbindungsTest.geschwStufe(pace)
    write(str(help))

# building frame grid
frameTop = Frame(main, padx=50, pady=50)
frameTop.grid(row=0, column=0)
frameTopRight = Frame(main, background='black', padx=50, pady=50)
frameTopRight.grid(row=0, column=1)
frameBot = Frame(main, background='black', padx=50, pady=50)
frameBot.grid(row=1, column=0)
frameBotRight = Frame(main, padx=50, pady=50)
frameBotRight.grid(row=1, column=1)

# frame for terminal
frameTerminal = Frame(frameBotRight)
frameTerminal.grid(row=2, column=3)

# create terminal output
output = Text(frameTerminal, width=50, height=15, background='black', fg='white')
output.pack(side=LEFT)

# create scrollbar
scrollbar = Scrollbar(frameTerminal, orient="vertical", command=output.yview)
scrollbar.pack(side=RIGHT, fill="y")

# terminal configuration
frameTerminal.count = 1
frameTerminal.configure(background='black')


def write(txt):
    output.insert(END, str(convertString(txt) + "\n"))

# initial set for variables
selectedHeight = StringVar(main)
selectedHeight.set("Höhe 1")
selectedPace = StringVar(main)
selectedPace.set("Geschwindigkeit 1")

# creating drop menus
dropPace = OptionMenu(frameTop, selectedPace, "Geschwindigkeit 1", "Geschwindigkeit 2", "Geschwindigkeit 3")
dropPace.grid(row=1, column=2)
dropPace.config(padx=20)
dropHeight = OptionMenu(frameTop, selectedHeight, "Höhe 1", "Höhe 2", "Höhe 3")
dropHeight.grid(row=1, column=1)

# creating Buttons
heightSelectedButton = Button(frameTop, text="Höhe übernehmen", pady=20, padx=20,
                              command=lambda: threading.Thread(target=heightSelect).start())
heightSelectedButton.grid(row=2, column=1)
paceSelectedButton = Button(frameTop, text="Geschwindigkeit übernehmen", pady=20, padx=20,
                            command=lambda: threading.Thread(target=paceSelect).start())
paceSelectedButton.grid(row=2, column=2)

# initial terminal message
write("Betriebsbereit !")

main.mainloop()
