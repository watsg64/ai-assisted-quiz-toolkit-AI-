import os
import sys
import csv
import re
import unicodedata
import tkinter as tk
from tkinter import ttk

# ================= 路径处理 =================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_abs_path(relative_path):
    return os.path.join(get_base_dir(), relative_path)

# ================= 数据清洗 =================
def clean_text_ultra(text):
    if not text: return ""
    text = unicodedata.normalize('NFKC', str(text)).lower()
    return re.sub(r'[^\w\u4e00-\u9fa5]', '', text)

def format_answer_ultra(answer):
    if not answer: return ""
    ans = unicodedata.normalize('NFKC', str(answer)).replace(" ", "").strip().upper()
    if ans in ["T", "TRUE", "对", "√", "Y", "YES"]: return "正确"
    if ans in ["F", "FALSE", "错", "×", "N", "NO"]: return "错误"
    if re.match(r'^[A-Z]+$', ans): return "".join(sorted(set(ans)))
    return ans

# ================= 文件读写 =================
def read_standard_csv(file_path):
    if not os.path.exists(file_path): return []
    data = []
    for encoding in ["utf-8-sig", "gbk"]:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("题目", "").strip(): data.append(row)
            return data
        except UnicodeDecodeError: continue
        except Exception: return []
    return []

def save_standard_csv(data_list, save_path):
    headers = ["分类", "题目", "选项", "答案"]
    try:
        with open(save_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data_list)
        return True, "保存成功"
    except Exception as e:
        return False, f"保存失败：{e}"

def append_wrong_question(question_dict):
    file_path = get_abs_path("错题本.csv")
    file_exists = os.path.exists(file_path)
    headers = ["分类", "题目", "选项", "答案"]
    with open(file_path, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists: writer.writeheader()
        writer.writerow({k: question_dict.get(k, "") for k in headers})

# ================= UI 组件 =================
COLOR_BG = "#f4f4f9"
COLOR_PRIMARY = "#2196F3"
COLOR_SUCCESS = "#4CAF50"
COLOR_DANGER = "#dc3545"
FONT_NORMAL = ("微软雅黑", 11)
FONT_TITLE = ("微软雅黑", 16, "bold")

def center_window(window, width, height):
    x = int((window.winfo_screenwidth() / 2) - (width / 2))
    y = int((window.winfo_screenheight() / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

def create_title_label(parent, text):
    return tk.Label(parent, text=text, font=FONT_TITLE, bg=COLOR_BG, fg="#333")

def create_normal_label(parent, text):
    return tk.Label(parent, text=text, font=FONT_NORMAL, bg=COLOR_BG, fg="#555")

def create_button(parent, text, command, style="primary"):
    colors = {"primary": (COLOR_PRIMARY, "white"), "success": (COLOR_SUCCESS, "white"), "danger": (COLOR_DANGER, "white"), "warning": ("#FFC107", "black")}
    bg, fg = colors.get(style, (COLOR_PRIMARY, "white"))
    return tk.Button(parent, text=text, command=command, font=("微软雅黑", 11, "bold"), bg=bg, fg=fg, relief="flat", cursor="hand2")

def create_treeview(parent, columns_config):
    frame = tk.Frame(parent)
    tree = ttk.Treeview(frame, columns=tuple(columns_config.keys()), show="headings")
    for col_id, (col_name, col_width) in columns_config.items():
        tree.heading(col_id, text=col_name)
        tree.column(col_id, width=col_width, anchor="w")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return frame, tree