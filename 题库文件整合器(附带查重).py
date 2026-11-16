import tkinter as tk
from tkinter import filedialog, messagebox
import os
from common_utils import (get_base_dir, read_standard_csv, center_window, save_standard_csv,
                          clean_text_ultra, COLOR_BG, create_title_label, create_button)

class MergeToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("华为ICT题库 - 智能整合工具")
        center_window(self.root, 700, 500)
        self.root.configure(bg=COLOR_BG)
        self.selected_files = []
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        top_frame.pack(fill="x", padx=20)
        
        create_button(top_frame, "📂 添加题库文件 (可多选)", self.ui_add_files).pack(side="left")
        create_button(top_frame, "🗑️ 清空列表", self.ui_clear_files, "danger").pack(side="left", padx=10)

        mid_frame = tk.Frame(self.root)
        mid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(mid_frame, text="已加载的文件队列：", font=("微软雅黑", 10), bg=COLOR_BG).pack(anchor="w")
        self.file_listbox = tk.Listbox(mid_frame, font=("微软雅黑", 11), selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill="both", expand=True, pady=5)

        bottom_frame = tk.Frame(self.root, bg=COLOR_BG, pady=10)
        bottom_frame.pack(fill="x", padx=20)

        self.lbl_status = tk.Label(bottom_frame, text="请添加文件...", font=("微软雅黑", 11), bg=COLOR_BG, fg="#555")
        self.lbl_status.pack(side="left")

        create_button(bottom_frame, "🚀 开始合并并去重", self.ui_start_merge, "success").pack(side="right")

    def ui_add_files(self):
        file_paths = filedialog.askopenfilenames(title="选择题库文件", filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")])
        if not file_paths: return
        for path in file_paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_listbox.insert(tk.END, os.path.basename(path))
        self.update_status()

    def ui_clear_files(self):
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_status()

    def update_status(self):
        self.lbl_status.config(text=f"当前已加载 {len(self.selected_files)} 个文件。")

    def ui_start_merge(self):
        if not self.selected_files:
            messagebox.showwarning("提示", "请先添加至少一个文件！")
            return

        self.lbl_status.config(text="⏳ 正在疯狂查重合并中...", fg="#FF9800")
        self.root.update()
        
        all_questions, seen_questions = [], set()
        total_read, duplicate_count = 0, 0

        for path in self.selected_files:
            file_data = read_standard_csv(path)
            if not file_data: continue
                
            for q in file_data:
                total_read += 1
                # 核心：调用通用库的全方位清洗查重
                q_text_normalized = clean_text_ultra(q.get("题目", ""))
                
                if q_text_normalized in seen_questions:
                    duplicate_count += 1
                    continue
                    
                seen_questions.add(q_text_normalized)
                all_questions.append(q)

        if not all_questions:
            messagebox.showwarning("提示", "合并失败，没有读取到有效数据。")
            self.update_status()
            return

        save_path = filedialog.asksaveasfilename(
            title="保存合并后的题库", initialdir=get_base_dir(),
            initialfile="合并题库.csv", defaultextension=".csv", filetypes=[("CSV 文件", "*.csv")]
        )
        if not save_path: return

        success, msg = save_standard_csv(all_questions, save_path)
        if success:
            self.lbl_status.config(text="✅ 合并完成！", fg="#4CAF50")
            messagebox.showinfo("合并报告", f"合并成功！\n\n📥 共读取原始题目：{total_read} 道\n✂️ 剔除重复题目：{duplicate_count} 道\n🏆 最终保留题目：{len(all_questions)} 道\n\n文件已保存至：\n{save_path}")
        else:
            messagebox.showerror("保存失败", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = MergeToolApp(root)
    root.mainloop()