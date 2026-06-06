import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import threading
import time
import random
import math

print("\n" + "="*60)
print(">>> RUNNING: EXTOR v5.0 - DARK UX/UI EDITION <<<")
print("="*60 + "\n")

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

# โหมดมืด คุมโทน UI/UX สบายตา
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

# ── DARK SLATE & UX/UI PALETTE ──────────────────────────────────────────────
C = {
    # Base Theme: เทาเข้มเกือบดำ สบายตา (Charcoal/Dark Slate)
    "root":       "#181A1B",   
    "sidebar":    "#202324",   
    "glass":      "#2A2D2E",   
    "input":      "#181A1B",   
    "content":    "#181A1B",   

    # Borders บางๆ คลีนๆ
    "border":     "#3F4448",
    "border2":    "#4B5155",
    "glass_edge": "#3F4448",

    # UI/UX Primary Action Button (เด่นเด้งตามหลัก UX)
    "primary":    "#2563EB",   # Standard UI Blue
    "primary_h":  "#1D4ED8",   # Hover Blue
    "primary_fg": "#FFFFFF",

    # Status Indicators (Muted Colors: เขียวตุ่น, แดงหม่น, เหลืองอมเทา)
    "green":      "#10B981",   
    "green_dim":  "#064E3B",   # เขียวเข้มจัด (พื้นหลัง)
    "green_fg":   "#A7F3D0",   # เขียวสว่างหม่น (ตัวอักษร)
    
    "amber":      "#F59E0B",
    "amber_dim":  "#78350F",   # เหลืองอมน้ำตาล (พื้นหลัง)
    "amber_fg":   "#FDE68A",   # เหลืองอ่อน (ตัวอักษร)
    
    "red":        "#EF4444",
    "red_dim":    "#7F1D1D",   # แดงหม่นเข้ม (พื้นหลัง)
    "red_fg":     "#FECACA",   # แดงอ่อน (ตัวอักษร)

    # Text: ขาวหม่น (Off-white) ลด Contrast
    "text":       "#FFFFFF",   
    "text2":      "#FFFFFF",   
    "muted":      "#FFFFFF",   
    "placeholder":"#6B7280",

    # Treeview Muted Colors
    "tree_bg":    "#202324",
    "tree_row":   "#202324",
    "tree_alt":   "#2A2D2E",
    "tree_head":  "#181A1B",
    "tree_fg":    "#D1D5DB",
    "tree_sel":   "#374151",
    "tree_sfg":   "#F3F4F6",
    
    "chg_bg":     "#422C10",   # โทนตุ่นสำหรับพื้นหลังตารางแถว Changed
    "chg_fg":     "#FDE68A",
    "new_bg":     "#064E3B",   # โทนตุ่นสำหรับพื้นหลังตารางแถว New
    "new_fg":     "#A7F3D0",
    "del_bg":     "#451A1A",   # โทนตุ่นสำหรับพื้นหลังตารางแถว Deleted
    "del_fg":     "#FECACA",
}

# =========================================================================
# Static Minimal Background (ตัดแอนิเมชันแสงวูบวาบออกเพื่อลดความรำคาญตา)
# =========================================================================
class MinimalGridBackground(ctk.CTkCanvas):
    """Static clean dark grid."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.bind("<Configure>", self._on_configure)

    def _on_configure(self, event=None):
        if event and (event.width < 10 or event.height < 10):
            return
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()

        grid_color = "#1D2022" # เส้นตารางสีเทากลืนๆ ไปกับพื้น
        cell = 48
        for x in range(0, w + cell, cell):
            self.create_line(x, 0, x, h, fill=grid_color, width=1)
        for y in range(0, h + cell, cell):
            self.create_line(0, y, w, y, fill=grid_color, width=1)


# =========================================================================
# Minimal Spinner
# =========================================================================
class MinimalSpinner(ctk.CTkCanvas):
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
        
        self.create_arc(cx - 30, cy - 30, cx + 30, cy + 30,
                        start=self.angle, extent=120,
                        outline=C["primary"], width=4, style="arc")
        self.create_arc(cx - 30, cy - 30, cx + 30, cy + 30,
                        start=self.angle + 180, extent=120,
                        outline=C["border2"], width=4, style="arc")

        self.angle = (self.angle + 8) % 360
        self.after(20, self._tick)


# =========================================================================
# Clean Logo
# =========================================================================
class CleanLogo(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(anchor="w")

        bar_wrap = ctk.CTkFrame(wrap, fg_color="transparent")
        bar_wrap.pack(side="left", padx=(0, 12), pady=2, fill="y")
        ctk.CTkFrame(bar_wrap, width=4, fg_color=C["primary"],
                     corner_radius=2).pack(fill="y", expand=True)

        col = ctk.CTkFrame(wrap, fg_color="transparent")
        col.pack(side="left")

        row = ctk.CTkFrame(col, fg_color="transparent")
        row.pack(anchor="w")

        ctk.CTkLabel(row, text="EX",
                     font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
                     text_color=C["primary"]).pack(side="left")
        ctk.CTkLabel(row, text="TOR",
                     font=ctk.CTkFont(family="Consolas", size=28, weight="bold"),
                     text_color=C["text"]).pack(side="left")

        ctk.CTkLabel(col, text="DATA RECONCILER SYSTEM",
                     font=ctk.CTkFont(family="Consolas", size=9),
                     text_color=C["muted"]).pack(anchor="w")


# =========================================================================
# Helpers
# =========================================================================
def divider(parent, padx=16, pady=8):
    f = ctk.CTkFrame(parent, height=1, fg_color=C["border"], corner_radius=0)
    f.pack(fill="x", padx=padx, pady=pady)

def sec_label(parent, text, icon=""):
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=16, pady=(14, 4))
    if icon:
        ctk.CTkLabel(r, text="■ ",
                     font=ctk.CTkFont(family="Consolas", size=11),
                     text_color=C["muted"]).pack(side="left")
    ctk.CTkLabel(r, text=f" {text}",
                 font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                 text_color=C["text2"]).pack(side="left")

def glass_card(parent):
    return ctk.CTkFrame(parent,
                        fg_color=C["glass"],
                        corner_radius=8,
                        border_width=1,
                        border_color=C["border"])

def secondary_btn(parent, text, cmd, w=110, h=30):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color=C["input"], hover_color=C["border"],
        text_color=C["text2"],
        border_color=C["border2"], border_width=1,
        font=ctk.CTkFont(family="Consolas", size=11),
        width=w, height=h, corner_radius=6)

def ghost_btn(parent, text, cmd, w=110, h=36, tc=None):
    return ctk.CTkButton(
        parent, text=text, command=cmd,
        fg_color="transparent", hover_color=C["border"],
        text_color=tc or C["text2"],
        border_color=C["border2"], border_width=1,
        font=ctk.CTkFont(family="Consolas", size=10),
        width=w, height=h, corner_radius=6)

def status_pill(parent, text, bg, fg, border):
    f = ctk.CTkFrame(parent, fg_color=bg, corner_radius=6,
                     border_width=1, border_color=border)
    f.pack(side="left", padx=(0, 8))
    lbl = ctk.CTkLabel(f, text=f"  {text}  ",
                       font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                       text_color=fg)
    lbl.pack(padx=2, pady=5)
    return lbl


# =========================================================================
# Main App
# =========================================================================
class ExcelCompareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        try:
            self.iconbitmap("EXTORLOGO.ico")
        except Exception as e:
            print(f"Icon not found or invalid: {e}")
        # -------------------------------------------------------------
        self.withdraw()

        self.title("EXTOR  —  Data Reconciler V1.0.2")
        self.geometry("1500x900")
        self.minsize(1100, 700)
        self.configure(fg_color=C["root"])

        self.bg = MinimalGridBackground(self, bg=C["root"])
        self.bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.file1_path = ""
        self.file2_path = ""
        self.selected_columns = []
        self.result_df = None
        self.processor = DataReconciler()

        self._build()
        if windnd:
            windnd.hook_dropfiles(self, func=self._on_drop)

        self.show_splash_screen()

    # =====================================================================
    # SPLASH SCREEN
    # =====================================================================
    def show_splash_screen(self):
        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True)
        w, h = 500, 300
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        splash.geometry(f"{w}x{h}+{x}+{y}")
        splash.attributes('-topmost', True)

        outer = ctk.CTkFrame(splash, fg_color=C["sidebar"],
                             border_width=1, border_color=C["border"],
                             corner_radius=8)
        outer.pack(fill="both", expand=True)

        ctk.CTkLabel(outer, text="EXTOR",
                     font=ctk.CTkFont(family="Consolas", size=48, weight="bold"),
                     text_color=C["text"]).pack(pady=(70, 5))
        
        ctk.CTkLabel(outer, text="DATA RECONCILER SYSTEM",
                     font=ctk.CTkFont(family="Consolas", size=12),
                     text_color=C["muted"]).pack(pady=(0, 30))

        progress = ctk.CTkProgressBar(outer, width=300, height=4,
                                      fg_color=C["root"],
                                      progress_color=C["primary"],
                                      corner_radius=2)
        progress.pack(pady=(0, 10))
        progress.set(0)

        lbl = ctk.CTkLabel(outer, text="Loading UI components...",
                           text_color=C["muted"],
                           font=ctk.CTkFont(family="Consolas", size=10))
        lbl.pack()

        self.update_splash(splash, progress, lbl, 0)

    def update_splash(self, splash, progress, lbl, value):
        if value <= 100:
            progress.set(value / 100)
            if value == 50:
                lbl.configure(text="Applying Dark Slate Theme...")
            elif value == 80:
                lbl.configure(text="System Ready.")
            self.after(20, self.update_splash, splash, progress, lbl, value + 2)
        else:
            splash.destroy()
            self.deiconify()
            try:
                self.state('zoomed')
            except Exception:
                pass

    # =====================================================================
    # TTK Treeview style
    # =====================================================================
    def _tree_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("X.Treeview",
                    background=C["tree_bg"],
                    fieldbackground=C["tree_bg"],
                    foreground=C["tree_fg"],
                    rowheight=38,
                    borderwidth=0,
                    relief="flat",
                    font=("Consolas", 10))
        s.map("X.Treeview",
              background=[("selected", C["tree_sel"])],
              foreground=[("selected", C["tree_sfg"])])
        s.configure("X.Treeview.Heading",
                    background=C["tree_head"],
                    foreground=C["text2"],
                    relief="flat",
                    borderwidth=0,
                    font=("Consolas", 10, "bold"),
                    padding=10)
        s.map("X.Treeview.Heading",
              background=[("active", C["border"])],
              relief=[("active", "flat")])
        s.layout("X.Treeview", [
            ("X.Treeview.treearea", {"sticky": "nswe"})
        ])
        for orient in ("Vertical", "Horizontal"):
            s.configure(f"X.{orient}.TScrollbar",
                        background=C["root"], troughcolor=C["root"],
                        borderwidth=0, arrowsize=0, relief="flat")
            s.map(f"X.{orient}.TScrollbar",
                  background=[("active", C["border2"]), ("!active", C["border"])])

    # =====================================================================
    # BUILD UI
    # =====================================================================
    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        # ── SIDEBAR ──────────────────────────────────────────────────────
        sb_outer = ctk.CTkFrame(outer, width=300,
                                fg_color=C["sidebar"],
                                corner_radius=12,
                                border_width=1,
                                border_color=C["border"])
        sb_outer.pack(side="left", fill="y", padx=(0, 12))
        sb_outer.pack_propagate(False)

        sb = ctk.CTkScrollableFrame(sb_outer, fg_color="transparent",
                                    scrollbar_button_color=C["border"],
                                    scrollbar_button_hover_color=C["border2"])
        sb.pack(fill="both", expand=True)

        logo_wrap = ctk.CTkFrame(sb, fg_color="transparent")
        logo_wrap.pack(fill="x", padx=16, pady=(20, 10))
        CleanLogo(logo_wrap).pack(anchor="w")

        divider(sb)

        # ── File 1 ───────────────────────────────────────────────────────
        sec_label(sb, "BASE FILE  (ไฟล์หลัก)")
        c1 = glass_card(sb)
        c1.pack(fill="x", padx=12, pady=(2, 0))

        self.lbl_file1 = ctk.CTkLabel(
            c1, text="ลาก/วาง หรือ Browse ไฟล์",
            text_color=C["placeholder"],
            font=ctk.CTkFont(family="Consolas", size=10),
            wraplength=238, justify="left")
        self.lbl_file1.pack(anchor="w", padx=12, pady=(10, 4))

        r1 = ctk.CTkFrame(c1, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=(0, 10))
        secondary_btn(r1, "BROWSE", lambda: self.select_file(1),
                      w=70).pack(side="left", padx=(0, 6))
        
        self.sheet_var1 = ctk.StringVar(value="-- Sheet --")
        self.dropdown1 = ctk.CTkOptionMenu(
            r1, variable=self.sheet_var1,
            values=["-- Sheet --"], state="disabled",
            width=166, height=30, corner_radius=6,
            fg_color=C["input"], button_color=C["border"],
            button_hover_color=C["border2"],
            text_color=C["text2"],
            font=ctk.CTkFont(family="Consolas", size=10),
            dynamic_resizing=False)
        self.dropdown1.pack(side="left")

        # Swap button
        ctk.CTkButton(
            sb, text="⇅  SWAP FILES",
            command=self.swap_files,
            fg_color="transparent", hover_color=C["glass"],
            text_color=C["text2"], border_width=0,
            font=ctk.CTkFont(family="Consolas", size=10),
            width=266, height=24
        ).pack(padx=12, pady=8)

        # ── File 2 ───────────────────────────────────────────────────────
        sec_label(sb, "COMPARE FILE  (ไฟล์เทียบ)")
        c2 = glass_card(sb)
        c2.pack(fill="x", padx=12, pady=(2, 0))

        self.lbl_file2 = ctk.CTkLabel(
            c2, text="ลาก/วาง หรือ Browse ไฟล์",
            text_color=C["placeholder"],
            font=ctk.CTkFont(family="Consolas", size=10),
            wraplength=238, justify="left")
        self.lbl_file2.pack(anchor="w", padx=12, pady=(10, 4))

        r2 = ctk.CTkFrame(c2, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=(0, 10))
        secondary_btn(r2, "BROWSE", lambda: self.select_file(2),
                      w=70).pack(side="left", padx=(0, 6))
        
        self.sheet_var2 = ctk.StringVar(value="-- Sheet --")
        self.dropdown2 = ctk.CTkOptionMenu(
            r2, variable=self.sheet_var2,
            values=["-- Sheet --"], state="disabled",
            width=166, height=30, corner_radius=6,
            fg_color=C["input"], button_color=C["border"],
            button_hover_color=C["border2"],
            text_color=C["text2"],
            font=ctk.CTkFont(family="Consolas", size=10),
            dynamic_resizing=False)
        self.dropdown2.pack(side="left")

        divider(sb, pady=12)

        # ── Filters ──────────────────────────────────────────────────────
        sec_label(sb, "FILTERS  (ตัวกรอง)")

        ctk.CTkLabel(sb, text="ROW RANGE  (เช่น 1-100)",
                     font=ctk.CTkFont(family="Consolas", size=10),
                     text_color=C["muted"]).pack(anchor="w", padx=16, pady=(2, 2))

        self.entry_row = ctk.CTkEntry(
            sb, placeholder_text="leave blank = all rows",
            height=32, corner_radius=6,
            fg_color=C["input"], border_color=C["border"],
            border_width=1, text_color=C["text"],
            placeholder_text_color=C["placeholder"],
            font=ctk.CTkFont(family="Consolas", size=10))
        self.entry_row.pack(fill="x", padx=12, pady=(0, 8))

        ghost_btn(sb, "SELECT COLUMNS",
                  self.open_column_selector,
                  w=266, h=32).pack(padx=12)

        self.lbl_sel_cols = ctk.CTkLabel(
            sb, text="ALL COLUMNS  (default)",
            text_color=C["muted"],
            font=ctk.CTkFont(family="Consolas", size=10))
        self.lbl_sel_cols.pack(pady=(6, 0))

        divider(sb, pady=12)

        # ── Compare Button (UX Primary Action) ────────────────────────────
        self.btn_compare = ctk.CTkButton(
            sb,
            text="RUN COMPARISON",
            fg_color=C["primary"],
            hover_color=C["primary_h"],
            text_color=C["primary_fg"],
            border_width=0,
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            height=44, corner_radius=6,
            command=self.run_comparison_thread)
        self.btn_compare.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(sb,
                     text=f"EXTOR v{APP_VERSION} — @EXTOR_OFFICIAL",
                     font=ctk.CTkFont(family="Consolas", size=9),
                     text_color=C["muted"]).pack(pady=(0, 14))

        # ── MAIN CONTENT AREA ─────────────────────────────────────────────
        content = ctk.CTkFrame(outer,
                               fg_color=C["content"],
                               corner_radius=12,
                               border_width=1,
                               border_color=C["border"])
        content.pack(side="right", fill="both", expand=True)

        hdr = ctk.CTkFrame(content, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 0))

        info_col = ctk.CTkFrame(hdr, fg_color="transparent")
        info_col.pack(side="left", fill="y")

        self.lbl_compare_info = ctk.CTkLabel(
            info_col,
            text="[ SELECT FILES TO BEGIN RECONCILIATION ]",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=C["muted"])
        self.lbl_compare_info.pack(anchor="w")

        self.lbl_summary = ctk.CTkLabel(
            info_col,
            text="DASHBOARD READY",
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=C["text"])
        self.lbl_summary.pack(anchor="w", pady=(2, 0))

        self.btn_export = ctk.CTkButton(
            hdr, text="↓  EXPORT EXCEL",
            fg_color=C["glass"], hover_color=C["border"],
            text_color=C["text2"], border_color=C["border"],
            border_width=1,
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            width=140, height=36, corner_radius=6,
            command=self.export_result, state="disabled")
        self.btn_export.pack(side="right", anchor="center")

        ctk.CTkFrame(content, height=1, fg_color=C["border"],
                     corner_radius=0).pack(fill="x", padx=20, pady=(14, 0))

        # Status pills row (UX Muted Semantic Colors)
        self.pill_row = ctk.CTkFrame(content, fg_color="transparent")
        self.pill_row.pack(fill="x", padx=20, pady=(10, 4))
        self._pills = {}
        for key, txt, bg, fg, bd in [
            ("changed", "CHANGED", C["amber_dim"], C["amber_fg"], C["amber_dim"]),
            ("new",     "NEW",     C["green_dim"], C["green_fg"], C["green_dim"]),
            ("deleted", "DELETED", C["red_dim"],   C["red_fg"],   C["red_dim"]),
        ]:
            self._pills[key] = status_pill(self.pill_row, txt, bg, fg, bd)

        self._tree_style()

        # ── Tab view ──────────────────────────────────────────────────────
        self.tabview = ctk.CTkTabview(
            content,
            corner_radius=8,
            fg_color=C["content"],
            segmented_button_fg_color=C["glass"],
            segmented_button_selected_color=C["border2"],
            segmented_button_selected_hover_color=C["border"],
            segmented_button_unselected_color=C["glass"],
            segmented_button_unselected_hover_color=C["input"],
            text_color=C["text2"],
            border_width=0)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.tab_all     = self.tabview.add("  ALL  ")
        self.tab_changed = self.tabview.add("  CHANGED  ")
        self.tab_new     = self.tabview.add("  NEW  ")
        self.tab_del     = self.tabview.add("  DELETED  ")

        self.tree_all     = self._make_tree(self.tab_all)
        self.tree_changed = self._make_tree(self.tab_changed)
        self.tree_new     = self._make_tree(self.tab_new)
        self.tree_del     = self._make_tree(self.tab_del)

        self._build_loading()

    # =====================================================================
    # Loading overlay
    # =====================================================================
    def _build_loading(self):
        self.loading_frame = ctk.CTkFrame(
            self, fg_color=C["glass"],
            corner_radius=12,
            border_width=1, border_color=C["border"])
        self.spinner = MinimalSpinner(self.loading_frame,
                                      bg=C["glass"], width=80, height=80)
        self.spinner.pack(pady=(24, 6))
        ctk.CTkLabel(self.loading_frame, text="PROCESSING...",
                     font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                     text_color=C["text2"]).pack(pady=(0, 24), padx=40)

    def _make_tree(self, parent):
        wrap = ctk.CTkFrame(parent, fg_color=C["tree_bg"],
                            corner_radius=6, border_width=1, border_color=C["border"])
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
        tree.bind("<Double-1>",
                  lambda e, t=tree: self.show_row_details(e, t))

        tree.tag_configure("Changed",
                           background=C["chg_bg"], foreground=C["chg_fg"])
        tree.tag_configure("New",
                           background=C["new_bg"], foreground=C["new_fg"])
        tree.tag_configure("Deleted",
                           background=C["del_bg"], foreground=C["del_fg"])
        return tree

    # =====================================================================
    # Loading show/hide
    # =====================================================================
    def show_loading(self):
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.spinner.start()
        self.btn_compare.configure(state="disabled")

    def hide_loading(self):
        self.spinner.stop()
        self.loading_frame.place_forget()
        self.btn_compare.configure(state="normal")

    # =====================================================================
    # File operations
    # =====================================================================
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
        top.title("SELECT COLUMNS")
        top.geometry("460x580")
        top.configure(fg_color=C["root"])
        top.grab_set()

        ctk.CTkLabel(top, text="SELECT COLUMNS TO COMPARE",
                     font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                     text_color=C["text"]).pack(pady=(20, 10))

        scroll = ctk.CTkScrollableFrame(
            top, width=400, height=360,
            fg_color=C["glass"],
            corner_radius=8,
            border_width=1, border_color=C["border"])
        scroll.pack(padx=22, pady=6, fill="both", expand=True)

        checkboxes = {}
        for col in columns:
            if col in self.processor.key_cols:
                continue
            var = ctk.BooleanVar(
                value=(col in self.selected_columns)
                if self.selected_columns else True)
            cb = ctk.CTkCheckBox(
                scroll, text=col, variable=var,
                corner_radius=4,
                border_color=C["border2"],
                fg_color=C["primary"],
                hover_color=C["primary_h"],
                checkmark_color=C["primary_fg"],
                text_color=C["text2"],
                font=ctk.CTkFont(family="Consolas", size=11))
            cb.pack(anchor="w", pady=6, padx=14)
            checkboxes[col] = var

        def save():
            self.selected_columns = [
                c for c, v in checkboxes.items() if v.get()]
            self.lbl_sel_cols.configure(
                text=f"{len(self.selected_columns)} COLUMNS SELECTED",
                text_color=C["text"])
            top.destroy()

        br = ctk.CTkFrame(top, fg_color="transparent")
        br.pack(pady=12)
        ghost_btn(br, "SELECT ALL",
                  lambda: [v.set(True) for v in checkboxes.values()],
                  w=106, h=32).pack(side="left", padx=4)
        ghost_btn(br, "CLEAR ALL",
                  lambda: [v.set(False) for v in checkboxes.values()],
                  w=106, h=32).pack(side="left", padx=4)
        secondary_btn(br, "SAVE", save, w=106, h=32).pack(side="left", padx=4)

    # =====================================================================
    # Row detail inspector
    # =====================================================================
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
        win.title("ROW INSPECTOR")
        win.geometry("660x700")

        # --- เพิ่มบรรทัดนี้ครับ ---
        if os.path.exists("EXTORLOGO.ico"):
            win.iconbitmap("EXTORLOGO.ico")
        # ------------------------

        win.configure(fg_color=C["root"])
        win.grab_set()

        badge_map = {
            "Changed": (C["amber_dim"], C["amber_fg"], C["amber_dim"], "CHANGED"),
            "New":     (C["green_dim"], C["green_fg"], C["green_dim"], "NEW"),
            "Deleted": (C["red_dim"],   C["red_fg"],   C["red_dim"],   "DELETED"),
        }
        bg, fg, bd, txt = badge_map.get(status, (C["input"], C["text2"], C["border"], "NORMAL"))
        badge = ctk.CTkFrame(win, fg_color=bg, corner_radius=6,
                             border_width=1, border_color=bd)
        badge.pack(anchor="w", padx=22, pady=(20, 8))
        ctk.CTkLabel(badge, text=f"  {txt}  ",
                     font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                     text_color=fg).pack(padx=6, pady=5)

        scroll = ctk.CTkScrollableFrame(
            win, width=614,
            fg_color=C["glass"],
            corner_radius=8,
            border_width=1, border_color=C["border"])
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
                         font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                         text_color=tc).pack(anchor="w", pady=(12, 5), padx=6)
            tbl = ctk.CTkFrame(scroll, fg_color=hbg, corner_radius=6,
                               border_width=1, border_color=C["border"])
            tbl.pack(fill="x", padx=4, pady=(0, 10))
            tbl.columnconfigure(0, weight=1)
            tbl.columnconfigure(1, weight=3)
            for ci, ht in enumerate(["COLUMN", "VALUE"]):
                ctk.CTkLabel(tbl, text=f"  {ht}",
                             fg_color=hbg, text_color=C["text2"],
                             font=ctk.CTkFont(family="Consolas", size=10, weight="bold"),
                             anchor="w").grid(
                    row=0, column=ci, sticky="nsew",
                    padx=1, pady=(2, 1), ipady=7)
            for i, (col, val) in enumerate(data):
                rb = rbg1 if i % 2 == 0 else rbg2
                ctk.CTkLabel(tbl, text=f"  {col}",
                             fg_color=rb, text_color=C["muted"],
                             anchor="w",
                             font=ctk.CTkFont(family="Consolas", size=10)).grid(
                    row=i + 1, column=0, sticky="nsew",
                    padx=1, pady=1, ipady=7)
                ctk.CTkLabel(tbl, text=f"  {val}",
                             fg_color=rb, text_color=vfg,
                             anchor="w",
                             font=ctk.CTkFont(family="Consolas", size=10, weight="bold")).grid(
                    row=i + 1, column=1, sticky="nsew",
                    padx=1, pady=1, ipady=7)

        if changed_data:
            render("CHANGED FIELDS", C["amber_fg"],
                   changed_data, C["amber_dim"],
                   C["glass"], C["input"], C["amber_fg"])
        if normal_data:
            render("✓ NORMAL DATA", C["text2"],
                   normal_data, C["glass"],
                   C["input"], C["glass"], C["text"])
        if not changed_data and status in ["New", "Deleted"]:
            ctk.CTkLabel(scroll,
                         text="THIS ROW WAS FULLY ADDED OR REMOVED\nNO CELL-LEVEL CHANGES DETECTED",
                         text_color=C["muted"],
                         font=ctk.CTkFont(family="Consolas", size=12)).pack(pady=50)

    # =====================================================================
    # Drop files
    # =====================================================================
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
                messagebox.showwarning("TYPE ERROR", "Supports .xlsx and .csv only")
                return
            mx = self.winfo_pointerx() - self.winfo_rootx()
            self.load_file_to_box(fp, 1 if mx < 320 else 2)

    def load_file_to_box(self, filepath, box_num):
        name = os.path.basename(filepath)
        try:
            sheets = self.processor.get_sheet_names(filepath)
        except Exception as e:
            messagebox.showerror("ERROR", str(e))
            return
        disp = name[:34] + ("…" if len(name) > 34 else "")
        if box_num == 1:
            self.file1_path = filepath
            self.lbl_file1.configure(text=disp, text_color=C["text2"])
            self.dropdown1.configure(values=sheets, state="normal")
            self.sheet_var1.set(sheets[0])
        else:
            self.file2_path = filepath
            self.lbl_file2.configure(text=disp, text_color=C["text2"])
            self.dropdown2.configure(values=sheets, state="normal")
            self.sheet_var2.set(sheets[0])

    def select_file(self, fn):
        fp = filedialog.askopenfilename(
            filetypes=[("Excel & CSV", "*.xlsx *.csv")])
        if fp:
            self.load_file_to_box(fp, fn)

    # =====================================================================
    # Comparison logic
    # =====================================================================
    def run_comparison_thread(self):
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("WARNING",
                                   "กรุณาเลือกไฟล์ให้ครบทั้ง 2 ฝั่งครับ")
            return
        s1, s2 = self.sheet_var1.get(), self.sheet_var2.get()
        if "Sheet" in s1 or "Sheet" in s2:
            messagebox.showwarning("WARNING", "กรุณาเลือก Sheet ด้วยครับ")
            return
        f1 = os.path.basename(self.file1_path)
        f2 = os.path.basename(self.file2_path)
        self.lbl_compare_info.configure(
            text=f"{f1}   ⇄   {f2}",
            text_color=C["text2"])
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
            self.after(0, lambda: messagebox.showerror("ERROR", str(e)))

    def _update_ui(self):
        self.hide_loading()
        total = len(self.result_df)
        if total == 0:
            self.lbl_summary.configure(
                text="✓  DATA MATCH 100%",
                text_color=C["text2"])
            self.btn_export.configure(state="disabled")
            self._clear_trees()
            self._update_pills(0, 0, 0)
        else:
            vc = self.result_df["Status"].value_counts()
            chg = vc.get("Changed", 0)
            new = vc.get("New",     0)
            dlt = vc.get("Deleted", 0)
            self.lbl_summary.configure(
                text=f" {total} DIFFERENCES FOUND",
                text_color=C["text"])
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
        self._pills["changed"].configure(text=f"   {chg}  CHANGED  ")
        self._pills["new"].configure(text=f"   {new}  NEW  ")
        self._pills["deleted"].configure(text=f"   {dlt}  DELETED  ")

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

    # =====================================================================
    # Export
    # =====================================================================
    def export_result(self):
        if self.result_df is None or self.result_df.empty:
            return
        sp = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="EXTOR_Reconcile_Result.xlsx")
        if sp:
            self.btn_export.configure(state="disabled", text="EXPORTING...")
            threading.Thread(
                target=self._run_export_backend, args=(sp,),
                daemon=True).start()

    def _run_export_backend(self, save_path):
        try:
            self.processor.export_excel(save_path)
            self.after(0, lambda: self.btn_export.configure(state="normal", text="↓  EXPORT EXCEL"))
            self.after(0, lambda: messagebox.showinfo(
                "EXPORT COMPLETE",
                "Excel file exported successfully!\n"
                "Sheet: Transport_Report included ✓"))
        except Exception as e:
            self.after(0, lambda: self.btn_export.configure(state="normal", text="↓  EXPORT EXCEL"))
            self.after(0, lambda: messagebox.showerror(
                "EXPORT ERROR", f"Failed to save file:\n{str(e)}"))


if __name__ == "__main__":
    check_for_updates()
    app = ExcelCompareApp()
    app.mainloop()