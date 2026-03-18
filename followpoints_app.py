import time
import argparse

import json
import sys
import os
import math
import zipfile
import shutil
import tempfile
from typing import Tuple, Dict, List
from tkinter import filedialog, messagebox
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageChops
except ImportError as e:
    print(f"Import Error: {e}")
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageTk = None
    ImageChops = None
except Exception as e:
    print(f"MI PORBLEMO{e}")
    Image = None
import tkinter as tk
from tkinter import ttk

# I WAS DRUNK MAKING IT DONT COME TO ME IF ITS NOT GONNA WORK PROPERLY

def resourcepatch(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def l1(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def l2(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def Followpoint(length: int, color: Tuple[int, int, int], shadow_color: Tuple[int, int, int], glow_strength: float, shadow_strength: float, alpha: float, thickness: int, fade_strength: float, scale: float = 1.0) -> "Image.Image":
    
    
    length = int(length)
    thickness = int(thickness)
    glow_strength = float(glow_strength)
    shadow_strength = float(shadow_strength)
    alpha = float(alpha)
    fade_strength = float(fade_strength)
    scale = float(scale)
    
    out_w, out_h = 128, 50
    s = 4
    W = int(out_w * s * scale)
    H = int(out_h * s * scale)

    final_w, final_h = out_w, out_h

    bg_color = (color[0], color[1], color[2], 0)
    img_hr = Image.new("RGBA", (W, H), bg_color)
    
   
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    
    # Shodws
    shadow_base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_base)
    
    th = max(1, thickness)
    # Length scale
    ln = int(l2(length, th * 2, out_w))
    th_px = int(th * s * scale)
    ln_px = int(ln * s * scale)
    cx = W // 2
    cy = H // 2
    left_x = cx - ln_px // 2
    right_x = cx + ln_px // 2
    
    # render shadow
    if shadow_strength > 0:
        sd_rgba = (shadow_color[0], shadow_color[1], shadow_color[2], int(255 * alpha * shadow_strength))
        sd.rectangle((left_x, cy - th_px // 2, right_x, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        sd.ellipse((left_x - th_px // 2, cy - th_px // 2, left_x + th_px // 2, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        sd.ellipse((right_x - th_px // 2, cy - th_px // 2, right_x + th_px // 2, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        shadow_img = shadow_base.filter(ImageFilter.GaussianBlur(radius=int(th_px * 0.5)))
    else:
        shadow_img = None

    # draw followpoint
    main_rgba = (color[0], color[1], color[2], int(255 * alpha))
    d.rectangle((left_x, cy - th_px // 2, right_x, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    d.ellipse((left_x - th_px // 2, cy - th_px // 2, left_x + th_px // 2, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    d.ellipse((right_x - th_px // 2, cy - th_px // 2, right_x + th_px // 2, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    
    # edge fade
    if fade_strength > 0 and ImageChops:
        fade_mask = Image.new("L", (W, H), 255)
        fm_d = ImageDraw.Draw(fade_mask)
        full_ln_px = ln_px + th_px
        fade_px = int((full_ln_px // 2) * fade_strength)
        
        if fade_px > 0:
            for i in range(fade_px):
                op = int(255 * (i / fade_px))
                # left side
                x_left = (left_x - th_px // 2) + i
                fm_d.line([(x_left, 0), (x_left, H)], fill=op)
                # right side
                x_right = (right_x + th_px // 2) - i
                fm_d.line([(x_right, 0), (x_right, H)], fill=op)
            
            fm_d.rectangle((0, 0, left_x - th_px // 2, H), fill=0)
            fm_d.rectangle((right_x + th_px // 2, 0, W, H), fill=0)
            
            # apply fade to followpoint
            base.putalpha(ImageChops.multiply(base.getchannel('A'), fade_mask))
            # apply fade to shadow
            if shadow_img:
                shadow_img.putalpha(ImageChops.multiply(shadow_img.getchannel('A'), fade_mask))

    # composite followpoint and shadows
    if shadow_img:
        img_hr = Image.alpha_composite(img_hr, shadow_img)
    
    glow = base.filter(ImageFilter.GaussianBlur(radius=int(th_px * glow_strength)))
    img_hr = Image.alpha_composite(img_hr, glow)
    img_hr = Image.alpha_composite(img_hr, base)
    
    # resize
    img = img_hr.resize((final_w, final_h), Image.Resampling.LANCZOS)
    return img


class FollowpointsGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Simple(Banger) Followpoint Generator")
        self.root.configure(bg="#1e1e1e")
        
        # style of the program gui
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#cccccc", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9, "bold"))
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#cccccc")

        self.preview_size = 300
        self.frame_index = 0
        self.frame_count = 62
        self.last_tick = time.time()
        
        # animations
        self.is_playing = False
        self.animation_progress = 0.0 
        self.entities_total = 0 
        
        # assets
        self.skin_assets: Dict[str, "Image.Image"] = {}
        self.skin_tk_assets: Dict[str, "ImageTk.PhotoImage"] = {}
        self.combo_colors: List[Tuple[int, int, int]] = []
        
        # followp[oint color variables
        self.r_var = tk.IntVar(value=0)
        self.g_var = tk.IntVar(value=170)
        self.b_var = tk.IntVar(value=255)
        
        self.sr_var = tk.IntVar(value=0)
        self.sg_var = tk.IntVar(value=0)
        self.sb_var = tk.IntVar(value=0)
        
        self.size_var = tk.IntVar(value=12)
        self.length_var = tk.IntVar(value=96)
        self.glow_var = tk.DoubleVar(value=0.25)
        self.shadow_var = tk.DoubleVar(value=0.0)
        self.fade_var = tk.DoubleVar(value=0.0)
        self.line_opacity_var = tk.DoubleVar(value=1.0)
        self.alpha_min_var = tk.DoubleVar(value=0.0)
        self.alpha_max_var = tk.DoubleVar(value=1.0)
        self.scale_min_var = tk.DoubleVar(value=0.5)
        self.scale_max_var = tk.DoubleVar(value=1.0)
        
        # toggles for shadow and glow
        self.use_glow_var = tk.BooleanVar(value=True)
        self.use_shadow_var = tk.BooleanVar(value=True)
        
        self.circle_count_var = tk.IntVar(value=2)
        self.circle_dist_var = tk.IntVar(value=500)
        self.circle_size_var = tk.IntVar(value=128)
        
        self.dark_bg_var = tk.BooleanVar(value=True)
        self.osk_path = tk.StringVar(value="")
        self.skins_dir_var = tk.StringVar(value="")
        self.selected_skin_var = tk.StringVar(value="Select a skin...")
        self.last_export_dir = "" # Memory for custom export location
        self.show_circles_var = tk.BooleanVar(value=True)

        # icon
        try:
            icon_path = get_resource_path("icon.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(False, self.icon_photo)
        except:
            pass

        # main
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # leftside options
        self.sidebar_canvas = tk.Canvas(main_container, bg="#1e1e1e", highlightthickness=0, width=280)
        self.sidebar_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.sidebar_canvas.yview)
        self.sidebar = ttk.Frame(self.sidebar_canvas)
        
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar, anchor="nw", width=280)
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)
        
        self.sidebar_canvas.pack(side="left", fill="both", expand=False)
        self.sidebar_scrollbar.pack(side="left", fill="y")
        
        def update_scroll_region(event):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        self.sidebar.bind("<Configure>", update_scroll_region)
        
        # preview
        preview_frame = ttk.Frame(main_container)
        preview_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas = tk.Canvas(preview_frame, width=self.preview_size * 2, height=self.preview_size, 
                                bg="#111111", highlightthickness=1, highlightbackground="#333333")
        self.canvas.pack(fill="both", expand=True)
        # controls
        def create_control(parent, label, var, from_, to):
            frame = ttk.Frame(parent)
            frame.pack(fill="x", pady=4)
            
            top_row = ttk.Frame(frame)
            top_row.pack(fill="x")
            
            ttk.Label(top_row, text=label).pack(side="left")
            
            entry_var = tk.StringVar(value=str(var.get()))
            entry = tk.Entry(top_row, textvariable=entry_var, width=6, bg="#2d2d2d", fg="#ffffff", 
                             insertbackground="white", relief="flat", font=("Segoe UI", 9))
            entry.pack(side="right")
            
            scale = ttk.Scale(frame, from_=from_, to=to, variable=var)
            scale.pack(fill="x", pady=(2, 0))
            
            def on_var_change(*args):
                try:
                    val = var.get()
                    if isinstance(var, tk.IntVar):
                        entry_var.set(str(int(val)))
                    else:
                        entry_var.set(f"{val:.2f}")
                except tk.TclError: pass
            
            def on_entry_change(*args):
                try:
                    val = float(entry_var.get())
                    var.set(l2(val, from_, to))
                except ValueError: pass
            
            var.trace_add("write", on_var_change)
            entry_var.trace_add("write", on_entry_change)
            return frame

        def create_color_section(parent, title, r_var, g_var, b_var):
            group = ttk.LabelFrame(parent, text=f" {title} ", padding=10)
            group.pack(fill="x", pady=5)
            
            # hex color pallet
            hex_frame = ttk.Frame(group)
            hex_frame.pack(fill="x", pady=(0, 5))
            ttk.Label(hex_frame, text="Hex:").pack(side="left")
            hex_var = tk.StringVar()
            hex_entry = tk.Entry(hex_frame, textvariable=hex_var, width=10, bg="#2d2d2d", fg="#ffffff",
                                 insertbackground="white", relief="flat", font=("Segoe UI", 9))
            hex_entry.pack(side="right")
            
            def update_hex(*args):
                if getattr(self, '_updating_rgb', False): return
                try:
                    self._updating_hex = True
                    r, g, b = r_var.get(), g_var.get(), b_var.get()
                    hex_val = f"#{r:02x}{g:02x}{b:02x}"
                    if hex_var.get().lower() != hex_val.lower():
                        hex_var.set(hex_val.upper())
                except tk.TclError: pass
                finally: self._updating_hex = False
            
            def update_rgb(*args):
                if getattr(self, '_updating_hex', False): return
                h = hex_var.get().lstrip('#')
                if len(h) == 6:
                    try:
                        self._updating_rgb = True
                        r_var.set(int(h[0:2], 16))
                        g_var.set(int(h[2:4], 16))
                        b_var.set(int(h[4:6], 16))
                    except ValueError: pass
                    finally: self._updating_rgb = False

            r_var.trace_add("write", update_hex)
            g_var.trace_add("write", update_hex)
            b_var.trace_add("write", update_hex)
            hex_var.trace_add("write", update_rgb)
            update_hex()
            
            create_control(group, "Red", r_var, 0, 255)
            create_control(group, "Green", g_var, 0, 255)
            create_control(group, "Blue", b_var, 0, 255)
            return group

        # presets
        preset_group = ttk.LabelFrame(self.sidebar, text=" Presets ", padding=10)
        preset_group.pack(fill="x", pady=(0, 5))
        ttk.Button(preset_group, text="Load Config", command=self.load_preset).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(preset_group, text="Save Config", command=self.save_preset).pack(side="right", fill="x", expand=True, padx=(2, 0))

        # colors options
        create_color_section(self.sidebar, "Main Color", self.r_var, self.g_var, self.b_var)
        create_color_section(self.sidebar, "Shadow Color", self.sr_var, self.sg_var, self.sb_var)
        
        # customization
        geo_group = ttk.LabelFrame(self.sidebar, text=" Customization ", padding=10)
        geo_group.pack(fill="x", pady=5)
        create_control(geo_group, "Thickness", self.size_var, 1, 32)
        create_control(geo_group, "Length", self.length_var, 10, 128)
        
        create_control(geo_group, "Glow Intensity", self.glow_var, 0.0, 1.0)
        ttk.Checkbutton(geo_group, text="Enable Glow", variable=self.use_glow_var).pack(fill="x", pady=2)
        
        create_control(geo_group, "Shadow Opacity", self.shadow_var, 0.0, 1.0)
        ttk.Checkbutton(geo_group, text="Enable Shadow", variable=self.use_shadow_var).pack(fill="x", pady=2)
        
        create_control(geo_group, "Edge Fade", self.fade_var, 0.0, 1.0)

        # preview
        preview_group = ttk.LabelFrame(self.sidebar, text=" Preview Controls ", padding=10)
        preview_group.pack(fill="x", pady=5)
        create_control(preview_group, "Circle Distance", self.circle_dist_var, 100, 1000)
        create_control(preview_group, "Circle Count", self.circle_count_var, 2, 6)
        create_control(preview_group, "Circle Size", self.circle_size_var, 64, 256)
        ttk.Checkbutton(preview_group, text="Skin Preview", variable=self.show_circles_var).pack(fill="x", pady=2)

        # animations
        anim_group = ttk.LabelFrame(self.sidebar, text=" Animation ", padding=10)
        anim_group.pack(fill="x", pady=5)
        create_control(anim_group, "Base Opacity", self.line_opacity_var, 0.0, 1.0)
        create_control(anim_group, "Alpha Min", self.alpha_min_var, 0.0, 1.0)
        create_control(anim_group, "Alpha Max", self.alpha_max_var, 0.0, 1.0)

        # osk file
        osk_group = ttk.LabelFrame(self.sidebar, text=" Load From .osk File ", padding=10)
        osk_group.pack(fill="x", pady=5)
        
        ttk.Label(osk_group, text="Open .osk file:", font=("Segoe UI", 8, "bold")).pack(fill="x")
        ttk.Button(osk_group, text="Open .osk File", command=self.open_osk).pack(fill="x", pady=(2, 5))
        
        ttk.Separator(osk_group, orient="horizontal").pack(fill="x", pady=5)
        
        ttk.Label(osk_group, text="Open skin from skin folder", font=("Segoe UI", 8, "bold")).pack(fill="x")
        ttk.Button(osk_group, text="Select Skins Folder", command=self.select_skins_folder).pack(fill="x", pady=2)
        
        self.skin_dropdown = ttk.Combobox(osk_group, textvariable=self.selected_skin_var, state="readonly")
        self.skin_dropdown.pack(fill="x", pady=2)
        self.skin_dropdown.bind("<<ComboboxSelected>>", self.on_skin_selected)
        
        ttk.Label(osk_group, textvariable=self.osk_path, wraplength=250, font=("Segoe UI", 8), foreground="#888888").pack(fill="x", pady=(5, 0))

        # bottom controls
        actions_frame = ttk.Frame(self.sidebar)
        actions_frame.pack(fill="x", pady=10)
        
        self.play_btn = ttk.Button(actions_frame, text="▶ Play", command=self.toggle_animation)
        self.play_btn.pack(side="left", padx=2)
        
        ttk.Checkbutton(actions_frame, text="Dark BG", variable=self.dark_bg_var, command=self.update_bg).pack(side="left")
        ttk.Button(actions_frame, text="Export", command=self.on_export).pack(side="right")

        self.photo_cache = []
        
        # load configs
        self.load_config()
        
        self.root.after(16, self.tick)

    def get_config_path(self) -> str:
        # permissions
        app_data = os.getenv('APPDATA')
        if app_data:
            base_dir = os.path.join(app_data, "BangerFollowpointMaker")
        else:
            base_dir = os.path.join(os.path.expanduser("~"), ".BangerFollowpointMaker")
        
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, "config.json")

    def load_config(self) -> None:
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    skins_dir = config.get("skins_dir", "")
                    if skins_dir and os.path.exists(skins_dir):
                        self.skins_dir_var.set(skins_dir)
                        self._populate_skin_dropdown(skins_dir)
                    
                    self.last_export_dir = config.get("last_export_dir", "")
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save_config(self) -> None:
        config_path = self.get_config_path()
        config = {
            "skins_dir": self.skins_dir_var.get(),
            "last_export_dir": self.last_export_dir
        }
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def save_preset(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path: return
        
        data = {
            "main_color": (self.r_var.get(), self.g_var.get(), self.b_var.get()),
            "shadow_color": (self.sr_var.get(), self.sg_var.get(), self.sb_var.get()),
            "thickness": self.size_var.get(),
            "length": self.length_var.get(),
            "glow": self.glow_var.get(),
            "shadow": self.shadow_var.get(),
            "fade": self.fade_var.get(),
            "line_opacity": self.line_opacity_var.get(),
            "alpha_min": self.alpha_min_var.get(),
            "alpha_max": self.alpha_max_var.get(),
            "scale_min": self.scale_min_var.get(),
            "scale_max": self.scale_max_var.get(),
            "use_glow": self.use_glow_var.get(),
            "use_shadow": self.use_shadow_var.get(),
            "circle_count": self.circle_count_var.get(),
            "circle_dist": self.circle_dist_var.get(),
            "circle_size": self.circle_size_var.get(),
            "dark_bg": self.dark_bg_var.get(),
            "show_circles": self.show_circles_var.get()
        }
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Banger Followpoint Maker", f"Config saved to {os.path.basename(path)}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def load_preset(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path: return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            def set_val(var, key):
                if key in data: var.set(data[key])
            
            if "main_color" in data:
                r, g, b = data["main_color"]
                self.r_var.set(r); self.g_var.set(g); self.b_var.set(b)
            if "shadow_color" in data:
                r, g, b = data["shadow_color"]
                self.sr_var.set(r); self.sg_var.set(g); self.sb_var.set(b)
            
            set_val(self.size_var, "thickness")
            set_val(self.length_var, "length")
            set_val(self.glow_var, "glow")
            set_val(self.shadow_var, "shadow")
            set_val(self.fade_var, "fade")
            set_val(self.line_opacity_var, "line_opacity")
            set_val(self.alpha_min_var, "alpha_min")
            set_val(self.alpha_max_var, "alpha_max")
            set_val(self.scale_min_var, "scale_min")
            set_val(self.scale_max_var, "scale_max")
            set_val(self.use_glow_var, "use_glow")
            set_val(self.use_shadow_var, "use_shadow")
            set_val(self.circle_count_var, "circle_count")
            set_val(self.circle_dist_var, "circle_dist")
            set_val(self.circle_size_var, "circle_size")
            set_val(self.dark_bg_var, "dark_bg")
            set_val(self.show_circles_var, "show_circles")
            
            messagebox.showinfo("Banger Followpoint Maker", f"Config loaded from {os.path.basename(path)}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")


    def _populate_skin_dropdown(self, path: str) -> None:
        try:
            skins = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
            if skins:
                self.skin_dropdown['values'] = sorted(skins)
                self.selected_skin_var.set("Select a skin...")
                self.osk_path.set(path)
        except Exception as e:
            print(f"Failed to populate skins: {e}")

    def toggle_animation(self) -> None:
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_btn.config(text="⏸ Pause")
            self.animation_progress = 0.0 
        else:
            self.play_btn.config(text="▶ Play")

    def open_osk(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("osu! Skin", "*.osk"), ("Zip File", "*.zip")])
        if path:
            self.selected_skin_var.set("Select a skin...")
            self.skins_dir_var.set("")
            self.skin_dropdown['values'] = []
            self.osk_path.set(path)
            self.load_skin_assets(path)
            messagebox.showinfo("Banger Followpoint Maker", f"Linked to {os.path.basename(path)}. Preview assets loaded!")

    def select_skins_folder(self) -> None:
        path = filedialog.askdirectory(title="Select osu! Skins Folder")
        if path:
            self.skins_dir_var.set(path)
            self._populate_skin_dropdown(path)
            self.save_config()

    def on_skin_selected(self, event=None) -> None:
        skin_name = self.selected_skin_var.get()
        skins_dir = self.skins_dir_var.get()
        if skin_name and skins_dir:
            full_path = os.path.join(skins_dir, skin_name)
            self.osk_path.set(full_path)
            self.load_skin_assets(full_path)

    def load_skin_assets(self, path: str) -> None:
        if Image is None:
            messagebox.showwarning("Warning", "Pillow is not installed. Skin preview assets cannot be loaded.")
            return
        
        self.combo_colors = []
        self.skin_assets = {}
        
        try:
            if os.path.isfile(path) and (path.lower().endswith(".osk") or path.lower().endswith(".zip")):
                # Load from osk or zip file
                with zipfile.ZipFile(path, 'r') as zin:
                    # Parse skin.ini
                    if "skin.ini" in zin.namelist():
                        with zin.open("skin.ini") as f:
                            self._parse_skin_ini(f.read().decode('utf-8', errors='ignore'))
                    
                    # load Images
                    asset_names = ["hitcircle", "hitcircleoverlay"]
                    for i in range(10): asset_names.append(f"combo-{i}")
                    
                    for name in asset_names:
                        found_name = self._find_asset_in_zip(zin, name)
                        if found_name:
                            with zin.open(found_name) as f:
                                self.skin_assets[name] = Image.open(f).convert("RGBA")
                        elif "combo-" in name:
                            # Fallback to default if combo- is missing
                            def_name = name.replace("combo-", "default-")
                            found_name = self._find_asset_in_zip(zin, def_name)
                            if found_name:
                                with zin.open(found_name) as f:
                                    self.skin_assets[name] = Image.open(f).convert("RGBA")
            
            elif os.path.isdir(path):
                # load from Directory
                ini_path = os.path.join(path, "skin.ini")
                if os.path.exists(ini_path):
                    with open(ini_path, 'r', encoding='utf-8', errors='ignore') as f:
                        self._parse_skin_ini(f.read())
                
                # load Images
                asset_names = ["hitcircle", "hitcircleoverlay"]
                for i in range(10): asset_names.append(f"combo-{i}")
                
                for name in asset_names:
                    found_path = self._find_asset_in_dir(path, name)
                    if found_path:
                        self.skin_assets[name] = Image.open(found_path).convert("RGBA")
                    elif "combo-" in name:
                        # Fallback to default if combo- is missing
                        def_name = name.replace("combo-", "default-")
                        found_path = self._find_asset_in_dir(path, def_name)
                        if found_path:
                            self.skin_assets[name] = Image.open(found_path).convert("RGBA")
            
            # use pre defined colors if there is no skin.ini
            if not self.combo_colors:
                self.combo_colors = [(255, 255, 255)]
                
        except Exception as e:
            messagebox.showerror("Failed to load skin.ini")

    def _parse_skin_ini(self, content: str) -> None:
        import re
        for i in range(1, 9):
            match = re.search(f"Combo{i}\\s*:\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)", content, re.IGNORECASE)
            if match:
                self.combo_colors.append((int(match.group(1)), int(match.group(2)), int(match.group(3))))
# font assets
    def _find_asset_in_zip(self, zin, name) -> str:
        for info in zin.infolist():
            if f"{name}@2x.png" == info.filename.lower(): return info.filename
        for info in zin.infolist():
            if f"{name}.png" == info.filename.lower(): return info.filename
        
        if "combo-" in name:
            for info in zin.infolist():
                if f"assets/combo/{name}@2x.png" == info.filename.lower(): return info.filename
            for info in zin.infolist():
                if f"assets/combo/{name}.png" == info.filename.lower(): return info.filename
        return None

    def _find_asset_in_dir(self, directory, name) -> str:

        p2x = os.path.join(directory, f"{name}@2x.png")
        if os.path.exists(p2x): return p2x
        p = os.path.join(directory, f"{name}.png")
        if os.path.exists(p): return p
        
  
        if "combo-" in name:
            p2x_asset = os.path.join(directory, "assets", "combo", f"{name}@2x.png")
            if os.path.exists(p2x_asset): return p2x_asset
            p_asset = os.path.join(directory, "assets", "combo", f"{name}.png")
            if os.path.exists(p_asset): return p_asset
        return None

    def tick(self) -> None:
        if self.is_playing:

            self.animation_progress += 0.2
            if self.animation_progress >= self.entities_total + 2:
                self.animation_progress = 0.0
        
        self.frame_index = (self.frame_index + 1) % self.frame_count
        self.draw_preview()
        self.root.after(16, self.tick)

    def draw_preview(self) -> None:
        if Image is None: return
        self.canvas.delete("all")
        
        r, g, b = self.r_var.get(), self.g_var.get(), self.b_var.get()
        sr, sg, sb = self.sr_var.get(), self.sg_var.get(), self.sb_var.get()
        thickness = self.size_var.get()
        length = self.length_var.get()
        

        glow = self.glow_var.get() if self.use_glow_var.get() else 0.0
        shadow = self.shadow_var.get() if self.use_shadow_var.get() else 0.0
        
        fade = self.fade_var.get()
        line_opacity = l2(self.line_opacity_var.get(), 0.0, 1.0)
        amin, amax = self.alpha_min_var.get(), self.alpha_max_var.get()
        smin, smax = self.scale_min_var.get(), self.scale_max_var.get()
        
        num_circles = self.circle_count_var.get()
        circle_dist = self.circle_dist_var.get()
        circle_size = self.circle_size_var.get()
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w > 1 and h > 1:
            cx, cy = w // 2, h // 2
            
            # positions of the cirlces
            circle_positions = []
            if num_circles == 2:
                circle_positions = [(cx - circle_dist // 2, cy), (cx + circle_dist // 2, cy)]
            else:
                angle_step = 2 * math.pi / num_circles
                radius = circle_dist / (2 * math.sin(math.pi / num_circles))
                for i in range(num_circles):
                    angle = i * angle_step - math.pi / 2
                    circle_positions.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))

# followpoint render
            entities = []
            spacing = 32
            
            for i in range(len(circle_positions)):
                
                entities.append({
                    "type": "circle",
                    "pos": circle_positions[i],
                    "index": i
                })
                
        
                if i < len(circle_positions) - 1:
                    p1, p2 = circle_positions[i], circle_positions[i+1]
                    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    ux, uy = (dx / dist, dy / dist) if dist > 0 else (1.0, 0.0)
                    angle = math.degrees(math.atan2(dy, dx))
                    n = int(dist // spacing)
                    
                    for j in range(1, n):



                        frame_idx = (j - 1) % self.frame_count
                        
                        entities.append({
                            "type": "dot",
                            "pos": (p1[0] + ux * (j * spacing), p1[1] + uy * (j * spacing)),
                            "frame_idx": frame_idx,
                            "angle": angle
                        })
            
            self.entities_total = len(entities)
            self.photo_cache = []
            
            # draw followpoints
            current_progress = self.animation_progress if self.is_playing else float(len(entities))
            
            
            
            
            for idx, ent in enumerate(entities):
                if idx > current_progress:
                    break
                
                
                if ent["type"] == "dot":
                    t = ent["frame_idx"] / float(self.frame_count - 1)
                    tri = t * 2.0 if t <= 0.5 else 2.0 * (1.0 - t)
                    alpha = l1(amin, amax, tri) * line_opacity
                    scale = l1(smin, smax, tri)
                    
                    img = Followpoint(length, (r, g, b), (sr, sg, sb), glow, shadow, alpha, thickness, fade, scale)
                    if ent["angle"] != 0:
                        img = img.rotate(-ent["angle"], resample=Image.Resampling.BICUBIC, expand=True)
                    
                    ph = ImageTk.PhotoImage(img)
                    self.photo_cache.append(ph)
                    self.canvas.create_image(ent["pos"][0], ent["pos"][1], image=ph)
                    
                elif ent["type"] == "circle":
                    px, py = ent["pos"]
                    num = ent["index"] + 1
                    combo_color = self.combo_colors[ent["index"] % len(self.combo_colors)] if self.combo_colors else (255, 255, 255)
                    
                    if "hitcircle" in self.skin_assets:
                        hc_img = self.skin_assets["hitcircle"].copy()
                        tint_layer = Image.new("RGBA", hc_img.size, combo_color + (255,))
                        hc_tinted = ImageChops.multiply(hc_img, tint_layer)
                        hc_ph = ImageTk.PhotoImage(hc_tinted.resize((circle_size, circle_size), Image.Resampling.LANCZOS))
                        self.photo_cache.append(hc_ph)
                        self.canvas.create_image(px, py, image=hc_ph)
                        
                        if "hitcircleoverlay" in self.skin_assets:
                            hco_img = self.skin_assets["hitcircleoverlay"]
                            hco_ph = ImageTk.PhotoImage(hco_img.resize((circle_size, circle_size), Image.Resampling.LANCZOS))
                            self.photo_cache.append(hco_ph)
                            self.canvas.create_image(px, py, image=hco_ph)
                            
                        digit_name = f"default-{num % 10}"
                        if digit_name in self.skin_assets:
                            d_img = self.skin_assets[digit_name]
                            d_scale = circle_size / 160.0
                            d_ph = ImageTk.PhotoImage(d_img.resize((int(d_img.width * d_scale), int(d_img.height * d_scale)), Image.Resampling.LANCZOS))
                            self.photo_cache.append(d_ph)
                            self.canvas.create_image(px, py, image=d_ph)
                    else:
                        r_circle = circle_size // 2
                        hex_color = f"#{combo_color[0]:02x}{combo_color[1]:02x}{combo_color[2]:02x}"
                        self.canvas.create_oval(px-r_circle, py-r_circle, px+r_circle, py+r_circle, fill=hex_color, outline="#ffffff", width=4)
                        self.canvas.create_text(px, py, text=str(num), fill="#ffffff", font=("Segoe UI", int(circle_size * 0.4), "bold"))

    def on_export(self) -> None:
        r, g, b = self.r_var.get(), self.g_var.get(), self.b_var.get()
        sr, sg, sb = self.sr_var.get(), self.sg_var.get(), self.sb_var.get()
        thickness, length = self.size_var.get(), self.length_var.get()
        
        # Respect toggles
        glow = self.glow_var.get() if self.use_glow_var.get() else 0.0
        shadow = self.shadow_var.get() if self.use_shadow_var.get() else 0.0
        
        fade = self.fade_var.get()
        line_opacity = self.line_opacity_var.get()
        amin, amax = self.alpha_min_var.get(), self.alpha_max_var.get()
        smin, smax = self.scale_min_var.get(), self.scale_max_var.get()

        frames = {}
        # loading followpoints2 
        for i in range(62):
            t = i / 61.0
            tri = t * 2.0 if t <= 0.5 else 2.0 * (1.0 - t)
            alpha = l1(amin, amax, tri) * line_opacity
            scale = l1(smin, smax, tri)
            img = Followpoint(length, (r, g, b), (sr, sg, sb), glow, shadow, alpha, thickness, fade, scale)
            
            name = "followpoint.png" if i == 0 else f"followpoint-{i-1}.png"
            frames[name] = img

        osk = self.osk_path.get()
        export_to_skin = False
        
        if osk and os.path.exists(osk):
            skin_name = os.path.basename(osk)
            msg = f"Click yes to update current skin: {skin_name}\n\nfollowpoints, or click no to export to another directory."
            res = messagebox.askyesnocancel("Export Destination", msg)
            
            if res is None: 
                return
            elif res is True: 
                export_to_skin = True
            else: 
                export_to_skin = False
        
        if export_to_skin:
            if os.path.isfile(osk):
                try:
                    temp_dir = tempfile.mkdtemp()
                    temp_osk = osk + ".tmp"
                    with zipfile.ZipFile(osk, 'r') as zin:
                        with zipfile.ZipFile(temp_osk, 'w') as zout:
                            for item in zin.infolist():
                                if not item.filename.lower().startswith("followpoint"):
                                    zout.writestr(item, zin.read(item.filename))
                            for name, img in frames.items():
                                p = os.path.join(temp_dir, name)
                                img.save(p)
                                zout.write(p, name)
                    shutil.move(temp_osk, osk)
                    shutil.rmtree(temp_dir)
                    messagebox.showinfo("Banger Followpoint Maker", f"Exported to {os.path.basename(osk)}!")
                except PermissionError:
                    messagebox.showerror("Permission Error", f"Access Denied: Could not save to {osk}. Try running the program as Administrator or choose another location.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update .osk {e}")
            elif os.path.isdir(osk):
                #update Directory
                try:
                    for name, img in frames.items():
                        img.save(os.path.join(osk, name))
                    messagebox.showinfo(f"Exported to skin directory: {os.path.basename(osk)}!")
                except PermissionError:
                    messagebox.showerror("Could not save to {osk}. Try running the program as Administrator or choose another directory.")
                except Exception as e:
                    messagebox.showerror("Failed to export to skin directory: {e}")
        else:
            # export to another directory
            initial_dir = self.last_export_dir if self.last_export_dir and os.path.exists(self.last_export_dir) else os.getcwd()
            out_dir = filedialog.askdirectory(title="Select Export Directory", initialdir=initial_dir)
            if out_dir:
                try:
                    for name, img in frames.items():
                        img.save(os.path.join(out_dir, name))
                    
                    self.last_export_dir = out_dir
                    self.save_config() # Save the new last directory
                    messagebox.showinfo("Exported to: {out_dir}")
                except PermissionError:
                    messagebox.showerror("Permission Error")
                except Exception as e:
                    messagebox.showerror(f"Failed to export: {e}")


    def update_bg(self) -> None:
        self.canvas.configure(bg="#111111" if self.dark_bg_var.get() else "#ffffff")

def cli_export(args) -> None:
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    color = tuple(args.color)
    shadow_color = tuple(args.shadow_color)
    
    
    glow = args.glow
    shadow = args.shadow
    
    base_img = Followpoint(args.length, color, shadow_color, glow, shadow, args.alpha_min * args.line_opacity, args.size, args.fade)
    base_img.save(os.path.join(out_dir, "followpoint.png"))
    for i in range(61):
        t = i / 60.0
        tri = t * 2.0 if t <= 0.5 else 2.0 * (1.0 - t)
        alpha = l1(args.alpha_min, args.alpha_max, tri) * args.line_opacity
        img = Followpoint(args.length, color, shadow_color, glow, shadow, alpha, args.size, args.fade)
        img.save(os.path.join(out_dir, f"followpoint-{i}.png"))

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--export", action="store_true")
    p.add_argument("--out", type=str, default="output")
    p.add_argument("--size", type=int, default=12)
    p.add_argument("--length", type=int, default=96)
    p.add_argument("--color", type=int, nargs=3, default=[0, 170, 255])
    p.add_argument("--shadow-color", dest="shadow_color", type=int, nargs=3, default=[0, 0, 0])
    p.add_argument("--glow", type=float, default=0.25)
    p.add_argument("--shadow", type=float, default=0.0)
    p.add_argument("--fade", type=float, default=0.0)
    p.add_argument("--alpha-min", dest="alpha_min", type=float, default=0.0)
    p.add_argument("--alpha-max", dest="alpha_max", type=float, default=1.0)
    p.add_argument("--line-opacity", dest="line_opacity", type=float, default=1.0)
    return p

def main() -> None:
    parser = build_argparser()
    args = parser.parse_args()
    
    if Image is None:
        try:
            root = tk.Tk()
            root.withdraw()
            root.destroy()
        except:
            pass
        sys.exit(1)

    if args.export:
        if Image is None:
            sys.exit(1)
        cli_export(args)
        print(f"Exported to{os.path.abspath(args.out)}")
        return
    gui = FollowpointsGUI()
    gui.root.mainloop()
if __name__ == "__main__":
    main()