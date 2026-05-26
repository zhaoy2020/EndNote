import tkinter as tk 
from tkinter import filedialog

from make_terms import JournalTermMaker


def open_file(label_widget):
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        label_widget.config(text=f"{file_path}")
    else:
        label_widget.config(text="No file selected")


def start_processing(db_label, query_label):
    if db_label.cget("text") != "Selected db file":
        term_maker = JournalTermMaker(db_label.cget("text"))
        if query_label.cget("text") != "Selected query file":
            term_maker.add_from_file(query_label.cget("text"))
            term_maker.save("updated_match_table.csv")
    else:
        tk.messagebox.showerror("Error", "Please select a db file before starting the processing.")


def main_window(root):
    db_label = tk.Label(root, text=f"Selected db file")
    query_label = tk.Label(root, text=f"Selected query file")
    db_button = tk.Button(root, text="Open db file", command=lambda: open_file(db_label))
    query_button = tk.Button(root, text="Open query file", command=lambda: open_file(query_label))
    start_button = tk.Button(root, text="Start", command=lambda: start_processing(db_label, query_label))


    db_button.grid(row=0, column=0)
    db_label.grid(row=0, column=1)
    query_button.grid(row=1, column=0)
    query_label.grid(row=1, column=1)
    start_button.grid(row=2, column=0, columnspan=2)

    return root


def main():
    '''Main function to run the GUI application.'''
    root = tk.Tk()
    root.title("Make journal term lists from WOS")
    width, height, scale = root.winfo_screenwidth(), root.winfo_screenheight(), 3
    root.geometry(f"{width//scale}x{height//scale}")

    root = main_window(root)

    root.mainloop()


if __name__ == "__main__":
    main()