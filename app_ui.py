import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import time
import random

print("\n" + "="*50)
print(">>> RUNNING LIGHT THEME + EXCEL GRID INSPECTOR <<<")
print("="*50 + "\n")

# --- นำเข้าไลบรารีสำหรับทำ Auto-Update แบบสากล ---
import json
import sys
import subprocess
import urllib.request 
# -------------------------------------------------

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import windnd
except ImportError:
    windnd = None

from core_logic import DataReconciler 

# 📌 ธีมสีขาว (Light Mode)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# =========================================================================
# โซนตั้งค่าระบบ AUTO-UPDATE แบบสากล
# =========================================================================
APP_VERSION = "1.0.1" 

VERSION_URL = "https://raw.githubusercontent.com/Buanruk/EXTOR/master/version.json"

def check_for_updates():
    try:
        if not sys.executable.endswith('.exe') or 'python' in sys.executable.lower():
            return
            
        req = urllib.request.Request(VERSION_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            server_config = json.loads(response.read().decode('utf-8'))
            
        latest_version = server_config.get("version", "1.0.0")
        
        if latest_version != APP_VERSION:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw() 
            response = messagebox.askyesno(
                "พบอัปเดตใหม่!", 
                f"โปรแกรม EXTOR มีเวอร์ชันใหม่ (v{latest_version})\nคุณต้องการอัปเดตเดี๋ยวนี้เลยหรือไม่?\n(ระบบจะดาวน์โหลดและติดตั้งอัตโนมัติ)"
            )
            root.destroy()
            
            if response:
                download_url = f"https://github.com/Buanruk/EXTOR/releases/download/v{latest_version}/main_ui.exe"
                current_exe_path = sys.executable 
                temp_exe_path = os.path.join(os.path.dirname(current_exe_path), "update_temp.exe")
                
                urllib.request.urlretrieve(download_url, temp_exe_path)

                updater_bat = os.path.join(os.path.dirname(current_exe_path), "updater.bat")
                with open(updater_bat, "w", encoding="cp874") as bat:
                    bat.write('@echo off\n')
                    bat.write('timeout /t 2 /nobreak > nul\n')
                    bat.write(f'copy /y "{temp_exe_path}" "{current_exe_path}"\n') 
                    bat.write(f'del "{temp_exe_path}"\n') 
                    bat.write(f'start "" "{current_exe_path}"\n') 
                    bat.write('del "%~f0"\n')
                    
                subprocess.Popen([updater_bat], shell=True)
                sys.exit()
                
    except Exception as e:
        pass
# =========================================================================

class MinebeaBackground(ctk.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.lines = []
        self.bind("<Configure>", self.init_lines)
        self.animate()

    def init_lines(self, event=None):
        self.delete("all")
        self.lines = []
        width = self.winfo_width()
        height = self.winfo_height()
        for _ in range(15):
            x = int(random.uniform(0, width))
            length = int(random.uniform(50, 200))
            speed = random.uniform(0.5, 2.0)
            line = self.create_line(x, height, x, height-length, fill="#e0f2fe", width=2)
            self.lines.append({'id': line, 'speed': speed, 'length': length})

    def animate(self):
        height = self.winfo_height()
        for l in self.lines:
            self.move(l['id'], 0, -l['speed'])
            pos = self.coords(l['id'])
            if pos and pos[3] < 0: 
                self.coords(l['id'], pos[0], height + l['length'], pos[2], height)
        self.after(30, self.animate)

class CircularSpinner(ctk.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.angle = 0
        self.is_spinning = False

    def start(self):
        self.is_spinning = True
        self.spin()

    def stop(self):
        self.is_spinning = False
        self.delete("all")

    def spin(self):
        if not self.is_spinning: return
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        cx, cy = width/2, height/2
        r = 30
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=self.angle, extent=120, outline="#38bdf8", width=5, style="arc")
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=self.angle+180, extent=120, outline="#0284c7", width=5, style="arc")
        self.angle = (self.angle - 10) % 360
        self.after(20, self.spin)

class ExcelCompareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EXTOR - Data Reconciler")
        
        self.geometry("1400x850")
        self.minsize(1024, 720) 
        try:
            self.state('zoomed') 
        except:
            pass
        
        self.bg_canvas = MinebeaBackground(self, bg="#f8fafc")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.file1_path = ""
        self.file2_path = ""
        self.selected_columns = []
        self.result_df = None
        self.processor = DataReconciler()

        self.create_widgets()
        if windnd:
            self.setup_drag_and_drop()

    def setup_treeview_style(self):
        style = ttk.Style(self)
        style.theme_use("default")
        
        style.configure("Cyber.Treeview", 
                        background="#ffffff", 
                        fieldbackground="#ffffff", 
                        foreground="#1e293b", 
                        rowheight=36, 
                        borderwidth=0, 
                        font=('Segoe UI', 10))
                        
        style.map('Cyber.Treeview', 
                  background=[('selected', '#e0f2fe')], 
                  foreground=[('selected', '#0369a1')]) 
                  
        style.configure("Cyber.Treeview.Heading", 
                        background="#f1f5f9", 
                        foreground="#0f172a", 
                        relief="flat", 
                        font=('Segoe UI', 10, 'bold'))
        
        def fixed_map(option):
            return [elm for elm in style.map("Cyber.Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]
        style.map("Cyber.Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))

    def create_widgets(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        sidebar = ctk.CTkScrollableFrame(self.main_container, width=340, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e2e8f0")
        sidebar.pack(side="left", fill="y", padx=(0, 15))

        logo_frame = ctk.CTkFrame(sidebar, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0", corner_radius=12)
        logo_frame.pack(pady=20, padx=15, fill="x")
        
        logo_loaded = False
        if HAS_PIL and os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png")
                img.thumbnail((280, 70)) 
                self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                lbl_logo = ctk.CTkLabel(logo_frame, image=self.logo_image, text="")
                lbl_logo.pack(pady=10, padx=10)
                logo_loaded = True
            except Exception as e:
                pass
            
        if not logo_loaded:
            ctk.CTkLabel(logo_frame, text="EXTOR", font=ctk.CTkFont(size=28, weight="bold"), text_color="#0284c7").pack(pady=12)
            
        ctk.CTkLabel(sidebar, text="Data Reconciler System", font=ctk.CTkFont(size=13, weight="normal"), text_color="#64748b").pack(pady=(0, 15))

        box1 = ctk.CTkFrame(sidebar, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#cbd5e1")
        box1.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(box1, text="1. Base File (ไฟล์หลัก)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#0f172a").pack(pady=(12,2))
        self.lbl_file1 = ctk.CTkLabel(box1, text="ยังไม่ได้เลือกไฟล์", text_color="#64748b", font=ctk.CTkFont(size=12))
        self.lbl_file1.pack(pady=2)
        btn_f1 = ctk.CTkFrame(box1, fg_color="transparent")
        btn_f1.pack(pady=(2,12))
        ctk.CTkButton(btn_f1, text="Browse", width=80, height=30, font=ctk.CTkFont(weight="bold"), command=lambda: self.select_file(1), fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b", border_width=1, border_color="#cbd5e1").pack(side="left", padx=5)
        self.sheet_var1 = ctk.StringVar(value="Sheet")
        self.dropdown1 = ctk.CTkOptionMenu(btn_f1, variable=self.sheet_var1, values=["Sheet"], state="disabled", width=120, height=30, fg_color="#f8fafc", button_color="#e2e8f0", text_color="#1e293b")
        self.dropdown1.pack(side="left", padx=5)

        ctk.CTkButton(sidebar, text="⇅ สลับไฟล์คู่เทียบ (Swap)", width=150, height=28, font=ctk.CTkFont(size=12, weight="bold"), fg_color="#f8fafc", hover_color="#e2e8f0", text_color="#0284c7", border_width=1, border_color="#e2e8f0", command=self.swap_files).pack(pady=8)

        box2 = ctk.CTkFrame(sidebar, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#cbd5e1")
        box2.pack(fill="x", padx=15, pady=6)
        ctk.CTkLabel(box2, text="2. Compare File (ไฟล์เทียบ)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#0f172a").pack(pady=(12,2))
        self.lbl_file2 = ctk.CTkLabel(box2, text="ยังไม่ได้เลือกไฟล์", text_color="#64748b", font=ctk.CTkFont(size=12))
        self.lbl_file2.pack(pady=2)
        btn_f2 = ctk.CTkFrame(box2, fg_color="transparent")
        btn_f2.pack(pady=(2,12))
        ctk.CTkButton(btn_f2, text="Browse", width=80, height=30, font=ctk.CTkFont(weight="bold"), command=lambda: self.select_file(2), fg_color="#f1f5f9", hover_color="#e2e8f0", text_color="#1e293b", border_width=1, border_color="#cbd5e1").pack(side="left", padx=5)
        self.sheet_var2 = ctk.StringVar(value="Sheet")
        self.dropdown2 = ctk.CTkOptionMenu(btn_f2, variable=self.sheet_var2, values=["Sheet"], state="disabled", width=120, height=30, fg_color="#f8fafc", button_color="#e2e8f0", text_color="#1e293b")
        self.dropdown2.pack(side="left", padx=5)

        filter_box = ctk.CTkFrame(sidebar, fg_color="#f8fafc", corner_radius=12, border_width=1, border_color="#e2e8f0")
        filter_box.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(filter_box, text="🛠 ตัวกรองข้อมูล (Filters)", font=ctk.CTkFont(size=13, weight="bold"), text_color="#0284c7").pack(pady=(12,8))
        
        ctk.CTkLabel(filter_box, text="ระบุช่วงบรรทัด (เช่น 1-100)", text_color="#64748b", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=15)
        self.entry_row = ctk.CTkEntry(filter_box, placeholder_text="เว้นว่างไว้หากต้องการดูทั้งหมด", height=32, fg_color="#ffffff", border_color="#cbd5e1", text_color="#0f172a")
        self.entry_row.pack(fill="x", padx=15, pady=(4,12))

        self.btn_col_filter = ctk.CTkButton(filter_box, text="⚙️ เลือกคอลัมน์ที่จะตรวจ...", fg_color="#0f172a", hover_color="#334155", text_color="#ffffff", height=32, font=ctk.CTkFont(size=12, weight="bold"), command=self.open_column_selector)
        self.btn_col_filter.pack(fill="x", padx=15, pady=(0,12))
        
        self.lbl_selected_cols = ctk.CTkLabel(filter_box, text="* เช็คทุกคอลัมน์ (ค่าเริ่มต้น)", text_color="#059669", font=ctk.CTkFont(size=11, weight="normal"))
        self.lbl_selected_cols.pack(pady=(0, 12))

        self.btn_compare = ctk.CTkButton(sidebar, text="COMPARE DATA", fg_color="#0ea5e9", hover_color="#0284c7", text_color="#ffffff", font=ctk.CTkFont(size=14, weight="bold"), height=48, corner_radius=12, command=self.run_comparison_thread)
        self.btn_compare.pack(fill="x", padx=15, pady=12)

        main_content = ctk.CTkFrame(self.main_container, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e2e8f0")
        main_content.pack(side="right", fill="both", expand=True)

        self.lbl_compare_info = ctk.CTkLabel(main_content, text="กรุณาเลือกไฟล์เพื่อเปรียบเทียบข้อมูล", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64748b")
        self.lbl_compare_info.pack(pady=(16, 5))

        head_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        head_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_summary = ctk.CTkLabel(head_frame, text="Dashboard Ready", font=ctk.CTkFont(size=18, weight="bold"), text_color="#0f172a")
        self.lbl_summary.pack(side="left")
        
        self.btn_export = ctk.CTkButton(head_frame, text="⬇ Export Excel", fg_color="#10b981", hover_color="#059669", text_color="white", font=ctk.CTkFont(weight="bold"), width=130, height=32, corner_radius=8, command=self.export_result, state="disabled")
        self.btn_export.pack(side="right")

        self.setup_treeview_style()

        self.tabview = ctk.CTkTabview(main_content, corner_radius=12, fg_color="#ffffff", segmented_button_fg_color="#f1f5f9", segmented_button_selected_color="#0ea5e9", segmented_button_unselected_color="#f1f5f9", segmented_button_unselected_hover_color="#e2e8f0", text_color="#1e293b")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_all = self.tabview.add("แสดงผลทั้งหมด")
        self.tab_changed = self.tabview.add("📌 เฉพาะที่แก้ (Changed)")
        self.tab_new = self.tabview.add("✨ รายการใหม่ (New)")
        self.tab_del = self.tabview.add("❌ ถูกลบ (Deleted)")

        self.tree_all = self.create_treeview(self.tab_all)
        self.tree_changed = self.create_treeview(self.tab_changed)
        self.tree_new = self.create_treeview(self.tab_new)
        self.tree_del = self.create_treeview(self.tab_del)

        self.loading_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=16, border_width=2, border_color="#0ea5e9")
        self.spinner = CircularSpinner(self.loading_frame, bg="#ffffff", width=100, height=100)
        self.spinner.pack(pady=(25, 10))
        self.loading_lbl = ctk.CTkLabel(self.loading_frame, text="กำลังประมวลผลข้อมูลคู่วิเคราะห์...\nกรุณารอสักครู่", font=ctk.CTkFont(size=13, weight="bold"), text_color="#0f172a")
        self.loading_lbl.pack(pady=(0, 25), padx=35)

    def show_loading(self):
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.spinner.start()
        self.btn_compare.configure(state="disabled")

    def hide_loading(self):
        self.spinner.stop()
        self.loading_frame.place_forget()
        self.btn_compare.configure(state="normal")

    def swap_files(self):
        self.file1_path, self.file2_path = self.file2_path, self.file1_path
        txt1 = self.lbl_file1.cget("text")
        txt2 = self.lbl_file2.cget("text")
        self.lbl_file1.configure(text=txt2)
        self.lbl_file2.configure(text=txt1)

        vals1 = self.dropdown1.cget("values")
        vals2 = self.dropdown2.cget("values")
        state1 = self.dropdown1.cget("state")
        state2 = self.dropdown2.cget("state")
        
        self.dropdown1.configure(values=vals2, state=state2)
        self.dropdown2.configure(values=vals1, state=state1)
        
        curr_sheet1 = self.sheet_var1.get()
        curr_sheet2 = self.sheet_var2.get()
        self.sheet_var1.set(curr_sheet2)
        self.sheet_var2.set(curr_sheet1)

    def open_column_selector(self):
        if not self.file1_path:
            messagebox.showwarning("แจ้งเตือน", "กรุณาใส่ไฟล์ในช่องที่ 1 เพื่อดึงหัวข้อคอลัมน์ก่อนครับ")
            return
        try:
            columns = self.processor.get_columns(self.file1_path, self.sheet_var1.get())
        except Exception as e:
            messagebox.showerror("อ่านคอลัมน์ไม่สำเร็จ", str(e))
            return

        top = ctk.CTkToplevel(self)
        top.title("เลือกคอลัมน์ที่ต้องการเปรียบเทียบ")
        top.geometry("400x500")
        top.grab_set()

        ctk.CTkLabel(top, text="ติ๊กเลือกเฉพาะคอลัมน์ที่ต้องการตรวจ", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        scroll = ctk.CTkScrollableFrame(top, width=350, height=350)
        scroll.pack(padx=20, pady=10, fill="both", expand=True)

        checkboxes = {}
        for col in columns:
            if col in self.processor.key_cols: continue
            var = ctk.BooleanVar(value=(col in self.selected_columns) if self.selected_columns else True)
            cb = ctk.CTkCheckBox(scroll, text=col, variable=var)
            cb.pack(anchor="w", pady=5, padx=10)
            checkboxes[col] = var

        def save_selection():
            self.selected_columns = [col for col, var in checkboxes.items() if var.get()]
            self.lbl_selected_cols.configure(text=f"* เลือกแล้ว {len(self.selected_columns)} คอลัมน์", text_color="#f39c12")
            top.destroy()

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="เลือกทั้งหมด", width=100, command=lambda: [v.set(True) for v in checkboxes.values()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="ล้างทั้งหมด", width=100, command=lambda: [v.set(False) for v in checkboxes.values()]).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="บันทึก", width=100, fg_color="#059669", hover_color="#047857", command=save_selection).pack(side="left", padx=5)

    # 📌 ฟังก์ชันป๊อปอัปตารางตรวจคอลัมน์ (ออกแบบเลียนแบบตาราง Excel)
    def show_row_details(self, event, tree):
        selected = tree.selection()
        if not selected: return
        
        item = tree.item(selected[0])
        values = item['values']
        columns = tree['columns']
        tags = item.get('tags', [])
        status = tags[0] if tags else "Normal"
        
        detail_win = ctk.CTkToplevel(self)
        detail_win.title("🔍 Grid Inspector - รายละเอียดการเปลี่ยนแปลง")
        detail_win.geometry("600x700")
        detail_win.grab_set() 
        
        ctk.CTkLabel(detail_win, text=f"รายการสถานะ: {status}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#0f172a").pack(pady=(20, 10))
        
        scroll = ctk.CTkScrollableFrame(detail_win, width=550, height=600, fg_color="#f8fafc", corner_radius=12)
        scroll.pack(padx=20, pady=10, fill="both", expand=True)
        
        changed_data = []
        normal_data = []
        
        for col, val in zip(columns, values):
            val_str = str(val)
            if "->" in val_str or (status == "Changed" and "[" in val_str and "]" in val_str):
                changed_data.append((col, val_str))
            else:
                normal_data.append((col, val_str))

        # -----------------------------------------------------------
        # ส่วนที่ 1: ตารางไฮไลท์จุดเปลี่ยน (กรอบเส้นสีเหลืองทองเหมือน Excel)
        # -----------------------------------------------------------
        if changed_data:
            ctk.CTkLabel(scroll, text="⚠️ คอลัมน์ที่มีการเปลี่ยนแปลง (Changed)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#d97706").pack(anchor="w", pady=(10, 5), padx=5)
            
            # ใช้พื้นหลังของ Frame เป็นสีของเส้นตาราง (Border Color)
            table_changed = ctk.CTkFrame(scroll, fg_color="#fbbf24", corner_radius=0) 
            table_changed.pack(fill="x", padx=5, pady=(0, 15))
            table_changed.columnconfigure(0, weight=1)
            table_changed.columnconfigure(1, weight=3)
            
            # หัวตาราง (เว้นขอบ 1px ให้เห็นพื้นหลังสีเหลืองกลายเป็นเส้นคั่น)
            h1 = ctk.CTkLabel(table_changed, text=" ชื่อคอลัมน์ (Column)", fg_color="#fef3c7", text_color="#92400e", font=ctk.CTkFont(weight="bold"), anchor="w")
            h1.grid(row=0, column=0, sticky="nsew", padx=(1, 1), pady=(1, 1), ipady=6)
            
            h2 = ctk.CTkLabel(table_changed, text=" ข้อมูลที่มีการแก้ไข (Data)", fg_color="#fef3c7", text_color="#92400e", font=ctk.CTkFont(weight="bold"), anchor="w")
            h2.grid(row=0, column=1, sticky="nsew", padx=(0, 1), pady=(1, 1), ipady=6)
            
            # ข้อมูลแต่ละแถว
            for i, (col, val) in enumerate(changed_data):
                row_idx = i + 1
                c1 = ctk.CTkLabel(table_changed, text=f" {col}", fg_color="#fffbeb", text_color="#b45309", anchor="w", justify="left")
                c1.grid(row=row_idx, column=0, sticky="nsew", padx=(1, 1), pady=(0, 1), ipady=6)
                
                c2 = ctk.CTkLabel(table_changed, text=f" {val}", fg_color="#ffffff", text_color="#d97706", anchor="w", justify="left", font=ctk.CTkFont(weight="bold"))
                c2.grid(row=row_idx, column=1, sticky="nsew", padx=(0, 1), pady=(0, 1), ipady=6)

        # -----------------------------------------------------------
        # ส่วนที่ 2: ตารางข้อมูลที่ไม่เปลี่ยน (กรอบเส้นสีเทา)
        # -----------------------------------------------------------
        if normal_data:
            ctk.CTkLabel(scroll, text="✅ คอลัมน์ที่ข้อมูลปกติ (Unchanged)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#64748b").pack(anchor="w", pady=(10, 5), padx=5)
            
            # ใช้พื้นหลังสีเทาเข้มเพื่อเป็นเส้นคั่น
            table_normal = ctk.CTkFrame(scroll, fg_color="#cbd5e1", corner_radius=0) 
            table_normal.pack(fill="x", padx=5, pady=(0, 15))
            table_normal.columnconfigure(0, weight=1)
            table_normal.columnconfigure(1, weight=3)
            
            for i, (col, val) in enumerate(normal_data):
                # ช่องซ้าย (สีเทาอ่อนมาก)
                c1 = ctk.CTkLabel(table_normal, text=f" {col}", fg_color="#f8fafc", text_color="#64748b", anchor="w", justify="left")
                c1.grid(row=i, column=0, sticky="nsew", padx=(1, 1), pady=(1 if i==0 else 0, 1), ipady=6)
                
                # ช่องขวา (สีขาว)
                c2 = ctk.CTkLabel(table_normal, text=f" {val}", fg_color="#ffffff", text_color="#1e293b", anchor="w", justify="left")
                c2.grid(row=i, column=1, sticky="nsew", padx=(0, 1), pady=(1 if i==0 else 0, 1), ipady=6)

        # ถ้าเป็นรายการที่พึ่งเพิ่มเข้ามาใหม่หรือถูกลบทิ้งไปทั้งแถว (ไม่มีค่า -> ให้เปรียบเทียบ)
        if not changed_data and status in ["New", "Deleted"]:
            ctk.CTkLabel(scroll, text="รายการนี้ถูกเพิ่มใหม่หรือลบออกทั้งบรรทัด\n(ไม่มีการเปลี่ยนค่ารายเซลล์ให้เปรียบเทียบ)", text_color="#64748b", font=ctk.CTkFont(size=13)).pack(pady=40)

    def create_treeview(self, parent):
        tree_scroll_y = ttk.Scrollbar(parent)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(parent, orient='horizontal')
        tree_scroll_x.pack(side="bottom", fill="x")

        tree = ttk.Treeview(parent, style="Cyber.Treeview", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        # 📌 ผูกฟังก์ชันดับเบิลคลิกเพื่อเปิด Inspector แบบ Grid
        tree.bind("<Double-1>", lambda e, t=tree: self.show_row_details(e, t))

        tree.tag_configure('Changed', background='#fef3c7', foreground='#b45309') 
        tree.tag_configure('New', background='#d1fae5', foreground='#047857')     
        tree.tag_configure('Deleted', background='#fee2e2', foreground='#b91c1c') 

        return tree

    def setup_drag_and_drop(self):
        windnd.hook_dropfiles(self, func=self.on_file_drop)

    def decode_path(self, file_bytes):
        for enc in ['utf-8', 'cp874', 'tis-620', 'ansi']:
            try: return file_bytes.decode(enc)
            except: continue
        return str(file_bytes)

    def load_file_to_box(self, filepath, box_num):
        filename = os.path.basename(filepath)
        try:
            sheets = self.processor.get_sheet_names(filepath)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if box_num == 1:
            self.file1_path = filepath
            self.lbl_file1.configure(text=filename[:30]+"...", text_color="#0f172a")
            self.dropdown1.configure(values=sheets, state="normal")
            self.sheet_var1.set(sheets[0])
        else:
            self.file2_path = filepath
            self.lbl_file2.configure(text=filename[:30]+"...", text_color="#0f172a")
            self.dropdown2.configure(values=sheets, state="normal")
            self.sheet_var2.set(sheets[0])

    def on_file_drop(self, files):
        for file_bytes in files:
            filepath = self.decode_path(file_bytes)
            if not (filepath.lower().endswith('.xlsx') or filepath.lower().endswith('.csv')):
                messagebox.showwarning("Type Error", "รองรับเฉพาะ .xlsx และ .csv")
                return
            mouse_x = self.winfo_pointerx() - self.winfo_rootx()
            box_num = 1 if mouse_x < 350 else 2
            self.load_file_to_box(filepath, box_num)

    def select_file(self, file_num):
        filepath = filedialog.askopenfilename(filetypes=[("Excel & CSV", "*.xlsx *.csv")])
        if filepath:
            self.load_file_to_box(filepath, file_num)

    def run_comparison_thread(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Warning", "กรุณาเลือกไฟล์ให้ครบทั้ง 2 ฝั่งครับ")
            return
        sheet1, sheet2 = self.sheet_var1.get(), self.sheet_var2.get()
        if sheet1.startswith("Sheet") or sheet2.startswith("Sheet"):
            messagebox.showwarning("Warning", "กรุณาเลือก Sheet ด้วยครับ")
            return

        fname1 = os.path.basename(self.file1_path)
        fname2 = os.path.basename(self.file2_path)
        self.lbl_compare_info.configure(text=f"📁 {fname1}   AND   📁 {fname2}", text_color="#0284c7")

        self.show_loading()
        threading.Thread(target=self._process_data_backend, args=(sheet1, sheet2), daemon=True).start()

    def _process_data_backend(self, sheet1, sheet2):
        row_limit = self.entry_row.get()
        cols = self.selected_columns if self.selected_columns else None
        try:
            time.sleep(0.5) 
            self.result_df = self.processor.compare_data(
                self.file1_path, sheet1, 
                self.file2_path, sheet2, 
                target_cols=cols, 
                row_range=row_limit
            )
            self.after(0, self._update_ui_with_results)
        except Exception as e:
            self.after(0, self.hide_loading)
            self.after(0, lambda: messagebox.showerror("เกิดข้อผิดพลาด", str(e)))

    def _update_ui_with_results(self):
        self.hide_loading()
        total_diff = len(self.result_df)
        if total_diff == 0:
            self.lbl_summary.configure(text="✅ ข้อมูลตรงกัน 100%", text_color="#10b981")
            self.btn_export.configure(state="disabled")
            self.clear_all_trees()
        else:
            counts = self.result_df['Status'].value_counts()
            chg = counts.get('Changed', 0)
            new = counts.get('New', 0)
            dlt = counts.get('Deleted', 0)
            
            msg = f"จุดที่เปลี่ยนแปลง {total_diff} รายการ (เปลี่ยน: {chg} | ใหม่: {new} | ลบ: {dlt})"
            self.lbl_summary.configure(text=msg, text_color="#b45309")
            self.btn_export.configure(state="normal")
            
            self.populate_tree(self.tree_all, self.result_df)
            self.populate_tree(self.tree_changed, self.result_df[self.result_df['Status'] == 'Changed'])
            self.populate_tree(self.tree_new, self.result_df[self.result_df['Status'] == 'New'])
            self.populate_tree(self.tree_del, self.result_df[self.result_df['Status'] == 'Deleted'])

    def clear_all_trees(self):
        for tree in [self.tree_all, self.tree_changed, self.tree_new, self.tree_del]:
            tree.delete(*tree.get_children())

    def populate_tree(self, tree, df):
        tree.delete(*tree.get_children())
        if df.empty: return

        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            width = 130 if col not in self.processor.key_cols else 100
            tree.column(col, width=width, minwidth=80)

        for _, row in df.iterrows():
            row_data = ["" if pd.isna(x) else str(x) for x in row]
            status = row.get('Status', '')
            tree.insert("", "end", values=row_data, tags=(status,))

    def export_result(self):
        if self.result_df is None or self.result_df.empty: return
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], initialfile="Reconcile_Result_Minebea.xlsx")
        if save_path:
            try:
                self.result_df.to_excel(save_path, index=False)
                messagebox.showinfo("Success", "ส่งออกไฟล์ Excel สำเร็จ!")
            except Exception as e:
                messagebox.showerror("Error", f"ไม่สามารถบันทึกไฟล์ได้:\n{str(e)}")

if __name__ == "__main__":
    check_for_updates() 
    app = ExcelCompareApp()
    app.mainloop()