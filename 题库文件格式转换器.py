import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import traceback

try:
    import pandas as pd
except ImportError:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("缺少组件", "您的电脑缺少 pandas 库！\n请先运行 pip install pandas openpyxl")
    exit()

from common_utils import center_window, get_base_dir, save_standard_csv, COLOR_BG, create_button

def read_data_from_file(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".xlsx", ".xls"]: df = pd.read_excel(file_path)
        elif ext == ".csv":
            try: df = pd.read_csv(file_path, encoding="utf-8-sig")
            except UnicodeDecodeError: df = pd.read_csv(file_path, encoding="gbk")
        elif ext == ".txt":
            try:
                df = pd.read_csv(file_path, sep="\t", encoding="utf-8-sig")
                if len(df.columns) == 1: df = pd.read_csv(file_path, sep=",", encoding="utf-8-sig")
            except Exception: df = pd.read_csv(file_path, encoding="gbk")
        else: return None
        return df.fillna("")
    except Exception: return None

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("华为ICT题库 - 万能格式转换器")
        center_window(self.root, 850, 600)
        self.root.configure(bg=COLOR_BG)
        self.df = None
        self.columns = []
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg=COLOR_BG, pady=15)
        top_frame.pack(fill="x", padx=20)
        create_button(top_frame, "📂 1. 选择源文件", self.ui_load_file).pack(side="left")
        self.lbl_file = tk.Label(top_frame, text="未选择文件", font=("微软雅黑", 11), bg=COLOR_BG, fg="#555")
        self.lbl_file.pack(side="left", padx=15)

        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill="both", expand=True, padx=20)
        self.tree = ttk.Treeview(mid_frame, show="headings", height=8)
        self.tree.pack(fill="both", expand=True, pady=5)

        bottom_frame = tk.LabelFrame(self.root, text=" ⚙️ 2. 字段映射配置 ", font=("微软雅黑", 12, "bold"), bg=COLOR_BG)
        bottom_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Label(bottom_frame, text="题目列:", bg=COLOR_BG).grid(row=0, column=0, pady=10)
        self.combo_q = ttk.Combobox(bottom_frame, state="readonly", width=20)
        self.combo_q.grid(row=0, column=1)
        tk.Label(bottom_frame, text="选项列:", bg=COLOR_BG).grid(row=0, column=2)
        self.combo_o = ttk.Combobox(bottom_frame, state="readonly", width=20)
        self.combo_o.grid(row=0, column=3)
        tk.Label(bottom_frame, text="答案列:", bg=COLOR_BG).grid(row=1, column=0, pady=10)
        self.combo_a = ttk.Combobox(bottom_frame, state="readonly", width=20)
        self.combo_a.grid(row=1, column=1)
        tk.Label(bottom_frame, text="分类列:", bg=COLOR_BG).grid(row=1, column=2)
        self.combo_c = ttk.Combobox(bottom_frame, state="readonly", width=20)
        self.combo_c.grid(row=1, column=3)

        create_button(self.root, "🚀 3. 转换并导出", self.ui_export_csv, "success").pack(pady=10)

    def ui_load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("表格", "*.xlsx *.xls *.csv *.txt")])
        if not file_path: return
        self.lbl_file.config(text=os.path.basename(file_path))
        self.df = read_data_from_file(file_path)
        if self.df is None: return messagebox.showwarning("提示", "读取失败，请检查文件是否被占用或格式错误。")
        self.show_preview()
        self.setup_mapping()

    def show_preview(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        self.columns = list(self.df.columns)
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        for _, row in self.df.head(10).iterrows():
            self.tree.insert("", "end", values=[str(row[col])[:30] for col in self.columns])

    def setup_mapping(self):
        def guess_col(keywords, default=0):
            for i, col in enumerate(self.columns):
                for kw in keywords:
                    if kw in str(col): return i
            return default
        self.combo_q["values"] = self.columns; self.combo_q.current(guess_col(["题", "问", "内容"]))
        self.combo_a["values"] = self.columns; self.combo_a.current(guess_col(["答", "正确"]))
        self.combo_o["values"] = ["无"] + self.columns; self.combo_o.current(0)
        self.combo_c["values"] = ["自动识别"] + self.columns; self.combo_c.current(0)

    def ui_export_csv(self):
        if self.df is None: return
        q_col, a_col, o_col, c_col = self.combo_q.get(), self.combo_a.get(), self.combo_o.get(), self.combo_c.get()
        if not q_col or not a_col: return messagebox.showerror("错误", "题目和答案必选！")

        result_data = []
        for _, row in self.df.iterrows():
            question, answer = str(row[q_col]).strip(), str(row[a_col]).strip()
            options = str(row[o_col]).strip() if o_col != "无" else "无"
            if not question or not answer: continue
                
            category = str(row[c_col]).strip() if c_col != "自动识别" else "未分类"
            if c_col == "自动识别":
                # 修复 √ 和 × 的识别
                if answer.upper() in ["对", "错", "正确", "错误", "T", "F", "√", "×"]: category = "判断题"
                elif len(answer) == 1 and answer.upper() in "ABCDEF": category = "单选题"
                elif len(answer) > 1 and all(c in "ABCDEF" for c in answer.upper()): category = "多选题"
                elif len(answer) > 10: category = "计算/解答题"

            if category == "判断题":
                # 修复 √ 和 × 的转换
                if answer.upper() in ["T", "TRUE", "对", "正确", "√"]: answer = "正确"
                elif answer.upper() in ["F", "FALSE", "错", "错误", "×"]: answer = "错误"

            result_data.append({"分类": category, "题目": question, "选项": options, "答案": answer})

        if not result_data: return messagebox.showwarning("警告", "没有有效数据。")

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="ict_questions.csv", initialdir=get_base_dir(), filetypes=[("CSV", "*.csv")])
        if save_path:
            success, msg = save_standard_csv(result_data, save_path)
            if success: messagebox.showinfo("成功", f"转换完成！共 {len(result_data)} 题。")
            else: messagebox.showerror("失败", msg)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ConverterApp(root)
        root.mainloop()
    except Exception as e:
        # 如果打不开，自动弹出报错并把日志写到文件里
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("程序崩溃", f"发生了错误：{e}\n详情已写入 error_log.txt")