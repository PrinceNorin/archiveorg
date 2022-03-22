import platform
from tkinter import filedialog, ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from .parser import AsyncFetchFile, slugify_from_url


class Window(ttk.Frame):
    def __init__(self, title: str):
        super().__init__()
        self.files = []
        self._init_gui(title)

    def _init_gui(self, title):
        self.master.title(title)
        self.pack(fill=tk.BOTH, expand=True)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=10)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=10)
        self.config(padding=10)

        self._build_input_section()
        self._build_table_section()
        self._build_button_section()

    def _build_input_section(self):
        label = ttk.Label(self, text='Archive URL')
        label.grid(sticky=tk.W, pady=4, padx=5)

        self.entry = ttk.Entry(self)
        self.entry.focus()
        self.entry.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.E+tk.W)

        key = '<Control-KeyRelease-a>'
        if platform.system() == 'Darwin':
            key = '<Command-KeyRelease-a>'

        self.entry.bind(key, self._select_all)

    def _build_table_section(self):
        columns = ['filename', 'size']
        self.table = ttk.Treeview(self)
        self.table.config(columns=columns)
        self.table.grid(row=2, column=0, columnspan=2,
            rowspan=4, padx=7, pady=7, sticky=tk.E+tk.W+tk.S+tk.N)

        self.table.column('#0', width=0, stretch=tk.NO)
        self.table.column('filename', anchor=tk.NW)
        self.table.column('size', width=5, anchor=tk.CENTER)

        self.table.heading('#0', text='')
        self.table.heading('filename', text='Filename', anchor=tk.NW)
        self.table.heading('size', text='Size', anchor=tk.CENTER)

    def _build_button_section(self):
        self.get_file_btn = ttk.Button(self, text='Get File', command=self._get_files)
        self.get_file_btn.grid(row=1, column=3)

        self.save_btn = ttk.Button(self, text='Save As', state=tk.DISABLED, command=self._choose_file)
        self.save_btn.grid(row=2, column=3, pady=4)

        self.close_btn = ttk.Button(self, text='Close', command=self._close_window)
        self.close_btn.grid(row=5, column=3)

    #
    # event handlers section
    #

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
        self._clear_all_rows()
        self._add_row([f'Fetching files from {url}', 0])
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
            urls = [file['url'] for file in self.files]
            f.write('\n'.join(urls))

    def _monitor(self, t):
        if t.is_alive():
            self.after(100, lambda: self._monitor(t))
        else:
            self.entry.config(state=tk.NORMAL)
            self.get_file_btn.config(state=tk.NORMAL)

            if len(t.files) == 0:
                self.files = []
                self.save_btn.config(state=tk.DISABLED)
                self._clear_all_rows()
                self._add_row(['No file url found', 0])
            else:
                self.files = t.files
                self.save_btn.config(state=tk.NORMAL)
                self._clear_all_rows()

                for file in t.files:
                    filename = file['filename']
                    self._add_row([filename, file['size']])

    def _add_row(self, row):
        self.table.insert(parent='', index='end', text='', values=row)

    def _clear_all_rows(self):
        for row in self.table.get_children():
            self.table.delete(row)
