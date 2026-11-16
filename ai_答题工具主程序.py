import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import subprocess
import os
import sys
from common_utils import (get_base_dir, get_abs_path, read_standard_csv, center_window, 
                          format_answer_ultra, append_wrong_question, COLOR_BG, COLOR_PRIMARY,
                          create_title_label, create_button)

class ICTHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("华为ICT校赛 - 刷题助手 (插件版)")
        center_window(self.root, 700, 580)
        self.root.configure(bg=COLOR_BG)
        
        # 🌟 修改：允许用户自由拉伸窗口，但设置最小尺寸防破相
        self.root.resizable(True, True)
        self.root.minsize(700, 580)

        self.default_file = get_abs_path("ict_questions.csv")
        self.all_questions, self.grouped, self.paper = [], {}, []
        self.current_index, self.score = 0, 0

        # 绑定窗口大小变化事件
        self.root.bind("<Configure>", self._on_window_resize)

        self.setup_start_ui()
        self.load_data_auto()

    def _on_window_resize(self, event):
        if event.widget == self.root:
            if hasattr(self, 'lbl_question') and self.lbl_question.winfo_exists():
                # 🌟 修改：加上最大宽度限制
                new_wrap = min(int(event.width * 0.75), 1000) 
                self.lbl_question.config(wraplength=new_wrap)
                self.lbl_options.config(wraplength=new_wrap)

    def clear_window(self):
        for widget in self.root.winfo_children(): widget.destroy()

    def setup_start_ui(self):
        self.clear_window()
        create_title_label(self.root, "📚 华为ICT校赛刷题助手").pack(pady=20)
        
        self.lbl_info = tk.Label(self.root, text="正在加载题库...", font=("微软雅黑", 12), bg=COLOR_BG, fg="#666")
        self.lbl_info.pack(pady=5)

        frame_mode = tk.Frame(self.root, bg="#fff", padx=20, pady=20, relief="groove", bd=2)
        frame_mode.pack(pady=10)
        frame_mode.config(width=580)

        tk.Label(frame_mode, text="【专项练习】", font=("微软雅黑", 14, "bold"), bg="#fff").grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
        tk.Label(frame_mode, text="选择题型:", font=("微软雅黑", 12), bg="#fff").grid(row=1, column=0, pady=10, sticky="w")
        self.combo_cat = ttk.Combobox(frame_mode, state="readonly", font=("微软雅黑", 12), width=15)
        self.combo_cat.grid(row=1, column=1, padx=10)
        tk.Label(frame_mode, text="题目数量:", font=("微软雅黑", 12), bg="#fff").grid(row=1, column=2, pady=10, sticky="e")
        self.entry_cat_num = tk.Entry(frame_mode, font=("微软雅黑", 12), width=8)
        self.entry_cat_num.insert(0, "10")
        self.entry_cat_num.grid(row=1, column=3, padx=10)
        create_button(frame_mode, "开始练习", self.start_category_quiz, "success").grid(row=1, column=4, padx=10)

        ttk.Separator(frame_mode, orient="horizontal").grid(row=2, column=0, columnspan=5, sticky="ew", pady=15)

        tk.Label(frame_mode, text="【模拟考试】", font=("微软雅黑", 14, "bold"), bg="#fff").grid(row=3, column=0, columnspan=3, pady=5, sticky="w")
        tk.Label(frame_mode, text="总题数 (按比例分配):", font=("微软雅黑", 12), bg="#fff").grid(row=4, column=0, columnspan=2, pady=10, sticky="w")
        self.entry_total_num = tk.Entry(frame_mode, font=("微软雅黑", 12), width=8)
        self.entry_total_num.insert(0, "20")
        self.entry_total_num.grid(row=4, column=2, padx=10, sticky="w")
        create_button(frame_mode, "模拟考试", self.start_ratio_quiz, "primary").grid(row=4, column=4, padx=10)

        bottom_frame = tk.Frame(self.root, bg=COLOR_BG)
        bottom_frame.pack(pady=15)
        create_button(bottom_frame, "📂 手动导入题库", self.import_csv, "warning").pack(side="left", padx=10)
        create_button(bottom_frame, "🛠️ 打开题库工具箱", self.open_toolbox, "primary").pack(side="left", padx=10)

        if self.grouped: self.update_ui_info()

    def load_data_auto(self):
        self.all_questions = read_standard_csv(self.default_file)
        if self.all_questions:
            self.grouped = self.group_by_category(self.all_questions)
            self.update_ui_info()
        else:
            if hasattr(self, 'lbl_info') and self.lbl_info.winfo_exists():
                self.lbl_info.config(text="⚠️ 未找到 ict_questions.csv，请手动导入。", fg="#d32f2f")

    def group_by_category(self, questions):
        grouped = {}
        for q in questions: grouped.setdefault(q.get("分类", "未分类"), []).append(q)
        return grouped

    def update_ui_info(self):
        info_text = f"题库加载成功！共 {len(self.all_questions)} 题。 "
        for k, v in self.grouped.items(): info_text += f"[{k}:{len(v)}道] "
        if hasattr(self, 'lbl_info'): self.lbl_info.config(text=info_text, fg="#388e3c")
        if hasattr(self, 'combo_cat'):
            self.combo_cat["values"] = list(self.grouped.keys())
            if self.combo_cat["values"]: self.combo_cat.current(0)

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV文件", "*.csv")])
        if file_path:
            self.all_questions = read_standard_csv(file_path)
            if self.all_questions:
                self.grouped = self.group_by_category(self.all_questions)
                self.update_ui_info()
                messagebox.showinfo("成功", "题库导入成功！")

    def open_toolbox(self):
        win = tk.Toplevel(self.root)
        win.title("题库辅助工具集")
        center_window(win, 350, 450)
        win.configure(bg=COLOR_BG)
        create_title_label(win, "🧰 插件工具箱").pack(pady=15)

        current_dir = get_base_dir()
        current_exe_name = os.path.basename(sys.argv[0]) if getattr(sys, 'frozen', False) else "ai_答题工具主程序.py"

        exe_files = [f for f in os.listdir(current_dir) if f.lower().endswith(".exe") and f != current_exe_name]
        if not exe_files:
            tk.Label(win, text="⚠️ 当前文件夹下没有发现其他工具", font=("微软雅黑", 11), bg=COLOR_BG, fg="#d32f2f").pack(pady=30)
        else:
            for exe_name in exe_files:
                def run_exe(name=exe_name):
                    try: subprocess.Popen([os.path.join(current_dir, name)], cwd=current_dir)
                    except Exception as e: messagebox.showerror("启动失败", f"无法启动 {name}：\n{e}")
                create_button(win, f"🔧 {exe_name[:-4]}", run_exe).pack(pady=8)
        create_button(win, "关闭", win.destroy, "danger").pack(pady=20)

    def start_category_quiz(self):
        try: num = int(self.entry_cat_num.get())
        except ValueError: return messagebox.showerror("错误", "请输入有效数字")
        cat = self.combo_cat.get()
        self.paper = random.sample(self.grouped.get(cat, []), min(num, len(self.grouped.get(cat, []))))
        if not self.paper: return messagebox.showwarning("提示", "题库不足")
        self.begin_quiz()

    def start_ratio_quiz(self):
        try: num = int(self.entry_total_num.get())
        except ValueError: return messagebox.showerror("错误", "请输入有效数字")
        
        paper = []
        for cat, ratio in {"单选题": 0.4, "多选题": 0.3, "判断题": 0.3}.items():
            count = int(num * ratio)
            if count > 0 and cat in self.grouped:
                paper.extend(random.sample(self.grouped[cat], min(count, len(self.grouped[cat]))))
                
        if len(paper) < num:
            remaining = [q for q in self.all_questions if q not in paper]
            random.shuffle(remaining)
            paper.extend(remaining[:num - len(paper)])
            
        self.paper = paper[:num]
        random.shuffle(self.paper)
        if not self.paper: return messagebox.showwarning("提示", "题库为空")
        self.begin_quiz()

    def begin_quiz(self):
        self.current_index, self.score = 0, 0
        self.setup_quiz_ui()
        self.show_question()

    def setup_quiz_ui(self):
        self.clear_window()
        top_frame = tk.Frame(self.root, bg=COLOR_BG)
        top_frame.pack(fill="x", pady=10, padx=20)
        self.lbl_progress = tk.Label(top_frame, text="", font=("微软雅黑", 14, "bold"), bg=COLOR_BG)
        self.lbl_progress.pack(side="left")
        self.lbl_score = tk.Label(top_frame, text="当前得分: 0", font=("微软雅黑", 14, "bold"), bg=COLOR_BG, fg=COLOR_PRIMARY)
        self.lbl_score.pack(side="right")

        main_frame = tk.Frame(self.root, bg="#fff", padx=30, pady=30, relief="groove", bd=2)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_type = tk.Label(main_frame, text="", font=("微软雅黑", 12, "bold"), bg="#fff", fg="#FF9800")
        self.lbl_type.pack(anchor="w")
        
        self.lbl_question = tk.Label(main_frame, text="", font=("微软雅黑", 16), bg="#fff", justify="left")
        self.lbl_question.pack(anchor="w", pady=(10, 20))
        
        self.lbl_options = tk.Label(main_frame, text="", font=("微软雅黑", 14), bg="#fff", fg="#333", justify="left")
        self.lbl_options.pack(anchor="w", pady=(0, 20))

        input_frame = tk.Frame(main_frame, bg="#fff")
        input_frame.pack(fill="x", pady=10)
        tk.Label(input_frame, text="你的答案:", font=("微软雅黑", 14), bg="#fff").pack(side="left")
        self.entry_answer = tk.Entry(input_frame, font=("微软雅黑", 16), width=20)
        self.entry_answer.pack(side="left", padx=10)
        self.entry_answer.bind("<Return>", lambda e: self.submit_answer())
        self.btn_submit = create_button(input_frame, "提交", self.submit_answer, "success")
        self.btn_submit.pack(side="left", padx=10)

        self.lbl_feedback = tk.Label(main_frame, text="", font=("微软雅黑", 14, "bold"), bg="#fff")
        self.lbl_feedback.pack(anchor="w", pady=20)
        self.btn_next = create_button(main_frame, "下一题 ➔", self.next_question, "primary")
        self.btn_next.config(state="disabled")
        self.btn_next.pack(side="right")

    def show_question(self):
        q = self.paper[self.current_index]
        self.lbl_progress.config(text=f"第 {self.current_index + 1} / {len(self.paper)} 题")
        self.lbl_score.config(text=f"当前得分: {self.score}")
        self.lbl_type.config(text=f"【{q.get('分类', '未知')}】")
        self.lbl_question.config(text=q.get('题目', ''))
        opt = q.get('选项', '无')
        self.lbl_options.config(text=f"选项：{opt}" if opt != '无' and opt.strip() != '' else "")
        self.entry_answer.delete(0, tk.END)
        self.entry_answer.config(state="normal")
        self.entry_answer.focus()
        self.btn_submit.config(state="normal")
        self.btn_next.config(state="disabled")
        self.lbl_feedback.config(text="")

    def submit_answer(self):
        if self.btn_submit["state"] == "disabled": return
        user_ans = format_answer_ultra(self.entry_answer.get())
        correct_ans = format_answer_ultra(self.paper[self.current_index].get('答案', ''))
        self.entry_answer.config(state="disabled")
        self.btn_submit.config(state="disabled")
        self.btn_next.config(state="normal")
        
        if user_ans == correct_ans:
            self.lbl_feedback.config(text="✅ 回答正确！", fg="#388e3c")
            self.score += 1
            self.lbl_score.config(text=f"当前得分: {self.score}")
        else:
            self.lbl_feedback.config(text=f"❌ 回答错误！正确答案是：{self.paper[self.current_index].get('答案', '')}", fg="#d32f2f")
            append_wrong_question(self.paper[self.current_index])
        if self.current_index == len(self.paper) - 1: self.btn_next.config(text="查看成绩 📊")

    def next_question(self):
        self.current_index += 1
        if self.current_index < len(self.paper): self.show_question()
        else: self.show_result()

    def show_result(self):
        self.clear_window()
        acc = (self.score / len(self.paper)) * 100 if self.paper else 0
        create_title_label(self.root, "🏆 答题结束").pack(pady=50)
        tk.Label(self.root, text=f"最终得分：{self.score} / {len(self.paper)}", font=("微软雅黑", 20), bg=COLOR_BG).pack(pady=10)
        color = "#388e3c" if acc >= 80 else ("#FF9800" if acc >= 60 else "#d32f2f")
        tk.Label(self.root, text=f"正确率：{acc:.1f}%", font=("微软雅黑", 24, "bold"), bg=COLOR_BG, fg=color).pack(pady=10)
        create_button(self.root, "返回主菜单", self.setup_start_ui).pack(pady=40)

if __name__ == "__main__":
    root = tk.Tk()
    app = ICTHelperApp(root)
    try:
        root.state("zoomed")
    except tk.TclError:
        root.attributes("-fullscreen", True)
    def _toggle_fullscreen(event=None):
        root.attributes("-fullscreen", not root.attributes("-fullscreen"))
    def _exit_fullscreen(event=None):
        root.attributes("-fullscreen", False)
    root.bind("<F11>", _toggle_fullscreen)
    root.bind("<Escape>", _exit_fullscreen)
    root.mainloop()
