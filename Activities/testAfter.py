import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Tkinter after() Demo')
        self.geometry('300x100')

        self.style = ttk.Style(self)

        self.button = ttk.Button(self, text='Wait 3 seconds')
        self.button['command'] = self.start
        self.button.pack(expand=True, ipadx=10, ipady=5)



    def start(self):
        self.sleepTime = 3000

        self.change_button_color('red')
        self.after(3000,lambda: self.change_button_color('black'))

        self.num = 0
        self.start_time = datetime.now()
        while True:
            print(self.num)
            self.num += 1
            if self.num > 9: self.num = 0
            time.sleep(1)



    def change_button_color(self, color):
        self.style.configure('TButton', foreground=color)
        print(color)


if __name__ == "__main__":
    app = App()

    app.mainloop()
