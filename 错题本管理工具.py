import tkinter as tk
from tkinter import messagebox, filedialog
import os
from common_utils import (get_base_dir, get_abs_path, read_standard_csv, save_standard_csv,
                          center_window, COLOR_BG, create_title_label, create_button, create_treeview)

class WrongBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("智能错题本管理器")
        center_window(self.root, 850, 600)
        self.root.configure(bg=COLOR_BG)
        self.wrong_file = get_abs_path("错题本.csv")
        self.wrong_data = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        create_title_label(self.root, "📕 我的错题本").pack(pady=(15, 5))
        top_frame = tk.Frame(self.root, bg=COLOR_BG)
        top_frame.pack(fill="x", padx=20, pady=10)
        
        self.lbl_info = tk.Label(top_frame, text="正在加载...", font=("微软雅黑", 11), bg=COLOR_BG, fg="#666")
        self.lbl_info.pack(side="left")
        
        create_button(top_frame, "🔄 刷新", self.load_data, "primary").pack(side="right", padx=5)
        create_button(top_frame, "🗑️ 删除选中", self.delete_selected, "danger").pack(side="right", padx=5)
        create_button(top_frame, "📤 导出复习题库", self.export_for_review, "success").pack(side="right", padx=5)

        columns_config = {"type": ("分类", 100), "question": ("题目", 450), "answer": ("答案", 150)}
        tree_frame, self.tree = create_treeview(self.root, columns_config)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def load_data(self):
        if not os.path.exists(self.wrong_file):
            self.lbl_info.config(text="🎉 太棒了！错题本是空的。", fg="#388e3c")
            self.wrong_data = []; self.update_treeview(); return
        self.wrong_data = read_standard_csv(self.wrong_file)
        self.lbl_info.config(text=f"当前累计错题：{len(self.wrong_data)} 道", fg="#d32f2f")
        self.update_treeview()

    def update_treeview(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for q in self.wrong_data:
            self.tree.insert("", "end", values=(q.get("分类", "未分类"), q.get("题目", ""), q.get("答案", "")))

    def delete_selected(self):
        if not self.wrong_data: return messagebox.showinfo("提示", "错题本已经空了。")
        selected = self.tree.selection()
        if not selected: return messagebox.showwarning("提示", "请先选中你要删除的错题。")
        if not messagebox.askyesno("确认", f"确定删除选中的 {len(selected)} 道错题吗？"): return

        to_delete_questions = {self.tree.item(item, "values")[1] for item in selected}
        new_data = [q for q in self.wrong_data if q.get("题目", "") not in to_delete_questions]
        
        success, msg = save_standard_csv(new_data, self.wrong_file)
        if success: self.load_data()
        else: messagebox.showerror("失败", msg)

    def export_for_review(self):
        if not self.wrong_data: return messagebox.showwarning("提示", "错题本为空，无法导出。")
        save_path = filedialog.asksaveasfilename(title="导出", initialfile="错题复习.csv", defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if save_path:
            success, msg = save_standard_csv(self.wrong_data, save_path)
            if success: messagebox.showinfo("成功", "导出成功！可以用主程序导入了。")

if __name__ == "__main__":
    root = tk.Tk()
    app = WrongBookApp(root)
    root.mainloop()