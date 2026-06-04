import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import time
import random

# --- [เพิ่มใหม่] นำเข้าไลบรารีสำหรับทำ Auto-Update ---
import json
import sys
import subprocess
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

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =========================================================================
# [เพิ่มใหม่] โซนตั้งค่าระบบ AUTO-UPDATE
# =========================================================================
APP_VERSION = "1.0.0"  # หากหนุ่มแก้โค้ดใหม่ ให้มาเปลี่ยนเลขตรงนี้เป็น 1.0.1, 1.0.2 ไปเรื่อยๆ
UPDATE_SERVER_PATH = r"Z:\Minebea_IT\DataReconciler_Update" # เปลี่ยนตรงนี้เป็นพาท Shared Drive ของแผนกที่จะเอาไฟล์ไปวาง

def check_for_updates():
    """ ระบบตรวจสอบเวอร์ชันและดาวน์โหลดตัวติดตั้งใหม่ทับตัวเองอัตโนมัติ """
    try:
        # ข้ามการเช็คอัปเดตถ้าหนุ่มกำลังรันเทสผ่าน VSCode (ทำงานเฉพาะตอนเป็น .exe แล้ว)
        if not sys.executable.endswith('.exe') or 'python' in sys.executable.lower():
            return
            
        version_file_server = os.path.join(UPDATE_SERVER_PATH, "version.json")
        if not os.path.exists(version_file_server):
            return # ถ้าไม่มีไฟล์บน Server ให้ข้ามไปเปิดแอปปกติ
            
        with open(version_file_server, "r") as f:
            server_config = json.load(f)
            
        latest_version = server_config.get("version", "1.0.0")
        
        # ถ้าเวอร์ชันบน Server ใหม่กว่าของที่เปิดอยู่
        if latest_version != APP_VERSION:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw() # ซ่อนหน้าต่างหลัก
            response = messagebox.askyesno(
                "มีอัปเดตใหม่!", 
                f"พบโปรแกรมเวอร์ชันใหม่ (v{latest_version})\nคุณต้องการอัปเดตเดี๋ยวนี้เลยหรือไม่?\n(โปรแกรมจะปิดและเปิดใหม่เองใช้เวลา 2-3 วินาที)"
            )
            root.destroy()
            
            if response:
                # ให้ตั้งชื่อไฟล์ exe ใหม่บน Server เป็นชื่อนี้
                new_exe_server = os.path.join(UPDATE_SERVER_PATH, "main_ui.exe") 
                current_exe_path = sys.executable 
                
                if not os.path.exists(new_exe_server):
                    messagebox.showerror("Error", "หาไฟล์อัปเดตบนเซิร์ฟเวอร์ไม่พบ กรุณาติดต่อผู้พัฒนา")
                    return

                # สร้าง Batch Script สั้นๆ เพื่อปิดแอปเก่า, เอาตัวใหม่มาวางทับ, และรันแอปใหม่
                updater_bat = os.path.join(os.path.dirname(current_exe_path), "updater.bat")
                with open(updater_bat, "w", encoding="cp874") as bat:
                    bat.write('@echo off\n')
                    bat.write('timeout /t 2 /nobreak > nul\n')
                    bat.write(f'copy /y "{new_exe_server}" "{current_exe_path}"\n')
                    bat.write(f'start "" "{current_exe_path}"\n')
                    bat.write('del "%~f0"\n')
                    
                # สั่งรันสคริปต์อัปเดต แล้วสั่งปิดโปรแกรมตัวเอง
                subprocess.Popen([updater_bat], shell=True)
                sys.exit()
                
    except Exception as e:
        pass # ถ้ามีปัญหา (เช่น ไม่ได้ต่อเน็ตโรงงาน) ก็ให้เงียบไว้ แล้วเปิดแอปตามปกติ
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
            line = self.create_line(x, height, x, height-length, fill="#0033a0", width=2)
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
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=self.angle, extent=120, outline="#00a0ff", width=5, style="arc")
        self.create_arc(cx-r, cy-r, cx+r, cy+r, start=self.angle+180, extent=120, outline="#0033a0", width=5, style="arc")
        self.angle = (self.angle - 10) % 360
        self.after(20, self.spin)

class ExcelCompareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EXTOR - Data Reconciler")
        self.geometry("1400x850")
        
        self.bg_canvas = MinebeaBackground(self, bg="#0d1117")
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.file1_path = ""
        self.file2_path = ""
        self.selected_columns = []
        self.result_df = None
        self.processor = DataReconciler()

        self.create_widgets()
        if windnd:
            self.setup_drag_and_drop()

    def create_widgets(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # --- SIDEBAR ---
        sidebar = ctk.CTkFrame(self.main_container, width=340, fg_color="#1c2128", corner_radius=15, border_width=1, border_color="#30363d")
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        # ส่วนจัดการ Logo กรอบสวยงาม
        logo_frame = ctk.CTkFrame(sidebar, fg_color="#22272e", border_width=1, border_color="#30363d", corner_radius=10)
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
                print(f"Logo fail: {e}")
            
        if not logo_loaded:
            ctk.CTkLabel(logo_frame, text="EXTOR", font=ctk.CTkFont(size=26, weight="bold"), text_color="#00a0ff").pack(pady=10)
            
        ctk.CTkLabel(sidebar, text="Data Reconciler", font=ctk.CTkFont(size=14), text_color="#8b949e").pack(pady=(0, 15))

        # กล่อง 1
        box1 = ctk.CTkFrame(sidebar, fg_color="#22272e", corner_radius=10, border_width=1, border_color="#0033a0")
        box1.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(box1, text="1. Base File (ไฟล์หลัก)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        self.lbl_file1 = ctk.CTkLabel(box1, text="ยังไม่ได้เลือกไฟล์", text_color="#768390")
        self.lbl_file1.pack()
        btn_f1 = ctk.CTkFrame(box1, fg_color="transparent")
        btn_f1.pack(pady=5)
        ctk.CTkButton(btn_f1, text="Browse", width=80, height=28, command=lambda: self.select_file(1), fg_color="#373e47", hover_color="#444c56").pack(side="left", padx=5)
        self.sheet_var1 = ctk.StringVar(value="Sheet")
        self.dropdown1 = ctk.CTkOptionMenu(btn_f1, variable=self.sheet_var1, values=["Sheet"], state="disabled", width=120)
        self.dropdown1.pack(side="left", padx=5)

        # ปุ่มสลับไฟล์
        ctk.CTkButton(sidebar, text="⇅ สลับไฟล์คู่เทียบ (Swap)", width=140, height=25, fg_color="#30363d", hover_color="#444c56", command=self.swap_files).pack(pady=5)

        # กล่อง 2
        box2 = ctk.CTkFrame(sidebar, fg_color="#22272e", corner_radius=10, border_width=1, border_color="#0033a0")
        box2.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(box2, text="2. Compare File (ไฟล์เทียบ)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        self.lbl_file2 = ctk.CTkLabel(box2, text="ยังไม่ได้เลือกไฟล์", text_color="#768390")
        self.lbl_file2.pack()
        btn_f2 = ctk.CTkFrame(box2, fg_color="transparent")
        btn_f2.pack(pady=5)
        ctk.CTkButton(btn_f2, text="Browse", width=80, height=28, command=lambda: self.select_file(2), fg_color="#373e47", hover_color="#444c56").pack(side="left", padx=5)
        self.sheet_var2 = ctk.StringVar(value="Sheet")
        self.dropdown2 = ctk.CTkOptionMenu(btn_f2, variable=self.sheet_var2, values=["Sheet"], state="disabled", width=120)
        self.dropdown2.pack(side="left", padx=5)

        # กล่อง Filter
        filter_box = ctk.CTkFrame(sidebar, fg_color="#22272e", corner_radius=10)
        filter_box.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(filter_box, text="🛠 ตัวกรองข้อมูล (Filters)", font=ctk.CTkFont(weight="bold")).pack(pady=(10,5))
        
        ctk.CTkLabel(filter_box, text="ระบุช่วงบรรทัด (เช่น 1-100)", text_color="#8b949e", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
        self.entry_row = ctk.CTkEntry(filter_box, placeholder_text="เว้นว่างไว้หากต้องการดูทั้งหมด", height=28)
        self.entry_row.pack(fill="x", padx=15, pady=(0,10))

        self.btn_col_filter = ctk.CTkButton(filter_box, text="⚙️ เลือกคอลัมน์ที่จะตรวจ...", fg_color="#1f538d", hover_color="#14375e", height=30, command=self.open_column_selector)
        self.btn_col_filter.pack(fill="x", padx=15, pady=(0,15))
        self.lbl_selected_cols = ctk.CTkLabel(filter_box, text="* เช็คทุกคอลัมน์ (ค่าเริ่มต้น)", text_color="#2ecc71", font=ctk.CTkFont(size=11))
        self.lbl_selected_cols.pack(pady=(0, 10))

        self.btn_compare = ctk.CTkButton(sidebar, text="COMPARE", fg_color="#005eb8", hover_color="#004b87", font=ctk.CTkFont(weight="bold"), height=45, command=self.run_comparison_thread)
        self.btn_compare.pack(fill="x", padx=15, pady=10)

        # --- MAIN AREA ---
        main_content = ctk.CTkFrame(self.main_container, fg_color="#161b22", corner_radius=15, border_width=1, border_color="#30363d")
        main_content.pack(side="right", fill="both", expand=True)

        self.lbl_compare_info = ctk.CTkLabel(main_content, text="กรุณาเลือกไฟล์เพื่อเปรียบเทียบ", font=ctk.CTkFont(size=15, weight="bold"), text_color="#8b949e")
        self.lbl_compare_info.pack(pady=(15, 5))

        head_frame = ctk.CTkFrame(main_content, fg_color="transparent")
        head_frame.pack(fill="x", padx=20, pady=5)
        self.lbl_summary = ctk.CTkLabel(head_frame, text="Dashboard Ready", font=ctk.CTkFont(size=18, weight="bold"))
        self.lbl_summary.pack(side="left")
        
        self.btn_export = ctk.CTkButton(head_frame, text="⬇ Export Excel", fg_color="#238636", hover_color="#2ea043", width=120, command=self.export_result, state="disabled")
        self.btn_export.pack(side="right")

        # Tabs
        self.tabview = ctk.CTkTabview(main_content, corner_radius=10, segmented_button_selected_color="#005eb8")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_all = self.tabview.add("แสดงผลทั้งหมด")
        self.tab_changed = self.tabview.add("📌 เฉพาะที่แก้ (Changed)")
        self.tab_new = self.tabview.add("✨ รายการใหม่ (New)")
        self.tab_del = self.tabview.add("❌ ถูกลบ (Deleted)")

        self.tree_all = self.create_treeview(self.tab_all)
        self.tree_changed = self.create_treeview(self.tab_changed)
        self.tree_new = self.create_treeview(self.tab_new)
        self.tree_del = self.create_treeview(self.tab_del)

        self.loading_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=15, border_width=2, border_color="#005eb8")
        self.spinner = CircularSpinner(self.loading_frame, bg="#161b22", width=100, height=100)
        self.spinner.pack(pady=(20, 10))
        self.loading_lbl = ctk.CTkLabel(self.loading_frame, text="กำลังประมวลผลข้อมูล...\nกรุณารอสักครู่", font=ctk.CTkFont(weight="bold"))
        self.loading_lbl.pack(pady=(0, 20), padx=30)

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
        ctk.CTkButton(btn_frame, text="บันทึก", width=100, fg_color="#2EA043", hover_color="#238636", command=save_selection).pack(side="left", padx=5)

    def create_treeview(self, parent):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#22272e", fieldbackground="#22272e", foreground="white", rowheight=30, borderwidth=0)
        style.map('Treeview', background=[('selected', '#005eb8')])
        style.configure("Treeview.Heading", background="#2d333b", foreground="white", relief="flat", font=('Arial', 10, 'bold'))
        
        def fixed_map(option):
            return [elm for elm in style.map("Treeview", query_opt=option) if elm[:2] != ("!disabled", "!selected")]
        style.map("Treeview", foreground=fixed_map("foreground"), background=fixed_map("background"))

        tree_scroll_y = ttk.Scrollbar(parent)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(parent, orient='horizontal')
        tree_scroll_x.pack(side="bottom", fill="x")

        tree = ttk.Treeview(parent, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)

        # 📌 จุดแก้ไขสำคัญ: ปรับแต่งโทนสีตารางให้อ่านง่ายและทำงาน 100%
        tree.tag_configure('Changed', background='#423519', foreground='#ffb833') 
        tree.tag_configure('New', background='#163820', foreground='#4ade80')     
        tree.tag_configure('Deleted', background='#451a1a', foreground='#f87171') 

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
            self.lbl_file1.configure(text=filename[:30]+"...", text_color="white")
            self.dropdown1.configure(values=sheets, state="normal")
            self.sheet_var1.set(sheets[0])
        else:
            self.file2_path = filepath
            self.lbl_file2.configure(text=filename[:30]+"...", text_color="white")
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
        self.lbl_compare_info.configure(text=f"📁 {fname1}   AND   📁 {fname2}", text_color="#00a0ff")

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
            self.lbl_summary.configure(text="✅ ข้อมูลตรงกัน 100%", text_color="#2ea043")
            self.btn_export.configure(state="disabled")
            self.clear_all_trees()
        else:
            counts = self.result_df['Status'].value_counts()
            chg = counts.get('Changed', 0)
            new = counts.get('New', 0)
            dlt = counts.get('Deleted', 0)
            
            msg = f"จุดที่เปลี่ยนแปลง {total_diff} รายการ (เปลี่ยน: {chg} | ใหม่: {new} | ลบ: {dlt})"
            self.lbl_summary.configure(text=msg, text_color="#f39c12")
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

# [เพิ่มใหม่] สั่งให้ทำงานฟังก์ชันเช็คอัปเดตก่อนเปิด UI ขึ้นมา
if __name__ == "__main__":
    check_for_updates() # แวะเช็คไฟล์ใน Shared Drive แปปนึง
    app = ExcelCompareApp()
    app.mainloop()