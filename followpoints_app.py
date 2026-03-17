import sys
import os
import math
import time
import argparse
from typing import Tuple
try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk, ImageChops
except Exception:
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageTk = None
    ImageChops = None
import tkinter as tk
from tkinter import ttk

# I WAS DRUNK MAKING IT DONT COME TO ME IF ITS NOT GONNA WORK PROPERLY

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def Followpoint(length: int, color: Tuple[int, int, int], shadow_color: Tuple[int, int, int], glow_strength: float, shadow_strength: float, alpha: float, thickness: int, fade_strength: float) -> Image.Image:
    out_w, out_h = 128, 50
    s = 4
    W = out_w * s
    H = out_h * s
    bg_color = (color[0], color[1], color[2], 0)
    img_hr = Image.new("RGBA", (W, H), bg_color)
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    shadow_base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_base)
    th = max(1, thickness)
    ln = int(clamp(length, th * 2, out_w - 4))
    th_px = th * s
    ln_px = ln * s
    cx = W // 2
    cy = H // 2
    left_x = cx - ln_px // 2
    right_x = cx + ln_px // 2
    if shadow_strength > 0:
        sd_rgba = (shadow_color[0], shadow_color[1], shadow_color[2], int(255 * alpha * shadow_strength))
        sd.rectangle((left_x, cy - th_px // 2, right_x, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        sd.ellipse((left_x - th_px // 2, cy - th_px // 2, left_x + th_px // 2, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        sd.ellipse((right_x - th_px // 2, cy - th_px // 2, right_x + th_px // 2, cy + th_px // 2), fill=sd_rgba, outline=sd_rgba)
        shadow_img = shadow_base.filter(ImageFilter.GaussianBlur(radius=int(th_px * 0.5)))
    else:
        shadow_img = None
    main_rgba = (color[0], color[1], color[2], int(255 * alpha))
    d.rectangle((left_x, cy - th_px // 2, right_x, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    d.ellipse((left_x - th_px // 2, cy - th_px // 2, left_x + th_px // 2, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    d.ellipse((right_x - th_px // 2, cy - th_px // 2, right_x + th_px // 2, cy + th_px // 2), fill=main_rgba, outline=main_rgba)
    if fade_strength > 0 and ImageChops:
        fade_mask = Image.new("L", (W, H), 255)
        fm_d = ImageDraw.Draw(fade_mask)
        full_ln_px = ln_px + th_px
        fade_px = int((full_ln_px // 2) * fade_strength)
        
        if fade_px > 0:
            for i in range(fade_px):
                op = int(255 * (i / fade_px))
                x_left = (left_x - th_px // 2) + i
                fm_d.line([(x_left, 0), (x_left, H)], fill=op)
                x_right = (right_x + th_px // 2) - i
                fm_d.line([(x_right, 0), (x_right, H)], fill=op)
            fm_d.rectangle((0, 0, left_x - th_px // 2, H), fill=0)
            fm_d.rectangle((right_x + th_px // 2, 0, W, H), fill=0)
            
            base.putalpha(ImageChops.multiply(base.getchannel('A'), fade_mask))
            if shadow_img:
                shadow_img.putalpha(ImageChops.multiply(shadow_img.getchannel('A'), fade_mask))
    if shadow_img:
        img_hr = Image.alpha_composite(img_hr, shadow_img)
    glow = base.filter(ImageFilter.GaussianBlur(radius=int(th_px * glow_strength)))
    img_hr = Image.alpha_composite(img_hr, glow)
    img_hr = Image.alpha_composite(img_hr, base)
    img = img_hr.resize((out_w, out_h), Image.Resampling.LANCZOS)
    return img
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FollowpointsGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Banger Followpoint Maker")
        self.root.configure(bg="#1e1e1e")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#cccccc", font=("Segoe UI", 9))
        style.configure("TButton", font=("Segoe UI", 9, "bold"))
        style.configure("TCheckbutton", background="#1e1e1e", foreground="#cccccc")

        self.preview_size = 300
        self.frame_index = 0
        self.frame_count = 60
        self.last_tick = time.time()
        
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
        self.speed_var = tk.DoubleVar(value=1.0)
        self.alpha_min_var = tk.DoubleVar(value=0.0)
        self.alpha_max_var = tk.DoubleVar(value=1.0)
        self.dark_bg_var = tk.BooleanVar(value=True)
        try:
            icon_path = get_resource_path("icon.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(False, self.icon_photo)
        except:
            pass
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        

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
        
        preview_frame = ttk.Frame(main_container)
        preview_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas = tk.Canvas(preview_frame, width=self.preview_size * 2, height=self.preview_size, 
                                bg="#111111", highlightthickness=1, highlightbackground="#333333")
        self.canvas.pack(fill="both", expand=True)
        
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
                    var.set(clamp(val, from_, to))
                except ValueError: pass
            
            var.trace_add("write", on_var_change)
            entry_var.trace_add("write", on_entry_change)
            return frame

        def create_color_section(parent, title, r_var, g_var, b_var):
            group = ttk.LabelFrame(parent, text=f" {title} ", padding=10)
            group.pack(fill="x", pady=5)
            
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
        create_color_section(self.sidebar, "", self.r_var, self.g_var, self.b_var)
        create_color_section(self.sidebar, "", self.sr_var, self.sg_var, self.sb_var)
        geo_group = ttk.LabelFrame(self.sidebar, text="", padding=10)
        geo_group.pack(fill="x", pady=5)
        create_control(geo_group, "Thickness", self.size_var, 1, 32)
        create_control(geo_group, "Length", self.length_var, 10, 128)
        create_control(geo_group, "Glow", self.glow_var, 0.0, 1.0)
        create_control(geo_group, "Shadow Opacity", self.shadow_var, 0.0, 1.0)
        create_control(geo_group, "Edge Fade", self.fade_var, 0.0, 1.0)

        anim_group = ttk.LabelFrame(self.sidebar, text="", padding=10)
        anim_group.pack(fill="x", pady=5)
        create_control(anim_group, "Base Opacity", self.line_opacity_var, 0.0, 1.0)
        create_control(anim_group, "Speed", self.speed_var, 0.1, 5.0)
        create_control(anim_group, "Alpha Min", self.alpha_min_var, 0.0, 1.0)
        create_control(anim_group, "Alpha Max", self.alpha_max_var, 0.0, 1.0)

        actions_frame = ttk.Frame(self.sidebar)
        actions_frame.pack(fill="x", pady=10)
        
        ttk.Checkbutton(actions_frame, text="Dark BG", variable=self.dark_bg_var, command=self.update_bg).pack(side="left")
        ttk.Button(actions_frame, text="Export", command=self.on_export).pack(side="right")

        self.photo_cache = []
        self.root.after(16, self.tick)

    def tick(self) -> None:
        self.frame_index = (self.frame_index + max(1, int(self.speed_var.get() * 2))) % self.frame_count
        self.draw_preview()
        self.root.after(16, self.tick)

    def draw_preview(self) -> None:
        if Image is None: return
        self.canvas.delete("all")
        
        r, g, b = self.r_var.get(), self.g_var.get(), self.b_var.get()
        sr, sg, sb = self.sr_var.get(), self.sg_var.get(), self.sb_var.get()
        thickness = self.size_var.get()
        length = self.length_var.get()
        glow = self.glow_var.get()
        shadow = self.shadow_var.get()
        fade = self.fade_var.get()
        line_opacity = clamp(self.line_opacity_var.get(), 0.0, 1.0)
        amin, amax = self.alpha_min_var.get(), self.alpha_max_var.get()
        
        phase = self.frame_index / float(self.frame_count)
        tri = phase * 2.0 if phase <= 0.5 else 2.0 * (1.0 - phase)
        alpha = lerp(amin, amax, tri) * line_opacity
        
        img = Followpoint(length, (r, g, b), (sr, sg, sb), glow, shadow, alpha, thickness, fade)
        ph = ImageTk.PhotoImage(img.resize((128 * 4, 50 * 4), Image.Resampling.LANCZOS))
        self.photo_cache = [ph]
        
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w > 1 and h > 1:
            self.canvas.create_image(w//2, h//2, image=ph)

    def on_export(self) -> None:
        out_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(out_dir, exist_ok=True)
        
        r, g, b = self.r_var.get(), self.g_var.get(), self.b_var.get()
        sr, sg, sb = self.sr_var.get(), self.sg_var.get(), self.sb_var.get()
        thickness, length = self.size_var.get(), self.length_var.get()
        glow, shadow = self.glow_var.get(), self.shadow_var.get()
        fade = self.fade_var.get()
        line_opacity = self.line_opacity_var.get()
        amin, amax = self.alpha_min_var.get(), self.alpha_max_var.get()

        base_img = Followpoint(length, (r, g, b), (sr, sg, sb), glow, shadow, amin * line_opacity, thickness, fade)
        base_img.save(os.path.join(out_dir, "followpoint.png"))
        
        for i in range(61):
            t = i / 60.0
            tri = t * 2.0 if t <= 0.5 else 2.0 * (1.0 - t)
            alpha = lerp(amin, amax, tri) * line_opacity
            img = Followpoint(length, (r, g, b), (sr, sg, sb), glow, shadow, alpha, thickness, fade)
            img.save(os.path.join(out_dir, f"followpoint-{i}.png"))

    def update_bg(self) -> None:
        self.canvas.configure(bg="#111111" if self.dark_bg_var.get() else "#ffffff")

def cli_export(args) -> None:
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)
    color = tuple(args.color)
    shadow_color = tuple(args.shadow_color)
    
    base_img = Followpoint(args.length, color, shadow_color, args.glow, args.shadow, args.alpha_min * args.line_opacity, args.size, args.fade)
    base_img.save(os.path.join(out_dir, "followpoint.png"))
    
    for i in range(61):
        t = i / 60.0
        tri = t * 2.0 if t <= 0.5 else 2.0 * (1.0 - t)
        alpha = lerp(args.alpha_min, args.alpha_max, tri) * args.line_opacity
        img = Followpoint(args.length, color, shadow_color, args.glow, args.shadow, alpha, args.size, args.fade)
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
    if args.export:
        if Image is None:
            print("Install pillow you deadass")
            sys.exit(1)
        cli_export(args)
        print(f"Exported to{os.path.abspath(args.out)}")
        return
    gui = FollowpointsGUI()
    gui.root.mainloop()

if __name__ == "__main__":
    main()
