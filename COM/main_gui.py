from tkinter import *

main = Tk()
main.geometry("800x800")
main.config(bg="grey")
main.title("Main Interface")

test = Label(main, text="Hier könnten Infos stehen", padx=40, pady=40, width=20)
test.pack()
main.mainloop()