import os
import tkinter as tk
from tkinter import messagebox
from script import *

INSTRUCTION = """

"""

class App:
    def __init__(self):
        self.root = tk.Tk()
        # self.root.iconbitmap("./assets/icon/icon.ico")
        self.root.title("Box Picker - {}".format(APP_VERSION))
        self.root.geometry("350x550")

        self.frame1 = tk.Frame(self.root)
        self.frame1.pack()

        self.howToButton = tk.Button(self.frame1, text="?", width=2, height=1, command=self.showInstruction)
        self.howToButton.pack(side=tk.TOP, anchor=tk.NE, padx=(0,20), pady=(4,0))

        self.labelFrame1 = tk.LabelFrame(self.frame1, text="Sales Quotation")
        self.labelFrame1.pack(padx=20, pady=20)

        self.inputField = tk.Entry(self.labelFrame1, font=("Arial", 10), width=50)
        self.inputField.bind("<KeyPress>", self.onEnter)
        self.inputField.pack(padx=10, pady=(5,10))

        self.submitButton = tk.Button(self.frame1, text="Pack", font=("Arial", 9), command=self.submit, width=20)
        self.submitButton.pack(padx=10, pady=0)

        self.statusMessage = tk.Label(self.frame1, text='', font=("Arial", 9))
        self.statusMessage.pack(padx=10, pady=10)

        self.labelFrame2 = tk.LabelFrame(self.frame1, text="Boxes To Use")
        self.labelFrame2.pack(padx=20, pady=20)

        self.resultsBox = tk.Text(self.labelFrame2, font=("Arial", 9), width=50)
        self.resultsBox.pack(padx=10, pady=(5,10))
        self.resultsBox.config(state=tk.DISABLED)
        
        self.root.mainloop()

    def showInstruction(self):
        messagebox.showinfo(title='Instruction', message=INSTRUCTION)

    def onEnter(self, event):
        if event.keysym == "Return":
            self.submit()

    def clearMessages(self):
        self.resultsBox.config(state=tk.NORMAL)
        self.resultsBox.delete('1.0', tk.END)
        self.resultsBox.config(state=tk.DISABLED)
        self.statusMessage.config(text="")

    def submit(self):
        self.clearMessages()
        self.statusMessage.config(text="Processing...")
        self.root.update()

        inputFilename = self.inputField.get()

        if len(inputFilename) != 0:
            response = distribute(inputFilename)

            if response["success"] is not None and not response["success"]:
                self.showStatusMessage("Error", response["errorMessage"])

            if response['results']:
                text = '\n'.join(response['results'])
                self.resultsBox.config(state=tk.NORMAL)
                self.resultsBox.insert(tk.END, text)
                self.resultsBox.config(state=tk.DISABLED)

            self.inputField.delete(0, "end")

        self.statusMessage.config(text="")

    def showStatusMessage(self, title, message):
        messagebox.showinfo(title=title, message=message)

def main():
    App()

if __name__ == "__main__":
    main()