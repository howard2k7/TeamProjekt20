from tkinter import *
import threading
import time
import verbindungsTest
import Gamepad as gp

root = Tk()
root.geometry("800x150")
root.config(bg="grey")
root.title("Team Rot Verbindungsmanager")
root.resizable(False, False)





def connectionClick():
    conLabel.config(bg="yellow", text="Verbindung wird aufgebaut")
    root.update()



    if ipField.get() != "":
        ipaddress = ipField.get()

        # call connection method
        myGamepad = gp.Gamepad(ipaddress)
        myGamepad.checkConnection()
        time.sleep(2)

        # checking the answer
        if (myGamepad.getConnectionStatus()):
            connectionIsPositive()
        else:
            print("Verbindungs TimeOut")
            conLabel.config(text="Verbindung nicht aufgebaut !", bg="red")
        myGamepad.getControlSignals()
    else:
        print("Fehler nichts eigegeben!")
        conLabel.config(bg="red", text="Verbindung fehlgeschlagen")
    del myGamepad


def connectionIsPositive():
    conLabel.config(bg="green", text="Verbindung erfolgreich!")
    openMain.grid(row=2, column=3)
    return


def openMain():
    import main_gui


# create labels
descriptionLabel = Label(root, text="Gebe die IP-Adresse des Servers ein !")
testLabel2 = Label(root, text="IP Adresse:")
conLabel = Label(root, text="Verbindung nicht aufgebaut !", bg="red")
placeHolder = Label(root, bg="grey")

# arrange labels
testLabel2.grid(row=2, column=0)
descriptionLabel.grid(row=0, column=0)
conLabel.grid(row=0, column=2)
placeHolder.grid(row=1, column=1)

# create input field
ipField = Entry(root)
ipField.config(width=25)

# arrange input field
ipField.grid(row=2, column=1)

# create button
connectButton = Button(root, text="Verbinden", pady=20, padx=20,
                       command=lambda: threading.Thread(target=connectionClick).start())
openMain = Button(root, text="Start", pady=20, padx=20, command=openMain)
# arrange button
connectButton.grid(row=2, column=2)

root.mainloop()