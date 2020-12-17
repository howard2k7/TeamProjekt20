from tkinter import *
import threading
import verbindungsTest


class mainGui:
    def __init__(self, master):
        self.master = master
        master.geometry("1100x500")
        master.config(bg="grey")
        master.title("Main Interface")
        master.resizable(False, False)

        #building frame grid
        self.frameTop = Frame(master, padx=50, pady=50)
        self.frameTop.grid(row=0, column=0)
        self.frameTopRight = Frame(master, background='black', padx=50, pady=50)
        self.frameTopRight.grid(row=0, column=1)
        self.frameBot = Frame(master, background='black', padx=50, pady=50)
        self.frameBot.grid(row=1, column=0)
        self.frameBotRight = Frame(master, padx=50, pady=50)
        self.frameBotRight.grid(row=1, column=1)

        # frame for terminal
        self.frameTerminal = Frame(self.frameBotRight)
        self.frameTerminal.grid(row=2, column=3)
        self.frameTerminal.configure(background='black')

        # create scrollbar
        self.scrollbar = Scrollbar(self.frameTerminal)
        self.scrollbar.pack(side=RIGHT, fill="y")

        # create output
        self.output = Listbox(self.frameTerminal, yscrollcommand=self.scrollbar.set , width=50, height=15, background='black', fg='white')
        self.output.pack(side=LEFT)
        self.scrollbar.config(command=self.output.yview)

        # initial set for variables
        self.selectedHeight = StringVar(main)
        self.selectedHeight.set("Höhe 1")
        self.selectedPace = StringVar(main)
        self.selectedPace.set("Geschwindigkeit 1")

        # creating drop menus
        self.dropPace = OptionMenu(self.frameTop, self.selectedPace, "Geschwindigkeit 1", "Geschwindigkeit 2", "Geschwindigkeit 3")
        self.dropPace.grid(row=1, column=2)
        self.dropPace.config(padx=20)
        self.dropHeight = OptionMenu(self.frameTop, self.selectedHeight, "Höhe 1", "Höhe 2", "Höhe 3")
        self.dropHeight.grid(row=1, column=1)

        # creating Buttons
        self.heightSelectedButton = Button(self.frameTop, text="Höhe übernehmen", pady=20, padx=20, command=lambda: threading.Thread(target=self.heightSelect).start())
        self.heightSelectedButton.grid(row=2, column=1)
        self.paceSelectedButton = Button(self.frameTop, text="Geschwindigkeit übernehmen", pady=20, padx=20, command=lambda: threading.Thread(target=self.paceSelect).start())
        self.paceSelectedButton.grid(row=2, column=2)

        # initial terminal message
        self.write("Betriebsbereit !")


    def convertString(self, string):
        helpStr = ""
        for i in range(len(string)):
            if string[i] != "'" and string[i] != "(" and string[i] != ")" and string[i] != ",":
                helpStr = helpStr + string[i]
        return helpStr


    def heightSelect(self):
        height = 0
        self.write("Befehl: " + self.selectedHeight.get())
        if self.selectedHeight.get() == "Höhe 1":
            height = 1
        elif self.selectedHeight.get() == "Höhe 2":
            height = 2
        elif self.selectedHeight.get() == "Höhe 3":
            height = 3
            # call heightSelect method with height
        help = verbindungsTest.hoeheStufe(height)
        self.write(str(help))


    def paceSelect(self):
        pace = 0
        self.write("Befehl: " + self.selectedPace.get())
        if self.selectedPace.get() == "Geschwindigkeit 1":
            pace = 1
        elif self.selectedPace.get() == "Geschwindigkeit 2":
            pace = 2
        elif self.selectedPace.get() == "Geschwindigkeit 3":
            pace = 3
        # call paceSelect method with pace
        help = verbindungsTest.geschwStufe(pace)
        self.write(str(help))

    def write(self, txt):
        self.output.insert(END, str(self.convertString(txt) + "\n"))


if __name__ == "__main__":
    main = Tk()
    my_maingui = mainGui(main)
    main.mainloop()
