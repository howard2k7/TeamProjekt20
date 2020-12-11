from tkinter import *
import threading
import verbindungsTest
import functools
import operator

main = Tk()
main.geometry("950x500")
main.config(bg="grey")
main.title("Main Interface")
main.resizable(False, False)


def convertString(string):
    helpstr = ""
    for i in range(len(string)):
        if string[i] != "'" and string[i] != "(" and string[i] != ")" and string[i] != ",":
            helpstr = helpstr + string[i]
    return helpstr


def hoeheEinstellen():
    hoehe = 0
    write("Befehl: " + selectedHoehe.get())
    if (selectedHoehe.get() == "Höhe 1"):
        hoehe = 1
    elif (selectedHoehe.get() == "Höhe 2"):
        hoehe = 2
    elif (selectedHoehe.get() == "Höhe 3"):
        hoehe = 3
    help = verbindungsTest.hoeheStufe(hoehe)
    write(str(help))


def geschwEinstellen():
    geschw = 0
    write("Befehl: " + selectedGeschw.get())
    if (selectedGeschw.get() == "Geschwindigkeit 1"):
        geschw = 1
    elif (selectedGeschw.get() == "Geschwindigkeit 2"):
        geschw = 2
    elif (selectedGeschw.get() == "Geschwindigkeit 3"):
        geschw = 3
    help = verbindungsTest.geschwStufe(geschw)
    write(str(help))

frameTop = Frame(main, padx=50, pady=50)
frameTop.grid(row=0, column=0)
frameTopRight = Frame(main, background='black', padx=50, pady=50)
frameTopRight.grid(row=0, column=1)
frameBot = Frame(main, background='black', padx=50, pady=50)
frameBot.grid(row=1, column=0)
frameBotRight = Frame(main, padx=50, pady=50)
frameBotRight.grid(row=1, column=1)


frameTerminal = Frame(frameBotRight)
frameTerminal.grid(row=2, column=3)


output = Text(frameTerminal, width=50, height=15, background='black', fg='white')
output.pack(side=LEFT)

scrollbar = Scrollbar(frameTerminal, orient="vertical", command=output.yview)
scrollbar.pack(side=RIGHT, fill="y")

frameTerminal.count = 1
frameTerminal.configure(background='black')


def write(txt):
    output.insert(END, str(convertString(txt) + "\n"))


selectedHoehe = StringVar(main)
selectedHoehe.set("Höhe 1")
selectedGeschw = StringVar(main)
selectedGeschw.set("Geschwindigkeit 1")

dropgeschw = OptionMenu(frameTop, selectedGeschw, "Geschwindigkeit 1", "Geschwindigkeit 2", "Geschwindigkeit 3")
dropgeschw.grid(row=1, column=2)
dropgeschw.config(padx=20)
drophoehe = OptionMenu(frameTop, selectedHoehe, "Höhe 1", "Höhe 2", "Höhe 3")
drophoehe.grid(row=1, column=1)

hoeheeinstellen = Button(frameTop, text="Höhe übernehmen", pady=20, padx=20,
                         command=lambda: threading.Thread(target=hoeheEinstellen).start())
hoeheeinstellen.grid(row=2, column=1)
geschweinstellen = Button(frameTop, text="Geschwindigkeit übernehmen", pady=20, padx=20,
                          command=lambda: threading.Thread(target=geschwEinstellen).start())
geschweinstellen.grid(row=2, column=2)

write("Betriebsbereit !")
# test = Label(main, text="Test", padx=40, pady=40, width=20)
# test.grid(row=1, column=4)

main.mainloop()
