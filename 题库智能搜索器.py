import tkinter as tk
from tkinter import filedialog
from common_utils import (center_window, read_standard_csv, get_abs_path, clean_text_ultra, 
                          COLOR_BG, create_normal_label, create_button, create_treeview)

class SearchToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("华为ICT题库 - 智能搜索器")
        center_window(self.root, 850, 600)
        self.root.configure(bg=COLOR_BG)
        
        # 默认先读同目录，如果没找到就是空的
        self.all_data = read_standard_csv(get_abs_path("ict_questions.csv"))
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=20, pady=15)
        
        create_button(top_frame, "📂 导入题库文件", self.load_custom_file, "warning").pack(side="left", padx=(0, 20))
        
        create_normal_label(top_frame, "输入关键字:").pack(side="left")
        self.entry_keyword = tk.Entry(top_frame, font=("微软雅黑", 14), width=30)
        self.entry_keyword.pack(side="left", padx=10)
        self.entry_keyword.bind("<KeyRelease>", self.on_search)
        
        self.lbl_count = create_normal_label(top_frame, "共 0 条结果")
        self.lbl_count.pack(side="right")

        columns_config = {"type": ("分类", 100), "question": ("题目", 450), "answer": ("答案", 150)}
        tree_frame, self.tree = create_treeview(self.root, columns_config)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.update_treeview(self.all_data)

    def load_custom_file(self):
        file_path = filedialog.askopenfilename(title="选择题库", filetypes=[("CSV 文件", "*.csv")])
        if file_path:
            self.all_data = read_standard_csv(file_path)
            self.entry_keyword.delete(0, tk.END)
            self.update_treeview(self.all_data)

    def on_search(self, event):
        keyword = clean_text_ultra(self.entry_keyword.get().strip())
        if not keyword:
            results = self.all_data
        else:
            results = [q for q in self.all_data if keyword in clean_text_ultra(str(q.get("题目", "")) + str(q.get("选项", "")) + str(q.get("答案", "")))]
        self.update_treeview(results)

    def update_treeview(self, data):
        for item in self.tree.get_children(): self.tree.delete(item)
        for q in data:
            self.tree.insert("", "end", values=(q.get("分类", "未分类"), q.get("题目", ""), q.get("答案", "")))
        self.lbl_count.config(text=f"共 {len(data)} 条结果")

if __name__ == "__main__":
    root = tk.Tk()
    app = SearchToolApp(root)
    root.mainloop()