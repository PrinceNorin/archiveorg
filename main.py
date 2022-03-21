import tkinter as tk

from app.gui import Window


def main():
    app = tk.Tk()
    app.resizable(0, 0)
    app.geometry('720x480+300+300')
    w = Window('Archive File')
    app.mainloop()


if __name__ == '__main__':
    main()
