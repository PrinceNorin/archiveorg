import tkinter as tk

from app.gui import Window


def main():
    app = tk.Tk()
    app.resizable(0, 0)
    app.geometry('1080x720+300+300')

    Window('Archive File')
    app.mainloop()


if __name__ == '__main__':
    main()
