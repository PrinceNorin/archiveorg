import platform
from tkinter import filedialog, ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from .parser import AsyncFetchFile, slugify_from_url


class Window(ttk.Frame):
    def __init__(self, title: str):
        super().__init__()
        self.urls = []
        self._init_gui(title)

    def _init_gui(self, title):
        self.master.title(title)
        self.pack(fill=tk.BOTH, expand=True)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=10)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=10)
        self.config(padding=10)

        label = ttk.Label(self, text='Archive URL')
        label.grid(sticky=tk.W, pady=4, padx=5)

        self.entry = ttk.Entry(self)
        self.entry.focus()
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.E+tk.W)

        key = '<Control-KeyRelease-a>'
        if platform.system() == 'Darwin':
            key = '<Command-KeyRelease-a>'

        self.entry.bind(key, self._select_all)

        self.textarea = ScrolledText(self, state=tk.DISABLED)
        self._set_text('No file url found')
        self.textarea.grid(row=2, column=0, columnspan=2,
                           rowspan=4, padx=7, pady=7, sticky=tk.E+tk.W+tk.S+tk.N)

        self.a = ttk.Treeview(self)
        self.a.grid(row=6, column=0, columnspan=3)
        self.a.insert()

        self.get_file_btn = ttk.Button(self, text='Get File', command=self._get_files)
        self.get_file_btn.grid(row=1, column=3)

        self.save_btn = ttk.Button(self, text='Save As', state=tk.DISABLED, command=self._choose_file)
        self.save_btn.grid(row=2, column=3, pady=4)

        self.close_btn = ttk.Button(self, text='Close', command=self._close_window)
        self.close_btn.grid(row=5, column=3)

    def _select_all(self, event):
        self.entry.selection_range(0, tk.END)

    def _close_window(self):
        self.master.destroy()

    def _get_files(self):
        url = self.entry.get()
        if not url:
            return

        self.urls = []
        self.entry.config(state=tk.DISABLED)
        self._set_text(f'Fetching files from: {url}')
        self.get_file_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)

        dl_t = AsyncFetchFile(url)
        dl_t.start()
        self._monitor(dl_t)

    def _choose_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension='.txt',
            initialfile=slugify_from_url(self.entry.get()),
        )

        if not filename:
            return

        with open(filename, 'w') as f:
            f.write('\n'.join(self.urls))

    def _monitor(self, t):
        if t.is_alive():
            self.after(100, lambda: self._monitor(t))
        else:
            self.entry.config(state=tk.NORMAL)
            self.get_file_btn.config(state=tk.NORMAL)

            if len(t.urls) == 0:
                self.urls = []
                self.save_btn.config(state=tk.DISABLED)
                self._set_text('No file url found')
            else:
                self.urls = t.urls
                self.save_btn.config(state=tk.NORMAL)
                self._set_text('\n'.join(t.urls))

    def _set_text(self, content):
        self.textarea.config(state=tk.NORMAL)
        self.textarea.delete(1.0, 'end')
        self.textarea.insert('end', content)
        self.textarea.config(state=tk.DISABLED)
