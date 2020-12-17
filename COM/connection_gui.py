from tkinter import *
import threading
import time
import verbindungsTest
#import Gamepad as gp

class connectionGui:
    def __init__(self, master):
        self.master = master
        master.geometry("800x150")
        master.config(bg="grey")
        master.title("Team Rot Verbindungsmanager")
        master.resizable(False, False)

        # create labels
        self.descriptionLabel = Label(master, text="Gebe die IP-Adresse des Servers ein !")
        self.testLabel2 = Label(master, text="IP Adresse:")
        self.conLabel = Label(master, text="Verbindung nicht aufgebaut !", bg="red")
        self.placeHolder = Label(master, bg="grey")

        # arrange labels
        self.testLabel2.grid(row=2, column=0)
        self.descriptionLabel.grid(row=0, column=0)
        self.conLabel.grid(row=0, column=2)
        self.placeHolder.grid(row=1, column=1)

        # create input field
        self.ipField = Entry(master)
        self.ipField.config(width=25)

        # arrange input field
        self.ipField.grid(row=2, column=1)

        # create button
        self.connectButton = Button(master, text="Verbinden", pady=20, padx=20,
                                    command=lambda: threading.Thread(target=self.connectionClick).start())
        self.openMain = Button(master, text="Start", pady=20, padx=20, command=self.openMain)
        # arrange button
        self.connectButton.grid(row=2, column=2)

    def connectionClick(self):
        self.conLabel.config(bg="yellow", text="Verbindung wird aufgebaut")
        self.update()

        if self.ipField.get() != "":
            ipaddress = self.ipField.get()

            # call connection method
            # myGamepad = gp.Gamepad(ipaddress)
            # myGamepad.checkConnection()
            time.sleep(2)

            # checking the answer
            if (myGamepad.getConnectionStatus()):
                connectionIsPositive()
            else:
                print("Verbindungs TimeOut")
                self.conLabel.config(text="Verbindung nicht aufgebaut !", bg="red")
            # myGamepad.getControlSignals()
        else:
            print("Fehler nichts eigegeben!")
            self.conLabel.config(bg="red", text="Verbindung fehlgeschlagen")
        # del myGamepad

    def connectionIsPositive(self):
        self.conLabel.config(bg="green", text="Verbindung erfolgreich!")
        #openMain.grid(row=2, column=3)
        return

    def openMain(self):
        import main_gui



if __name__ == "__main__":
    root = Tk()
    my_gui = connectionGui(root)
    root.mainloop()