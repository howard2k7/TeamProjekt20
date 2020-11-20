from tkinter import *
import threading
import time
import verbindungsTest

root = Tk()
root.geometry("800x150")
root.config(bg="grey")
root.title("Team Rot Verbindungsmanager")

def verbindungsClick():
    vbLabel.config(bg="yellow", text="Verbindung wird aufgebaut")
    root.update()

    if(ipFeld.get() != ""):
        ipadresse = ipFeld.get()

        #Aufruf der Verbindungsmethode
        verbindungsTest.verbinde(ipadresse)
        time.sleep(5)

        #überprüfung der Antwort
        if (verbindungsTest.testVerbunden() == True):
            verbindungIstPositiv()
        else:
            print("Verbindungs TimeOut")
            vbLabel.config(text="Verbindung nicht aufgebaut !", bg="red")

    else:
        print("Fehler nichts eigegeben!")
        vbLabel.config(bg="red", text="Verbindung fehlgeschlagen")

def verbindungIstPositiv():
    vbLabel.config(bg="green", text="Verbindung erfolgreich!")
    openMain.grid(row=2, column=3)
    return

#Label erstellen
beschreibungLabel = Label(root, text="Gebe die IP-Adresse des Servers ein !")
testLabel2 = Label(root, text="IP Adresse:")
vbLabel = Label(root, text="Verbindung nicht aufgebaut !", bg="red")
platzHalter = Label(root, bg="grey")

#Label anordnen
testLabel2.grid(row=2, column=0)
beschreibungLabel.grid(row=0, column=0)
vbLabel.grid(row=0, column=2)
platzHalter.grid(row=1, column=1)

#Inputfeld erstellen
ipFeld = Entry(root)
ipFeld.config(width=25)

#Iputfeld anordnen
ipFeld.grid(row=2, column=1)

#Button erstellen
connectButton = Button(root, text="Verbinden", pady=20, padx=20, command=lambda:threading.Thread(target=verbindungsClick).start())
openMain = Button(root, text="Start", pady=20, padx=20)
#Button anordnen
connectButton.grid(row=2, column=2)


root.mainloop()

