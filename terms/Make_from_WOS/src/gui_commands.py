import sys
import threading
from loguru import logger 

import tkinter as tk 
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from make_terms import JournalTermMaker


# =========================
# 输出重定向类（print + loguru）
# =========================
class GuiOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if message.strip():
            self.text_widget.after(0, lambda: (
                self.text_widget.insert(tk.END, message),
                self.text_widget.see(tk.END)
            ))

    def flush(self):
        pass


# =========================
# 文件选择
# =========================
def open_file(label_widget):
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[
            ('Excel files', "*.xlsx"),
            ("Text files", "*.txt"), 
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ]
    )

    if file_path:
        label_widget.config(text=f"{file_path}")
    else:
        label_widget.config(text="No file selected")
    
    return None 


def save_file(label_widget):
    file_path = filedialog.asksaveasfilename(
        title="Save file as",
        defaultextension=".csv",
        filetypes=[
            ('Excel files', "*.xlsx"),
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ]
    )

    if file_path:
        label_widget.config(text=f"{file_path}")
    else:
        label_widget.config(text="No file selected")
    
    return None


# =========================
# 核心处理逻辑（放到线程里）
# =========================
def start_processing(db_label, query_label, output_label):
    def task():
        try:
            if db_label.cget("text") != "Selected db file":
                term_maker = JournalTermMaker(db_label.cget("text"))
                logger.info("已加载数据库文件")

                if query_label.cget("text") != "Selected query file":
                    logger.info("开始处理 query 文件...")
                    term_maker.add_from_file(query_label.cget("text"))

                logger.info(f'Total | Query | Added: {term_maker.match_table.shape[0]} | {term_maker.query_terms_table.shape[0]} | {term_maker.match_table.shape[0] - term_maker.raw_match_table.shape[0]}')
        
                logger.info("开始保存结果...")
                term_maker.save(output_label.cget("text"))
                logger.info("处理完成！")

            else:
                messagebox.showerror("Error", "Please select a db file before starting the processing.")
        except Exception as e:
            logger.exception("处理过程中发生错误")

    # ✅ 放到线程，防止 GUI 卡死
    threading.Thread(target=task, daemon=True).start()


class GUI:
    def __init__(self, root):
        self.root = root
        root.title('Journal Term Maker')
        root.geometry('800x600')
        root.minsize(800, 600)

        # === Layout ===
        root.rowconfigure(0, weight=0) # File selection row
        root.rowconfigure(1, weight=1) # Log text
        root.rowconfigure(2, weight=0) # status bar row
        root.columnconfigure(0, weight=0)
        root.columnconfigure(1, weight=1) # Log text column

        # === Create widgets ===
        self.create_title()
        self.create_file_selection()
        self.create_log_text()
        self.create_status_bar()

        return None 
    
    def create_title(self):
        title = tk.Frame(self.root, bg='lightgray', height=100)
        title.grid(row=0, column=0, columnspan=2, sticky='ew')
        tk.Label(title, text="Journal Term Maker", bg='lightgray', font=("Arial", 16)).pack(pady=10)
    
    def create_file_selection(self):
        file_selection = tk.Frame(self.root, bg='#f0f0f0', width=200)
        file_selection.grid(row=1, column=0, sticky='nsew')

        file_selection.rowconfigure(0, weight=0)
        file_selection.rowconfigure(1, weight=0)
        file_selection.rowconfigure(2, weight=0)
        file_selection.rowconfigure(3, weight=0)
        file_selection.rowconfigure(4, weight=1) # Spacer row to push buttons to top
        file_selection.columnconfigure(0, weight=0)
        file_selection.columnconfigure(1, weight=0)

        db_button = tk.Button(file_selection, text="Open db file", command=lambda: open_file(db_label))
        query_button = tk.Button(file_selection, text="Open query file", command=lambda: open_file(query_label))
        output_button = tk.Button(file_selection, text="Output file", command=lambda: save_file(output_label))
        db_label = tk.Label(file_selection, text="Selected db file", anchor='w', justify='right', width=30)
        query_label = tk.Label(file_selection, text="Selected query file", anchor='w', justify='right', width=30)
        output_label = tk.Label(file_selection, text="Selected output file", anchor='w', justify='right', width=30)
        start_button = tk.Button(file_selection, text="Start", command=lambda: start_processing(db_label, query_label, output_label))
    
        db_button.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        query_button.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        output_button.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        db_label.grid(row=0, column=1, padx=5, pady=5)
        query_label.grid(row=1, column=1, padx=5, pady=5)
        output_label.grid(row=2, column=1, padx=5, pady=5)
        start_button.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)


        return None
    
    def create_log_text(self):
        log = tk.Frame(self.root, bg='white')
        log.grid(row=1, column=1, sticky='nsew')
        self.long_text = ScrolledText(log, font=("Arial", 10))
        self.long_text.pack(fill='both', expand=True)

        # =========================
        # 重定向输出
        # =========================
        gui_output = GuiOutput(self.long_text)

        # 捕获 print
        sys.stdout = gui_output
        sys.stderr = gui_output

        # 捕获 loguru
        logger.remove()
        logger.add(gui_output, level="DEBUG")

        # （可选）保留终端输出
        logger.add(sys.__stdout__, level="DEBUG")

        return None
    
    def create_status_bar(self):
        status_bar = tk.Frame(self.root, bg='lightgray', height=30)
        status_bar.grid(row=2, column=0, columnspan=2, sticky='ew')
        tk.Label(status_bar, text="Ready", bg='lightgray').pack(side='left', padx=5)

        return None
    

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()