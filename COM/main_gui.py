from tkinter import *
import threading
import verbindungsTest
# tupel to string imports
import functools
import operator

main = Tk()
main.geometry("1100x800")
main.config(bg="grey")
main.title("Main Interface")
main.resizable(False, False)


def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str


def hoeheEinstellen():
    hoehe = 0
    write(selectedHoehe.get())
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
    write(selectedGeschw.get())
    if (selectedGeschw.get() == "Geschwindigkeit 1"):
        geschw = 1
    elif (selectedGeschw.get() == "Geschwindigkeit 2"):
        geschw = 2
    elif (selectedGeschw.get() == "Geschwindigkeit 3"):
        geschw = 3
    help = verbindungsTest.geschwStufe(geschw)
    write(str(help))


frame = Frame(main)
frame.grid(row=2, column=3)

output = Text(frame, width=50, height=15, background='black', fg='white')
output.pack(side=LEFT)

scrollbar = Scrollbar(frame, orient="vertical", command=output.yview)
scrollbar.pack(side=RIGHT, fill="y")

frame.count = 1
frame.configure(background='black')


def write(txt):
    output.insert(END, str(txt + "\n"))


selectedHoehe = StringVar(main)
selectedHoehe.set("Höhe 1")
selectedGeschw = StringVar(main)
selectedGeschw.set("Geschwindigkeit 1")

dropgeschw = OptionMenu(main, selectedGeschw, "Geschwindigkeit 1", "Geschwindigkeit 2", "Geschwindigkeit 3")
dropgeschw.grid(row=1, column=2)
dropgeschw.config(padx=20)
drophoehe = OptionMenu(main, selectedHoehe, "Höhe 1", "Höhe 2", "Höhe 3")
drophoehe.grid(row=1, column=1)

hoeheeinstellen = Button(main, text="Höhe übernehmen", pady=20, padx=20,
                         command=lambda: threading.Thread(target=hoeheEinstellen).start())
hoeheeinstellen.grid(row=2, column=1)
geschweinstellen = Button(main, text="Geschwindigkeit übernehmen", pady=20, padx=20,
                          command=lambda: threading.Thread(target=geschwEinstellen).start())
geschweinstellen.grid(row=2, column=2)

write("Test")
# test = Label(main, text="Test", padx=40, pady=40, width=20)
# test.grid(row=1, column=4)

main.mainloop()
