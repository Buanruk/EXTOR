import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import time
import random
import math

print("\n" + "="*50)
print(">>> RUNNING: EXTOR v4.0 - MIDNIGHT DARK THEME + SPLASH <<<")
print("="*50 + "\n")

import json
import sys
import subprocess
import urllib.request

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
            ans = messagebox.askyesno(
                "พบอัปเดตใหม่!",
                f"EXTOR มีเวอร์ชันใหม่ (v{latest_version})\n"
                f"ต้องการอัปเดตเดี๋ยวนี้เลยไหมครับ?\n"
                f"(ระบบจะดาวน์โหลดและติดตั้งอัตโนมัติ)"
            )
            root.destroy()
            if ans:
                dl = (f"https://github.com/Buanruk/EXTOR/releases/download/"
                      f"v{latest_version}/main_ui.exe")
                cur = sys.executable
                tmp = os.path.join(os.path.dirname(cur), "update_temp.exe")
                urllib.request.urlretrieve(dl, tmp)
                bat_path = os.path.join(os.path.dirname(cur), "updater.bat")
                with open(bat_path, "w", encoding="cp874") as bat:
                    bat.write('@echo off\ntimeout /t 2 /nobreak > nul\n')
                    bat.write(f'copy /y "{tmp}" "{cur}"\ndel "{tmp}"\n')
                    bat.write(f'start "" "{cur}"\ndel "%~f0"\n')
                subprocess.Popen([bat_path], shell=True)
                sys.exit()
    except Exception:
        pass
# =========================================================================

# ── Palette ───────────────────────────────────────────────────────────────
C = {
    # Base surfaces
    "root":      "#0D1117",   # GitHub-dark base
    "sidebar":   "#161B22",   # slightly lifted sidebar
    "card":      "#1C2333",   # card panels
    "input":     "#21262D",   # input fields
    "content":   "#161B22",   # main content

    # Borders
    "border":    "#30363D",
    "border2":   "#21262D",

    # Blues
    "blue":      "#388BFD",   # primary action
    "blue_h":    "#1F6FEB",   # hover
    "blue_dim":  "#1C2D48",   # very subtle tint
    "blue_glow": "#0D419D",   # glow behind

    # Accents
    "cyan":      "#79C0FF",
    "sky":       "#56D364",

    # Status
    "green":     "#3FB950",
    "green_dim": "#1B4721",
    "green_fg":  "#56D364",
    "amber":     "#D29922",
    "amber_dim": "#3D2F00",
    "amber_fg":  "#E3B341",
    "red":       "#DA3633",
    "red_dim":   "#3D0A09",
    "red_fg":    "#FF7B72",

    # Text
    "text":      "#E6EDF3",
    "text2":     "#8B949E",
    "muted":     "#6E7681",
    "placeholder":"#484F58",

    # Treeview (ttk — explicit hex required)
    "tree_bg":    "#161B22",
    "tree_row":   "#1C2333",
    "tree_alt":   "#161B22",
    "tree_head":  "#21262D",
    "tree_fg":    "#C9D1D9",
    "tree_sel":   "#1F6FEB",
    "tree_sfg":   "#FFFFFF",
    "chg_bg":     "#2D2100",
    "chg_fg":     "#E3B341",
    "new_bg":     "#122820",
    "new_fg":     "#56D364",
    "del_bg":     "#2D0A09",
    "del_fg":     "#FF7B72",
}

# =========================================================================
# Always-moving star field
# =========================================================================
class StarField(ctk.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self._stars = []
        self._nebulas = []
        self._ready = False
        self.bind("<Configure>", self._on_configure)
        self._tick()

    def _on_configure(self, event=None):
        if event and (event.width < 10 or event.height < 10):
            return
        self.delete("all")
        self._stars.clear()
        self._nebulas.clear()
        w = self.winfo_width()
        h = self.winfo_height()

        blob_palette = [
            "#0D1F3C", "#0A1A2E", "#102030",
            "#0E1C28", "#091520", "#0C1830",
        ]
        for _ in range(10):
            r = random.randint(180, 480)
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.08, 0.25)
            color = random.choice(blob_palette)
            oid = self.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            self._nebulas.append({
                "id": oid, "r": r,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
            })

        star_colors = [
            "#FFFFFF", "#C8D3F5", "#A9B8E8",
            "#7DCFFF", "#89DDFF", "#B4F9F8",
            "#FFE57A",
        ]
        for _ in range(220):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            size = random.choice([1, 1, 1, 2, 2, 3])
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.05, 0.45)
            color = random.choice(star_colors)
            oid = self.create_oval(x, y, x+size, y+size,
                                   fill=color, outline="")
            self._stars.append({
                "id": oid, "size": size,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
            })

        self._ready = True

    def _tick(self):
        if self._ready:
            w = self.winfo_width()
            h = self.winfo_height()

            for b in self._nebulas:
                self.move(b["id"], b["dx"], b["dy"])
                x1, y1, x2, y2 = self.coords(b["id"])
                cx, cy = (x1+x2)/2, (y1+y2)/2
                r = b["r"]
                if cx < -r:
                    self.move(b["id"], w + r*2, 0)
                elif cx > w + r:
                    self.move(b["id"], -(w + r*2), 0)
                if cy < -r:
                    self.move(b["id"], 0, h + r*2)
                elif cy > h + r:
                    self.move(b["id"], 0, -(h + r*2))

            for s in self._stars:
                self.move(s["id"], s["dx"], s["dy"])
                coords = self.coords(s["id"])
                if not coords:
                    continue
                x1, y1, x2, y2 = coords
                if x1 > w:
                    self.coords(s["id"], -s["size"], y1,
                                0, y1 + s["size"])
                elif x2 < 0:
                    self.coords(s["id"], w, y1,
                                w + s["size"], y1 + s["size"])
                if y1 > h:
                    self.coords(s["id"], x1, -s["size"],
                                x1 + s["size"], 0)
                elif y2 < 0:
                    self.coords(s["id"], x1, h,
                                x1 + s["size"], h + s["size"])

        self.after(25, self._tick)

# =========================================================================
# Spinner
# =========================================================================
class Spinner(ctk.CTkCanvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.angle = 0
        self.running = False

    def start(self):
        self.running = True
        self._tick()

    def stop(self):
        self.running = False
        self.delete("all")

    def _tick(self):
        if not self.running:
            return
        self.delete("all")
        cx = self.winfo_width() / 2
        cy = self.winfo_height() / 2
        rings = [
            (36, 7, C["blue"],   1.0),
            (24, 5, C["cyan"],   0.75),
            (13, 4, "#79C0FF",   0.5),
        ]
        for r, lw, col, ph in rings:
            a = self.angle * ph
            self.create_arc(cx-r, cy-r, cx+r, cy+r,
                            start=a, extent=215,
                            outline=col, width=lw, style="arc")
        self.angle = (self.angle - 9) % 360
        self.after(18, self._tick)

# =========================================================================
# Logo
# =========================================================================
class LogoBadge(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(anchor="w")

        bar = ctk.CTkFrame(wrap, width=4, fg_color=C["blue"], corner_radius=2)
        bar.pack(side="left", fill="y", padx=(0, 10), pady=2)

        col = ctk.CTkFrame(wrap, fg_color="transparent")
        col.pack(side="left")

        row = ctk.CTkFrame(col, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text="EX",
                     font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
                     text_color=C["blue"]).pack(side="left")
        ctk.CTkLabel(row, text="TOR",
                     font=ctk.CTkFont(family="Georgia", size=26, weight="bold"),
                     text_color=C["text"]).pack(side="left")

        ctk.CTkLabel(col, text="Data Reconciler System",
                     font=ctk.CTkFont(family="Georgia", size=10),
                     text_color=C["muted"]).pack(anchor="w")

# =========================================================================
# Helpers
# =========================================================================
def divider(parent, padx=16, pady=8):
    ctk.CTkFrame(parent, height=1, fg_color=C["border"],
                 corner_radius=0).pack(fill="x", padx=padx, pady=pady)

def sec_label(parent, text, icon=""):
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=16, pady=(12, 3))
    if icon:
        ctk.CTkLabel(r, text=icon, font=ctk.CTkFont(size=12),
                     text_color=C["blue"]).pack(side="left")
    ctk.CTkLabel(r, text=f"  {text}",
                 font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
                 text_color=C["text2"]).pack(side="left")

def card(parent):
    return ctk.CTkFrame(parent, fg_color=C["card"],
                        corner_radius=8,
                        border_width=1, border_color=C["border"])

def primary_btn(parent, text, cmd, w=100, h=36):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color=C["blue"], hover_color=C["blue_h"],
        text_color="#FFFFFF",
        font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
        width=w, height=h, corner_radius=6)

def ghost_btn(parent, text, cmd, w=100, h=36, tc=None, bc=None):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color="transparent", hover_color=C["blue_dim"],
        text_color=tc or C["blue"],
        border_color=bc or C["blue"], border_width=1,
        font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
        width=w, height=h, corner_radius=6)

def status_pill(parent, text, bg, fg, border):
    f = ctk.CTkFrame(parent, fg_color=bg, corner_radius=6,
                     border_width=1, border_color=border)
    f.pack(side="left", padx=(0, 8))
    lbl = ctk.CTkLabel(f, text=f"  {text}  ",
                       font=ctk.CTkFont(family="Georgia", size=11, weight="bold"),
                       text_color=fg)
    lbl.pack(padx=2, pady=4)
    return lbl

# =========================================================================
# Main App
# =========================================================================
class ExcelCompareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 📌 ซ่อนหน้าต่างหลักเอาไว้ก่อน เพื่อโชว์ Splash Screen
        self.withdraw()
        
        self.title("EXTOR  —  Data Reconciler")
        self.geometry("1440x860")
        self.minsize(1100, 700)
        self.configure(fg_color=C["root"])

        self.bg = StarField(self, bg=C["root"])
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.file1_path = ""
        self.file2_path = ""
        self.selected_columns = []
        self.result_df = None
        self.processor = DataReconciler()

        self._build()
        if windnd:
            windnd.hook_dropfiles(self, func=self._on_drop)
            
        # 📌 เรียกใช้งานหน้าจอโหลด 3 วินาที
        self.show_splash_screen()

    # =========================================================================
    # โซนระบบหน้าจอโหลด (SPLASH SCREEN)
    # =========================================================================
    def show_splash_screen(self):
        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True) # ซ่อนขอบหน้าต่าง
        
        width, height = 550, 320
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        splash.geometry(f"{width}x{height}+{x}+{y}")
        splash.attributes('-topmost', True)
        
        # กรอบเรืองแสงสีฟ้านีออนสไตล์ Midnight Dark
        frame = ctk.CTkFrame(splash, fg_color=C["root"], border_width=2, border_color=C["blue"], corner_radius=0)
        frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(frame, text="EXTOR", font=ctk.CTkFont(family="Georgia", size=50, weight="bold"), text_color=C["blue"]).pack(pady=(65, 5))
        ctk.CTkLabel(frame, text="Data Reconciler System v4.0", font=ctk.CTkFont(size=15), text_color=C["text2"]).pack(pady=(0, 45))
        
        # หลอด Progress Bar
        progress = ctk.CTkProgressBar(frame, width=380, height=8, fg_color=C["input"], progress_color=C["blue"])
        progress.pack(pady=10)
        progress.set(0)
        
        lbl_loading = ctk.CTkLabel(frame, text="Initializing systems...", text_color=C["muted"], font=ctk.CTkFont(size=12))
        lbl_loading.pack(pady=5)
        
        # เริ่มการโหลด (วิ่ง 100 รอบ รอบละ 30ms = 3000ms หรือ 3 วินาทีถ้วน)
        self.update_splash(splash, progress, lbl_loading, 0)

    def update_splash(self, splash, progress, lbl_loading, value):
        if value <= 100:
            progress.set(value / 100)
            
            # เปลี่ยนข้อความตามจังหวะโหลด
            if value == 20:
                lbl_loading.configure(text="Loading Midnight Dark interface...")
            elif value == 50:
                lbl_loading.configure(text="Connecting data processor algorithms...")
            elif value == 80:
                lbl_loading.configure(text="Preparing starfield engine...")
            elif value == 95:
                lbl_loading.configure(text="Ready to launch!")
            
            # เรียกซ้ำตัวเองทุกๆ 30ms
            self.after(30, self.update_splash, splash, progress, lbl_loading, value + 1)
        else:
            # ครบ 100% ทำลายหน้าโหลดแล้วขยายแอปหลัก
            splash.destroy()
            self.deiconify() 
            try:
                self.state('zoomed')
            except Exception:
                pass
    # =========================================================================

    def _tree_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("X.Treeview",
                    background=C["tree_bg"],
                    fieldbackground=C["tree_bg"],
                    foreground=C["tree_fg"],
                    rowheight=36,
                    borderwidth=0,
                    relief="flat",
                    font=("Segoe UI", 10))
        s.map("X.Treeview",
              background=[("selected", C["tree_sel"])],
              foreground=[("selected", C["tree_sfg"])])
        s.configure("X.Treeview.Heading",
                    background=C["tree_head"],
                    foreground=C["text2"],
                    relief="flat",
                    borderwidth=0,
                    font=("Segoe UI", 10, "bold"),
                    padding=8)
        s.map("X.Treeview.Heading",
              background=[("active", C["blue_dim"])],
              relief=[("active", "flat")])
        s.layout("X.Treeview", [
            ("X.Treeview.treearea", {"sticky": "nswe"})
        ])
        s.configure("X.Vertical.TScrollbar",
                    background=C["border"], troughcolor=C["card"],
                    borderwidth=0, arrowsize=0, relief="flat")
        s.configure("X.Horizontal.TScrollbar",
                    background=C["border"], troughcolor=C["card"],
                    borderwidth=0, arrowsize=0, relief="flat")
        s.map("X.Vertical.TScrollbar",
              background=[("active", C["blue"]), ("!active", C["border"])])
        s.map("X.Horizontal.TScrollbar",
              background=[("active", C["blue"]), ("!active", C["border"])])

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        sb_outer = ctk.CTkFrame(outer, width=300,
                                fg_color=C["sidebar"],
                                corner_radius=10,
                                border_width=1,
                                border_color=C["border"])
        sb_outer.pack(side="left", fill="y", padx=(0, 14))
        sb_outer.pack_propagate(False)

        sb = ctk.CTkScrollableFrame(sb_outer,
                                    fg_color="transparent",
                                    scrollbar_button_color=C["border"],
                                    scrollbar_button_hover_color=C["blue"])
        sb.pack(fill="both", expand=True)

        logo_wrap = ctk.CTkFrame(sb, fg_color="transparent")
        logo_wrap.pack(fill="x", padx=16, pady=(20, 12))
        LogoBadge(logo_wrap).pack(anchor="w")

        divider(sb)

        sec_label(sb, "Base File  (ไฟล์หลัก)", "①")
        c1 = card(sb)
        c1.pack(fill="x", padx=14, pady=(2, 0))

        self.lbl_file1 = ctk.CTkLabel(c1, text="ยังไม่ได้เลือกไฟล์",
                                       text_color=C["placeholder"],
                                       font=ctk.CTkFont(size=11),
                                       wraplength=240, justify="left")
        self.lbl_file1.pack(anchor="w", padx=12, pady=(10, 4))

        r1 = ctk.CTkFrame(c1, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=(0, 10))
        primary_btn(r1, "Browse", lambda: self.select_file(1),
                    w=80, h=32).pack(side="left", padx=(0, 6))
        self.sheet_var1 = ctk.StringVar(value="เลือก Sheet")
        self.dropdown1 = ctk.CTkOptionMenu(
            r1, variable=self.sheet_var1,
            values=["เลือก Sheet"], state="disabled",
            width=152, height=32, corner_radius=6,
            fg_color=C["input"], button_color=C["border"],
            button_hover_color=C["border"],
            text_color=C["text"],
            font=ctk.CTkFont(size=11), dynamic_resizing=False)
        self.dropdown1.pack(side="left")

        ghost_btn(sb, "⇅  สลับไฟล์  (Swap)", self.swap_files,
                  w=272, h=30,
                  tc=C["text2"], bc=C["border"]).pack(padx=14, pady=6)

        sec_label(sb, "Compare File  (ไฟล์เทียบ)", "②")
        c2 = card(sb)
        c2.pack(fill="x", padx=14, pady=(2, 0))

        self.lbl_file2 = ctk.CTkLabel(c2, text="ยังไม่ได้เลือกไฟล์",
                                       text_color=C["placeholder"],
                                       font=ctk.CTkFont(size=11),
                                       wraplength=240, justify="left")
        self.lbl_file2.pack(anchor="w", padx=12, pady=(10, 4))

        r2 = ctk.CTkFrame(c2, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=(0, 10))
        primary_btn(r2, "Browse", lambda: self.select_file(2),
                    w=80, h=32).pack(side="left", padx=(0, 6))
        self.sheet_var2 = ctk.StringVar(value="เลือก Sheet")
        self.dropdown2 = ctk.CTkOptionMenu(
            r2, variable=self.sheet_var2,
            values=["เลือก Sheet"], state="disabled",
            width=152, height=32, corner_radius=6,
            fg_color=C["input"], button_color=C["border"],
            button_hover_color=C["border"],
            text_color=C["text"],
            font=ctk.CTkFont(size=11), dynamic_resizing=False)
        self.dropdown2.pack(side="left")

        divider(sb)

        sec_label(sb, "ตัวกรองข้อมูล")

        ctk.CTkLabel(sb, text="ช่วงบรรทัด  (เช่น 1-100)",
                     font=ctk.CTkFont(size=11),
                     text_color=C["text2"]).pack(anchor="w", padx=16, pady=(2, 2))
        self.entry_row = ctk.CTkEntry(
            sb, placeholder_text="เว้นว่างหากต้องการทั้งหมด",
            height=34, corner_radius=6,
            fg_color=C["input"], border_color=C["border"],
            border_width=1, text_color=C["text"],
            font=ctk.CTkFont(size=11))
        self.entry_row.pack(fill="x", padx=14, pady=(0, 8))

        ghost_btn(sb, "⊞  เลือกคอลัมน์ที่จะตรวจ...",
                  self.open_column_selector,
                  w=272, h=34).pack(padx=14)

        self.lbl_sel_cols = ctk.CTkLabel(
            sb, text="เช็คทุกคอลัมน์  (ค่าเริ่มต้น)",
            text_color=C["green_fg"],
            font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_sel_cols.pack(pady=(6, 0))

        divider(sb, pady=10)

        self.btn_compare = ctk.CTkButton(
            sb, text="▶  COMPARE DATA",
            fg_color=C["blue"], hover_color=C["blue_h"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
            height=46, corner_radius=8,
            command=self.run_comparison_thread)
        self.btn_compare.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(sb, text=f"v{APP_VERSION}",
                     font=ctk.CTkFont(size=10),
                     text_color=C["muted"]).pack(pady=(0, 14))

        content = ctk.CTkFrame(outer,
                               fg_color=C["content"],
                               corner_radius=10,
                               border_width=1,
                               border_color=C["border"])
        content.pack(side="right", fill="both", expand=True)

        hdr = ctk.CTkFrame(content, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(16, 0))

        info_col = ctk.CTkFrame(hdr, fg_color="transparent")
        info_col.pack(side="left", fill="y")

        self.lbl_compare_info = ctk.CTkLabel(
            info_col,
            text="เลือกไฟล์เพื่อเริ่มการเปรียบเทียบ",
            font=ctk.CTkFont(size=11), text_color=C["muted"])
        self.lbl_compare_info.pack(anchor="w")

        self.lbl_summary = ctk.CTkLabel(
            info_col,
            text="Dashboard Ready",
            font=ctk.CTkFont(family="Georgia", size=19, weight="bold"),
            text_color=C["text"])
        self.lbl_summary.pack(anchor="w", pady=(2, 0))

        self.btn_export = ctk.CTkButton(
            hdr, text="↓  Export Excel",
            fg_color=C["green"], hover_color="#2EA043",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Georgia", size=12, weight="bold"),
            width=148, height=36, corner_radius=6,
            command=self.export_result, state="disabled")
        self.btn_export.pack(side="right", anchor="center")

        ctk.CTkFrame(content, height=2, fg_color=C["blue"],
                     corner_radius=0).pack(fill="x", padx=20, pady=(10, 0))

        self.pill_row = ctk.CTkFrame(content, fg_color="transparent")
        self.pill_row.pack(fill="x", padx=20, pady=(8, 4))
        self._pills = {}
        for key, txt, bg, fg, bd in [
            ("changed", "—  เปลี่ยนแปลง", C["amber_dim"], C["amber_fg"], C["amber"]),
            ("new",     "—  รายการใหม่",  C["green_dim"], C["green_fg"], C["green"]),
            ("deleted", "—  ถูกลบ",        C["red_dim"],   C["red_fg"],   C["red"]),
        ]:
            self._pills[key] = status_pill(self.pill_row, txt, bg, fg, bd)

        self._tree_style()

        self.tabview = ctk.CTkTabview(
            content, corner_radius=8,
            fg_color=C["content"],
            segmented_button_fg_color=C["card"],
            segmented_button_selected_color=C["blue"],
            segmented_button_selected_hover_color=C["blue_h"],
            segmented_button_unselected_color=C["card"],
            segmented_button_unselected_hover_color=C["blue_dim"],
            text_color=C["text2"],
            border_width=0)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.tab_all     = self.tabview.add("  ทั้งหมด  ")
        self.tab_changed = self.tabview.add("  📌 Changed  ")
        self.tab_new     = self.tabview.add("  ✨ New  ")
        self.tab_del     = self.tabview.add("  ❌ Deleted  ")

        self.tree_all     = self._make_tree(self.tab_all)
        self.tree_changed = self._make_tree(self.tab_changed)
        self.tree_new     = self._make_tree(self.tab_new)
        self.tree_del     = self._make_tree(self.tab_del)

        self._build_loading()

    def _build_loading(self):
        self.loading_frame = ctk.CTkFrame(
            self, fg_color=C["card"],
            corner_radius=12,
            border_width=1, border_color=C["blue"])
        self.spinner = Spinner(self.loading_frame,
                               bg=C["card"], width=92, height=92)
        self.spinner.pack(pady=(28, 6))
        ctk.CTkLabel(self.loading_frame, text="EXTOR",
                     font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
                     text_color=C["blue"]).pack()
        self.loading_lbl = ctk.CTkLabel(
            self.loading_frame,
            text="กำลังประมวลผลข้อมูล...\nกรุณารอสักครู่",
            font=ctk.CTkFont(size=12), text_color=C["text2"])
        self.loading_lbl.pack(pady=(4, 28), padx=52)

    def _make_tree(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color=C["tree_bg"],
                            corner_radius=0, border_width=0)
        wrap.pack(fill="both", expand=True)

        sy = ttk.Scrollbar(wrap, orient="vertical",
                           style="X.Vertical.TScrollbar")
        sy.pack(side="right", fill="y")
        sx = ttk.Scrollbar(wrap, orient="horizontal",
                           style="X.Horizontal.TScrollbar")
        sx.pack(side="bottom", fill="x")

        tree = ttk.Treeview(wrap, style="X.Treeview",
                             yscrollcommand=sy.set,
                             xscrollcommand=sx.set)
        tree.pack(fill="both", expand=True)
        sy.config(command=tree.yview)
        sx.config(command=tree.xview)
        tree.bind("<Double-1>", lambda e, t=tree: self.show_row_details(e, t))

        tree.tag_configure("Changed",
                            background=C["chg_bg"], foreground=C["chg_fg"])
        tree.tag_configure("New",
                            background=C["new_bg"], foreground=C["new_fg"])
        tree.tag_configure("Deleted",
                            background=C["del_bg"], foreground=C["del_fg"])
        return tree

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
        t1, t2 = self.lbl_file1.cget("text"), self.lbl_file2.cget("text")
        self.lbl_file1.configure(text=t2)
        self.lbl_file2.configure(text=t1)
        v1 = self.dropdown1.cget("values")
        v2 = self.dropdown2.cget("values")
        s1 = self.dropdown1.cget("state")
        s2 = self.dropdown2.cget("state")
        c1, c2 = self.sheet_var1.get(), self.sheet_var2.get()
        self.dropdown1.configure(values=v2, state=s2)
        self.dropdown2.configure(values=v1, state=s1)
        self.sheet_var1.set(c2)
        self.sheet_var2.set(c1)

    def open_column_selector(self):
        if not self.file1_path:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณาใส่ไฟล์ในช่องที่ 1 ก่อนครับ")
            return
        try:
            columns = self.processor.get_columns(
                self.file1_path, self.sheet_var1.get())
        except Exception as e:
            messagebox.showerror("อ่านคอลัมน์ไม่สำเร็จ", str(e))
            return

        top = ctk.CTkToplevel(self)
        top.title("เลือกคอลัมน์")
        top.geometry("440x560")
        top.configure(fg_color=C["sidebar"])
        top.grab_set()

        ctk.CTkLabel(top, text="เลือกคอลัมน์ที่ต้องการเปรียบเทียบ",
                     font=ctk.CTkFont(family="Georgia", size=14, weight="bold"),
                     text_color=C["text"]).pack(pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(top, width=380, height=360,
                                         fg_color=C["card"],
                                         corner_radius=8,
                                         border_width=1,
                                         border_color=C["border"])
        scroll.pack(padx=22, pady=6, fill="both", expand=True)

        checkboxes = {}
        for col in columns:
            if col in self.processor.key_cols:
                continue
            var = ctk.BooleanVar(
                value=(col in self.selected_columns)
                if self.selected_columns else True)
            cb = ctk.CTkCheckBox(scroll, text=col, variable=var,
                                  corner_radius=4,
                                  border_color=C["border"],
                                  fg_color=C["blue"],
                                  hover_color=C["blue_h"],
                                  text_color=C["text"],
                                  font=ctk.CTkFont(size=12))
            cb.pack(anchor="w", pady=6, padx=14)
            checkboxes[col] = var

        def save():
            self.selected_columns = [
                c for c, v in checkboxes.items() if v.get()]
            self.lbl_sel_cols.configure(
                text=f"เลือกแล้ว {len(self.selected_columns)} คอลัมน์",
                text_color=C["amber_fg"])
            top.destroy()

        br = ctk.CTkFrame(top, fg_color="transparent")
        br.pack(pady=12)
        ghost_btn(br, "เลือกทั้งหมด",
                  lambda: [v.set(True) for v in checkboxes.values()],
                  w=106, h=32).pack(side="left", padx=4)
        ghost_btn(br, "ล้างทั้งหมด",
                  lambda: [v.set(False) for v in checkboxes.values()],
                  w=106, h=32,
                  tc=C["text2"], bc=C["border"]).pack(side="left", padx=4)
        primary_btn(br, "บันทึก", save,
                    w=106, h=32).pack(side="left", padx=4)

    def show_row_details(self, event, tree):
        sel = tree.selection()
        if not sel:
            return
        item = tree.item(sel[0])
        values = item["values"]
        columns = tree["columns"]
        tags = item.get("tags", [])
        status = tags[0] if tags else "Normal"

        win = ctk.CTkToplevel(self)
        win.title("Grid Inspector  —  รายละเอียด")
        win.geometry("640x680")
        win.configure(fg_color=C["sidebar"])
        win.grab_set()

        badge_map = {
            "Changed": (C["amber_dim"], C["amber_fg"], C["amber"]),
            "New":     (C["green_dim"], C["green_fg"], C["green"]),
            "Deleted": (C["red_dim"],   C["red_fg"],   C["red"]),
        }
        bg, fg, bd = badge_map.get(status, (C["blue_dim"], C["cyan"], C["blue"]))
        badge = ctk.CTkFrame(win, fg_color=bg, corner_radius=6,
                              border_width=1, border_color=bd)
        badge.pack(anchor="w", padx=22, pady=(18, 10))
        ctk.CTkLabel(badge, text=f"  {status}  ",
                     font=ctk.CTkFont(family="Georgia", size=13, weight="bold"),
                     text_color=fg).pack(padx=6, pady=5)

        scroll = ctk.CTkScrollableFrame(win, width=594,
                                         fg_color=C["card"],
                                         corner_radius=8,
                                         border_width=1,
                                         border_color=C["border"])
        scroll.pack(padx=22, pady=(0, 18), fill="both", expand=True)

        changed_data, normal_data = [], []
        for col, val in zip(columns, values):
            vs = str(val)
            if "->" in vs or (status == "Changed" and "[" in vs and "]" in vs):
                changed_data.append((col, vs))
            else:
                normal_data.append((col, vs))

        def render(title, tc, data, hbg, rbg1, rbg2, vfg):
            ctk.CTkLabel(scroll, text=title,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=tc).pack(anchor="w",
                                              pady=(12, 5), padx=6)
            tbl = ctk.CTkFrame(scroll, fg_color=hbg,
                                corner_radius=6,
                                border_width=1, border_color=C["border"])
            tbl.pack(fill="x", padx=4, pady=(0, 10))
            tbl.columnconfigure(0, weight=1)
            tbl.columnconfigure(1, weight=3)
            for ci, ht in enumerate(["คอลัมน์", "ข้อมูล"]):
                ctk.CTkLabel(tbl, text=f"  {ht}",
                             fg_color=hbg, text_color=C["text2"],
                             font=ctk.CTkFont(size=11, weight="bold"),
                             anchor="w").grid(row=0, column=ci,
                                               sticky="nsew",
                                               padx=1, pady=(2, 1), ipady=7)
            for i, (col, val) in enumerate(data):
                rb = rbg1 if i % 2 == 0 else rbg2
                ctk.CTkLabel(tbl, text=f"  {col}",
                             fg_color=rb, text_color=C["muted"],
                             anchor="w",
                             font=ctk.CTkFont(size=11)).grid(
                    row=i+1, column=0, sticky="nsew",
                    padx=1, pady=1, ipady=7)
                ctk.CTkLabel(tbl, text=f"  {val}",
                             fg_color=rb, text_color=vfg,
                             anchor="w",
                             font=ctk.CTkFont(size=11, weight="bold")).grid(
                    row=i+1, column=1, sticky="nsew",
                    padx=1, pady=1, ipady=7)

        if changed_data:
            render("คอลัมน์ที่เปลี่ยนแปลง", C["amber_fg"],
                   changed_data,
                   C["amber_dim"], "#261900", "#1E1400", C["amber_fg"])
        if normal_data:
            render("✓  ข้อมูลปกติ", C["text2"],
                   normal_data,
                   C["card"], C["input"], C["card"], C["text"])
        if not changed_data and status in ["New", "Deleted"]:
            ctk.CTkLabel(scroll,
                         text="รายการนี้ถูกเพิ่มหรือลบทั้งบรรทัด\nไม่มีการเปลี่ยนค่ารายเซลล์",
                         text_color=C["muted"],
                         font=ctk.CTkFont(size=13)).pack(pady=50)

    def _decode(self, fb):
        for enc in ["utf-8", "cp874", "tis-620", "ansi"]:
            try:
                return fb.decode(enc)
            except Exception:
                continue
        return str(fb)

    def _on_drop(self, files):
        for fb in files:
            fp = self._decode(fb)
            if not (fp.lower().endswith(".xlsx") or fp.lower().endswith(".csv")):
                messagebox.showwarning("Type Error", "รองรับเฉพาะ .xlsx และ .csv")
                return
            mx = self.winfo_pointerx() - self.winfo_rootx()
            self.load_file_to_box(fp, 1 if mx < 320 else 2)

    def load_file_to_box(self, filepath, box_num):
        name = os.path.basename(filepath)
        try:
            sheets = self.processor.get_sheet_names(filepath)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        disp = name[:34] + ("…" if len(name) > 34 else "")
        if box_num == 1:
            self.file1_path = filepath
            self.lbl_file1.configure(text=disp, text_color=C["text"])
            self.dropdown1.configure(values=sheets, state="normal")
            self.sheet_var1.set(sheets[0])
        else:
            self.file2_path = filepath
            self.lbl_file2.configure(text=disp, text_color=C["text"])
            self.dropdown2.configure(values=sheets, state="normal")
            self.sheet_var2.set(sheets[0])

    def select_file(self, fn):
        fp = filedialog.askopenfilename(
            filetypes=[("Excel & CSV", "*.xlsx *.csv")])
        if fp:
            self.load_file_to_box(fp, fn)

    def run_comparison_thread(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("Warning",
                                   "กรุณาเลือกไฟล์ให้ครบทั้ง 2 ฝั่งครับ")
            return
        s1, s2 = self.sheet_var1.get(), self.sheet_var2.get()
        if "เลือก" in s1 or "เลือก" in s2:
            messagebox.showwarning("Warning", "กรุณาเลือก Sheet ด้วยครับ")
            return
        f1 = os.path.basename(self.file1_path)
        f2 = os.path.basename(self.file2_path)
        self.lbl_compare_info.configure(
            text=f"{f1}   ⇄   {f2}",
            text_color=C["cyan"])
        self.show_loading()
        threading.Thread(
            target=self._process, args=(s1, s2), daemon=True).start()

    def _process(self, s1, s2):
        row_lim = self.entry_row.get()
        cols = self.selected_columns if self.selected_columns else None
        try:
            time.sleep(0.35)
            self.result_df = self.processor.compare_data(
                self.file1_path, s1,
                self.file2_path, s2,
                target_cols=cols,
                row_range=row_lim)
            self.after(0, self._update_ui)
        except Exception as e:
            self.after(0, self.hide_loading)
            self.after(0, lambda: messagebox.showerror("เกิดข้อผิดพลาด", str(e)))

    def _update_ui(self):
        self.hide_loading()
        total = len(self.result_df)
        if total == 0:
            self.lbl_summary.configure(text="✅  ข้อมูลตรงกัน 100%",
                                        text_color=C["green_fg"])
            self.btn_export.configure(state="disabled")
            self._clear_trees()
            self._update_pills(0, 0, 0)
        else:
            vc = self.result_df["Status"].value_counts()
            chg = vc.get("Changed", 0)
            new = vc.get("New",     0)
            dlt = vc.get("Deleted", 0)
            self.lbl_summary.configure(
                text=f"พบ {total} รายการที่แตกต่าง",
                text_color=C["amber_fg"])
            self.btn_export.configure(state="normal")
            self._update_pills(chg, new, dlt)
            self._fill(self.tree_all,     self.result_df)
            self._fill(self.tree_changed,
                       self.result_df[self.result_df["Status"] == "Changed"])
            self._fill(self.tree_new,
                       self.result_df[self.result_df["Status"] == "New"])
            self._fill(self.tree_del,
                       self.result_df[self.result_df["Status"] == "Deleted"])

    def _update_pills(self, chg, new, dlt):
        self._pills["changed"].configure(text=f"  {chg}  เปลี่ยนแปลง  ")
        self._pills["new"].configure(text=f"  {new}  รายการใหม่  ")
        self._pills["deleted"].configure(text=f"  {dlt}  ถูกลบ  ")

    def _clear_trees(self):
        for t in [self.tree_all, self.tree_changed,
                  self.tree_new, self.tree_del]:
            t.delete(*t.get_children())

    def _fill(self, tree, df):
        tree.delete(*tree.get_children())
        if df.empty:
            return
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"
        for col in df.columns:
            tree.heading(col, text=col)
            w = 130 if col not in self.processor.key_cols else 100
            tree.column(col, width=w, minwidth=80)
        for _, row in df.iterrows():
            rd = ["" if pd.isna(x) else str(x) for x in row]
            st = row.get("Status", "")
            tree.insert("", "end", values=rd, tags=(st,))

    # 📌 ฟังก์ชันส่งออกที่อัปเดตใหม่
    def export_result(self):
        if self.result_df is None or self.result_df.empty:
            return
        sp = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="EXTOR_Reconcile_Result.xlsx")
        
        if sp:
            # 📌 เด้ง Loading ให้ User รอกระบวนการหลังบ้าน
            self.show_loading()
            self.loading_lbl.configure(text="กำลังสร้างไฟล์ต้นฉบับ...\nและวิเคราะห์สีจัดส่ง (AIR/OCEAN/TRUCK)")
            
            # รันการเซฟไฟล์ใน Thread เพื่อไม่ให้หน้าจอค้าง
            threading.Thread(target=self._run_export_backend, args=(sp,), daemon=True).start()

    def _run_export_backend(self, save_path):
        try:
            # เรียกใช้ฟังก์ชัน Openpyxl ที่เราเพิ่งเขียนไว้ใน core_logic.py
            self.processor.export_excel(save_path)
            self.after(0, self.hide_loading)
            self.after(0, lambda: messagebox.showinfo("Success", "ส่งออกไฟล์ Excel สำเร็จ!\nเพิ่ม Sheet: Transport_Report พร้อมแยกสีเรียบร้อยครับ ✓"))
        except Exception as e:
            self.after(0, self.hide_loading)
            self.after(0, lambda: messagebox.showerror("Export Error", f"ไม่สามารถบันทึกไฟล์ได้:\n{str(e)}"))

if __name__ == "__main__":
    check_for_updates()
    app = ExcelCompareApp()
    app.mainloop()