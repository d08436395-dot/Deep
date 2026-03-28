import customtkinter as ctk
ctk.CTk._windows_set_titlebar_color = lambda *a, **k: None
import os, json, sqlite3, subprocess, tkinter as tk, random, math, time, sys, requests
from datetime import datetime
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

# --- КОНФИГУРАЦИЯ ОБНОВЛЕНИЙ ---
CURRENT_VERSION = "1.0.7"
GITHUB_USER = "d08436395-dot"
GITHUB_REPO = "Deep"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"
LAUNCHER_URL = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/raw/main/Kodik_Ultra.exe"
# ------------------------------

try:
    import pywinstyles
except ImportError:
    pywinstyles = None

DB_FILE = os.path.join(os.path.expanduser("~"), "launcher_system.db")
DATA_FILE = os.path.join(os.path.expanduser("~"), "apps_data.json")
LOG_FILE = os.path.join(os.path.expanduser("~"), "launcher_logs.txt")

ctk.set_appearance_mode("dark")
ACCENT_RED = "#FF2A2A"
DARK_BG = "#020203"
PLAY_GREEN = "#00C853"
TEXT_GRAY = "#888888"
COIN_GOLD = "#FFD700"
STATTRAK_ORANGE = "#CF6A32"

AVATAR_FRAMES = [
    {"id": "none", "name": "Стандарт", "color": "#FF2A2A", "width": 2, "effect": "static", "label": "", "price": 0, "type": "basic"},
    {"id": "neon_blue", "name": "Neon Blue", "color": "#00F2FF", "width": 3, "effect": "pulse", "label": "NEON", "price": 100, "type": "basic"},
    {"id": "minecraft", "name": "Minecraft", "color": "#55FF55", "width": 4, "effect": "pixel", "label": "CRAFT", "price": 150, "type": "basic"},
    {"id": "vip", "name": "VIP Gold", "color": "#FFD700", "width": 5, "effect": "3d_shine", "label": "VIP", "price": 450, "type": "basic"},
    {"id": "st_cyber", "name": "ST Cyber", "color": "#00FF00", "width": 4, "effect": "matrix", "label": "ST", "price": 300, "type": "stattrak"},
    {"id": "st_lava", "name": "ST Lava", "color": "#FF4500", "width": 5, "effect": "fire", "label": "ST", "price": 350, "type": "stattrak"},
    {"id": "st_ice", "name": "ST Ice", "color": "#A5F2F3", "width": 3, "effect": "blink", "label": "ST", "price": 400, "type": "stattrak"},
    {"id": "st_void", "name": "ST Void", "color": "#4B0082", "width": 4, "effect": "rotate", "label": "ST", "price": 450, "type": "stattrak"},
    {"id": "st_toxic", "name": "ST Toxic", "color": "#ADFF2F", "width": 3, "effect": "pulse", "label": "ST", "price": 500, "type": "stattrak"},
    {"id": "st_blood", "name": "ST Blood", "color": "#8B0000", "width": 5, "effect": "glow", "label": "ST", "price": 550, "type": "stattrak"},
    {"id": "st_royal", "name": "ST Royal", "color": "#4169E1", "width": 4, "effect": "3d_shine", "label": "ST", "price": 600, "type": "stattrak"},
    {"id": "st_sun", "name": "ST Sun", "color": "#FFA500", "width": 4, "effect": "rainbow", "label": "ST", "price": 650, "type": "stattrak"},
    {"id": "st_phantom", "name": "ST Ghost", "color": "#708090", "width": 2, "effect": "blink", "label": "ST", "price": 700, "type": "stattrak"},
    {"id": "st_ultra", "name": "ST Ultra", "color": "#FFFFFF", "width": 6, "effect": "rainbow", "label": "ST", "price": 750, "type": "stattrak"},
    {"id": "6d_kitty", "name": "Hello Kitty", "color": "#FFB6C1", "width": 6, "effect": "6d_kitty", "label": "KAWAII", "price": -1, "type": "6d"},
    {"id": "6d_gold", "name": "Golden Emperor", "color": "#FFD700", "width": 8, "effect": "6d_gold", "label": "EMPEROR", "price": -1, "type": "6d"},
    {"id": "6d_glitch", "name": "Cyber Glitch", "color": "#00FFFF", "width": 5, "effect": "6d_glitch", "label": "HACKER", "price": -1, "type": "6d"},
    {"id": "6d_gothic", "name": "Dark Gothic", "color": "#FFFFFF", "width": 4, "effect": "6d_gothic", "label": "GOTHIC", "price": -1, "type": "6d"},
    {"id": "6d_techno", "name": "6D TECHNO", "color": "#A020F0", "width": 8, "effect": "6d_cyber", "label": "ULTRA", "price": -1, "type": "6d"},
    {"id": "6d_nature", "name": "6D NATURE", "color": "#2E8B57", "width": 8, "effect": "6d_floral", "label": "ELITE", "price": -1, "type": "6d"}
]

class AdmHelper(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.is_running = True
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.init_db()
        self.title("DEEPTECH ULTRA")
        self.geometry("1200x800")
        self.configure(fg_color=DARK_BG)
        self.current_user = None
        self.user_level = 1
        self.user_coins = 0
        self.user_time = 0
        self.owned_frames = ["none"]
        self.current_frame = "none"
        self.apps = self.load_data()
        self.overlay = None
        self._frame_anim_step = 0
        self._fire_particles = []
        self.setup_background()
        self.show_login_screen()
        self.start_coin_farm()
        self.check_for_updates()

    def check_for_updates(self):
        try:
            res = requests.get(VERSION_URL, timeout=5)
            if res.status_code == 200 and res.json().get("version") > CURRENT_VERSION: self.perform_update()
        except: pass

    def perform_update(self):
        try:
            res = requests.get(LAUNCHER_URL, stream=True)
            if res.status_code == 200:
                cur = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0])
                new = cur + ".new"
                with open(new, 'wb') as f:
                    for c in res.iter_content(8192): f.write(c)
                bat = os.path.join(os.path.dirname(cur), "upd.bat")
                with open(bat, "w") as f: f.write(f"@echo off\ntimeout /t 3\ntaskkill /f /im \"{os.path.basename(cur)}\"\ndel \"{cur}\"\nmove \"{new}\" \"{cur}\"\nstart \"\" \"{cur}\"\ndel \"%~f0\"")
                subprocess.Popen(["cmd", "/c", bat], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.destroy(); sys.exit()
        except: pass

    def init_db(self):
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, level INTEGER, avatar TEXT, frame TEXT, coins INTEGER DEFAULT 0, owned_frames TEXT DEFAULT 'none', total_time INTEGER DEFAULT 0, bg_settings TEXT)")
        cols = [c[1] for c in cur.execute("PRAGMA table_info(users)").fetchall()]
        if "total_time" not in cols: cur.execute("ALTER TABLE users ADD COLUMN total_time INTEGER DEFAULT 0")
        if "bg_settings" not in cols: cur.execute("ALTER TABLE users ADD COLUMN bg_settings TEXT")
        cur.execute("SELECT * FROM users WHERE username=?", ("Dima_Ovenov",))
        if not cur.fetchone(): cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", ("Dima_Ovenov", "barnikovds", 5, None, "6d_gold", 5000, "none,6d_kitty,6d_gold,6d_glitch,6d_gothic,6d_techno,6d_nature", 0, None))
        conn.commit(); conn.close()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.apps, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.notify(f"Ошибка сохранения: {e}")

    def notify(self, text, color=ACCENT_RED):
        # Создаем стильное уведомление внутри окна
        notif = ctk.CTkFrame(self, fg_color="#0D0D0D", corner_radius=10, border_width=1, border_color=color)
        notif.place(relx=0.5, rely=0.05, anchor="n")
        
        # Иконка или текст
        ctk.CTkLabel(notif, text=text, font=("Arial Bold", 14), text_color="white").pack(padx=20, pady=10)
        
        # Автоматическое удаление через 3 секунды
        self.after(3000, notif.destroy)

    def log_event(self, event, level="INFO"):
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {event}\n")
        except:
            pass

    def setup_background(self):
        self.bg_canvas = tk.Canvas(self, bg="#010101", highlightthickness=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.particles = []
        self.mouse_x, self.mouse_y = -1000, -1000
        for _ in range(80):
            x, y = random.randint(0, 1200), random.randint(0, 800)
            r = random.randint(1, 3)
            p_id = self.bg_canvas.create_oval(x-r, y-r, x+r, y+r, fill='#220000', outline='')
            self.particles.append({'id': p_id, 'x': x, 'y': y, 'vx': random.uniform(-0.7, 0.7), 'vy': random.uniform(-0.7, 0.7), 'r': r, 'base_fill': '#220000'})
        self.bind("<Motion>", lambda e: setattr(self, 'mouse_x', e.x) or setattr(self, 'mouse_y', e.y))
        self.animate_particles()

    def animate_particles(self):
        if not self.is_running or not hasattr(self, 'bg_canvas') or not self.bg_canvas.winfo_exists(): return
        try:
            w, h = self.winfo_width(), self.winfo_height()
            if w < 100: w, h = 1200, 800
            for p in self.particles:
                p['x'] = (p['x'] + p['vx']) % w; p['y'] = (p['y'] + p['vy']) % h
                dx, dy = p['x'] - self.mouse_x, p['y'] - self.mouse_y
                dist = (dx**2 + dy**2)**0.5
                if dist < 120:
                    force = (120 - dist) / 120; p['x'] += dx * force * 0.1; p['y'] += dy * force * 0.1
                    self.bg_canvas.itemconfig(p['id'], fill='#FF0000')
                else: self.bg_canvas.itemconfig(p['id'], fill=p['base_fill'])
                self.bg_canvas.coords(p['id'], p['x']-p['r'], p['y']-p['r'], p['x']+p['r'], p['y']+p['r'])
            self.after(25, self.animate_particles)
        except: pass

    def start_coin_farm(self):
        def farm():
            if self.is_running and self.current_user:
                self.user_coins += 1
                self.user_time += 1
                if hasattr(self, 'coin_label'):
                    self.coin_label.configure(text=f" {self.user_coins}")
                if self.user_time % 60 == 0: # Сохраняем каждую минуту
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
                    cur.execute("UPDATE users SET coins=?, total_time=? WHERE username=?", (self.user_coins, self.user_time, self.current_user))
                    conn.commit(); conn.close()
            self.after(60000, farm)
        self.after(60000, farm)

    def show_overlay(self, title, content_func):
        if self.overlay: self.overlay.destroy()
        self.overlay = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        dialog = ctk.CTkFrame(self.overlay, fg_color="#0A0A0A", corner_radius=20, border_width=1, border_color=ACCENT_RED, width=600, height=500)
        dialog.place(relx=0.5, rely=0.5, anchor="center"); dialog.pack_propagate(False)
        ctk.CTkLabel(dialog, text=title, font=("Arial Black", 18), text_color=ACCENT_RED).pack(pady=20)
        body = ctk.CTkFrame(dialog, fg_color="transparent"); body.pack(fill="both", expand=True, padx=20)
        content_func(body, dialog)

    def show_reg_screen(self):
        for w in self.winfo_children():
            if w != getattr(self, 'bg_canvas', None): w.destroy()
        frame = ctk.CTkFrame(self, width=400, height=450, fg_color="#0A0A0A", corner_radius=20, border_width=1, border_color="#222222")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="РЕГИСТРАЦИЯ", font=("Arial Black", 32), text_color=ACCENT_RED).pack(pady=40)
        u_e = ctk.CTkEntry(frame, placeholder_text="Логин", width=280, height=45); u_e.pack(pady=10)
        p_e = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*", width=280, height=45); p_e.pack(pady=10)
        def do_reg():
            u, p = u_e.get(), p_e.get()
            if u and p:
                conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO users (username, password, level, frame, coins, owned_frames, total_time) VALUES (?, ?, ?, ?, ?, ?, ?)", (u, p, 1, "none", 0, "none", 0))
                    conn.commit(); self.notify("Аккаунт создан!", PLAY_GREEN); self.show_login_screen()
                except: self.notify("Логин занят"); conn.close()
            else: self.notify("Заполните поля")
        ctk.CTkButton(frame, text="ЗАРЕГИСТРИРОВАТЬСЯ", fg_color=ACCENT_RED, width=280, height=50, command=do_reg).pack(pady=20)
        ctk.CTkButton(frame, text="Назад", fg_color="transparent", command=self.show_login_screen).pack()

    def setup_ui(self):
        for w in self.winfo_children():
            if w != getattr(self, 'bg_canvas', None): w.destroy()
        if pywinstyles:
            try:
                pywinstyles.apply_style(self, "mica"); pywinstyles.set_opacity(self, color="#000001", bg_blur=True)
                self.wm_attributes("-transparentcolor", "#000001"); self.configure(fg_color="#000001")
            except: pass
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        sidebar = ctk.CTkFrame(self, width=260, fg_color="#0a0a0a", corner_radius=0, border_width=1, border_color="#222222")
        sidebar.grid(row=0, column=0, sticky="nsew")
        ava_f = ctk.CTkFrame(sidebar, fg_color="transparent"); ava_f.pack(pady=(40, 10))
        self.ava_canvas = tk.Canvas(ava_f, width=140, height=140, bg="#0a0a0a", highlightthickness=0); self.ava_canvas.pack()
        
        def draw_complex_frame(canvas, x1, y1, x2, y2, f_data, step=0):
            canvas.delete("frame")
            cx, cy = (x1+x2)/2, (y1+y2)/2
            color = f_data["color"]; width = f_data["width"]; effect = f_data["effect"]
            
            if effect == "6d_kitty":
                canvas.create_oval(x1, y1, x2, y2, outline="#FFB6C1", width=width, tags="frame")
            elif effect == "6d_gold":
                for i in range(6): canvas.create_rectangle(x1-i, y1-i, x2+i, y2+i, outline="#443300", width=1, tags="frame")
                canvas.create_rectangle(x1, y1, x2, y2, outline="#FFD700", width=width, tags="frame")
                s = 25
                canvas.create_polygon(x1, y1, x1+s, y1, x1, y1+s, fill="#FFD700", tags="frame")
                canvas.create_polygon(x2, y1, x2-s, y1, x2, y1+s, fill="#FFD700", tags="frame")
                canvas.create_polygon(x1, y2, x1+s, y2, x1, y2-s, fill="#FFD700", tags="frame")
                canvas.create_polygon(x2, y2, x2-s, y2, x2, y2-s, fill="#FFD700", tags="frame")
            elif effect == "6d_glitch":
                off = math.sin(step*0.5)*3
                canvas.create_rectangle(x1+off, y1, x2+off, y2, outline="#FF00FF", width=width, tags="frame")
                canvas.create_rectangle(x1-off, y1, x2-off, y2, outline="#00FFFF", width=width, tags="frame")
            elif effect == "6d_gothic":
                canvas.create_oval(x1, y1, x2, y2, outline="white", width=2, tags="frame")
            elif effect == "fire":
                if len(self._fire_particles) < 25: self._fire_particles.append({'x': cx + random.randint(-50, 50), 'y': y2, 'life': 1.0, 'vy': random.uniform(-2.5, -1.5)})
                for p in self._fire_particles[:]:
                    p['y'] += p['vy']; p['life'] -= 0.04
                    if p['life'] <= 0: self._fire_particles.remove(p)
                    else: canvas.create_oval(p['x']-4, p['y']-4, p['x']+4, p['y']+4, fill=random.choice(["#FF4500", "#FF0000", "#FFA500"]), outline="", tags="frame")
                canvas.create_oval(x1, y1, x2, y2, outline=color, width=width, tags="frame")
            elif effect == "rainbow":
                c = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#8B00FF"][(step//5)%7]
                canvas.create_oval(x1, y1, x2, y2, outline=c, width=width, tags="frame")
            elif effect == "matrix":
                canvas.create_oval(x1, y1, x2, y2, outline="#003300", width=width, tags="frame")
                for _ in range(5):
                    rx = cx + random.randint(-50, 50); ry = cy + random.randint(-50, 50)
                    canvas.create_text(rx, ry, text=random.choice("01"), fill="#00FF00", font=("Courier", 8), tags="frame")
            elif effect == "rotate":
                canvas.create_oval(x1, y1, x2, y2, outline=color, width=width, tags="frame", dash=(10, 5), dashoffset=step)
            else:
                canvas.create_oval(x1, y1, x2, y2, outline=color, width=width, tags="frame")
            
            if f_data["label"]:
                canvas.create_rectangle(cx-40, y2-10, cx+40, y2+10, fill=color, outline="white", tags="frame")
                canvas.create_text(cx, y2, text=f_data["label"], fill="black", font=("Arial Black", 10), tags="frame")
            
            if f_data["type"] == "stattrak":
                canvas.create_rectangle(cx-30, y1-15, cx+30, y1+5, fill="#111111", outline=STATTRAK_ORANGE, tags="frame")
                canvas.create_text(cx, y1-5, text=f"{self.user_time}m", fill=STATTRAK_ORANGE, font=("Courier", 10, "bold"), tags="frame")

        def animate_frame():
            if not self.is_running or not self.ava_canvas.winfo_exists(): return
            self._frame_anim_step += 1
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT frame FROM users WHERE username=?", (self.current_user,))
            res = cur.fetchone(); conn.close(); f_id = res[0] if res and res[0] else "none"
            f_data = next((f for f in AVATAR_FRAMES if f["id"] == f_id), AVATAR_FRAMES[0])
            draw_complex_frame(self.ava_canvas, 20, 20, 120, 120, f_data, self._frame_anim_step)
            self.after(50, animate_frame)

        def load_ava():
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT avatar FROM users WHERE username=?", (self.current_user,))
            res = cur.fetchone(); conn.close(); path = res[0] if res and res[0] else None
            if path and os.path.exists(path):
                try:
                    img = Image.open(path).resize((100, 100), Image.Resampling.LANCZOS)
                    mask = Image.new("L", (100, 100), 0); draw = ImageDraw.Draw(mask); draw.ellipse((0, 0, 100, 100), fill=255)
                    img.putalpha(mask); self.tk_ava = ImageTk.PhotoImage(img); self.ava_canvas.create_image(70, 70, image=self.tk_ava)
                except: self.ava_canvas.create_text(70, 70, text="", fill="white")
            else: self.ava_canvas.create_text(70, 70, text="", fill="white", font=("Arial", 45))
        
        self.load_ava = load_ava; load_ava(); animate_frame()
        self.ava_canvas.bind("<Button-1>", lambda e: self.change_ava()); self.ava_canvas.configure(cursor="hand2")
        ctk.CTkLabel(sidebar, text=self.current_user.upper(), font=("Arial Black", 18)).pack()
        ctk.CTkLabel(sidebar, text=f"LEVEL {self.user_level}", text_color=ACCENT_RED).pack()
        self.coin_label = ctk.CTkLabel(sidebar, text=f" {self.user_coins}", font=("Arial Black", 16), text_color=COIN_GOLD); self.coin_label.pack(pady=(5, 20))
        btns = [(" ГЛАВНАЯ", self.show_main), (" ПРИЛОЖЕНИЯ", self.show_apps_mgmt), (" МАГАЗИН РАМОК", self.show_inventory), (" ЛОГИ", self.show_logs)]
        if self.user_level >= 5: btns.append((" ПОЛЬЗОВАТЕЛИ", self.show_users_mgmt))
        for txt, cmd in btns: ctk.CTkButton(sidebar, text=txt, fg_color="transparent", anchor="w", height=45, command=cmd).pack(fill="x", padx=15, pady=4)
        ctk.CTkButton(sidebar, text="ВЫЙТИ ИЗ АККАУНТА", fg_color="#1A1A1A", hover_color="#330000", height=40, font=("Arial Bold", 12), command=self.logout).pack(side="bottom", fill="x", padx=20, pady=20)
        self.main = ctk.CTkFrame(self, fg_color="transparent"); self.main.grid(row=0, column=1, sticky="nsew")
        self.show_main()

    def show_login_screen(self):
        for w in self.winfo_children():
            if w != getattr(self, 'bg_canvas', None): w.destroy()
        frame = ctk.CTkFrame(self, width=400, height=450, fg_color="#0A0A0A", corner_radius=20, border_width=1, border_color="#222222")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(frame, text="KODIK ULTRA", font=("Arial Black", 32), text_color=ACCENT_RED).pack(pady=(40, 5))
        ctk.CTkLabel(frame, text=f"v{CURRENT_VERSION}", font=("Arial Bold", 14), text_color=TEXT_GRAY).pack(pady=(0, 20))
        u_e = ctk.CTkEntry(frame, placeholder_text="Логин", width=280, height=45); u_e.pack(pady=10)
        p_e = ctk.CTkEntry(frame, placeholder_text="Пароль", show="*", width=280, height=45); p_e.pack(pady=10)
        def login():
            u, p = u_e.get(), p_e.get()
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
            cur.execute("SELECT level, frame, coins, owned_frames, total_time, bg_settings FROM users WHERE username=? AND password=?", (u, p))
            res = cur.fetchone(); conn.close()
            if res:
                self.current_user = u; self.user_level = res[0]; self.current_frame = res[1] if res[1] else "none"
                self.user_coins = res[2]; self.owned_frames = res[3].split(",") if res[3] else ["none"]; self.user_time = res[4]
                if res[5]:
                    try: self.apply_background(json.loads(res[5]), save=False)
                    except: pass
                self.log_event("Успешный вход в систему")
                self.setup_ui()
            else: self.notify("Ошибка входа")
        ctk.CTkButton(frame, text="ВОЙТИ", fg_color=ACCENT_RED, width=280, height=50, command=login).pack(pady=20)
        ctk.CTkButton(frame, text="Создать аккаунт", fg_color="transparent", command=self.show_reg_screen).pack()

    def apply_background(self, bg, save=True):
        self.bg_canvas.configure(bg=bg["color"])
        if bg["type"] == "anim":
            for p in self.particles:
                self.bg_canvas.itemconfig(p['id'], fill=bg['p_color'], state="normal")
                p['base_fill'] = bg['p_color']
        else:
            for p in self.particles:
                self.bg_canvas.itemconfig(p['id'], state="hidden")
        
        if save and self.current_user:
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
            cur.execute("UPDATE users SET bg_settings=? WHERE username=?", (json.dumps(bg), self.current_user))
            conn.commit(); conn.close()
        
        self.notify(f"Фон '{bg['name']}' применен")

    def change_ava(self):
        p = filedialog.askopenfilename()
        if p:
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
            cur.execute("UPDATE users SET avatar=? WHERE username=?", (p, self.current_user))
            conn.commit(); conn.close(); self.load_ava()

    def logout(self):        self.current_user = None; self.show_login_screen()

    def show_main(self):
        for w in self.main.winfo_children(): w.destroy()
        scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent", corner_radius=0); scroll.pack(fill="both", expand=True)
        
        # --- ПОИСК ГЛАВНОГО БАННЕРА ИЗ ПРОЕКТОВ ---
        main_project = next((a for a in self.apps if a.get("is_banner")), None)
        
        if main_project:
            banner_frame = ctk.CTkFrame(scroll, height=350, fg_color="#050505", corner_radius=25, border_width=2, border_color=ACCENT_RED)
            banner_frame.pack(fill="x", padx=20, pady=20)
            banner_frame.pack_propagate(False)
            
            imgs = main_project.get("images", [])
            if imgs and os.path.exists(imgs[0]):
                try:
                    img = ctk.CTkImage(light_image=Image.open(imgs[0]), size=(1100, 350))
                    ctk.CTkLabel(banner_frame, image=img, text="").place(relx=0, rely=0, relwidth=1, relheight=1)
                    ctk.CTkFrame(banner_frame, fg_color="rgba(0,0,0,0.6)", corner_radius=25).place(relx=0, rely=0, relwidth=1, relheight=1)
                except: pass
            
            ctk.CTkLabel(banner_frame, text="ГЛАВНЫЙ ПРОЕКТ", font=("Arial Bold", 14), text_color=ACCENT_RED).place(relx=0.05, rely=0.2)
            ctk.CTkLabel(banner_frame, text=main_project["name"].upper(), font=("Arial Black", 48), text_color="white").place(relx=0.05, rely=0.4)
            
            ctk.CTkButton(banner_frame, text="ОТКРЫТЬ ПРОЕКТ", fg_color=ACCENT_RED, width=200, height=50, 
                          font=("Arial Black", 16), corner_radius=12,
                          command=lambda a=main_project: self.show_app_details(a)).place(relx=0.05, rely=0.7)
        else:
            # Стандартный админ-баннер, если проект не выбран
            banner_file = os.path.join(os.path.dirname(DATA_FILE), "banner_info.json")
            banner_data = {"text": "ДОБРО ПОЖАЛОВАТЬ В DEEPTECH ULTRA", "color": ACCENT_RED, "font": "Arial Black", "size": 24, "image": None}
            if os.path.exists(banner_file):
                try:
                    with open(banner_file, "r", encoding="utf-8") as f: banner_data.update(json.load(f))
                except: pass

            banner_frame = ctk.CTkFrame(scroll, fg_color="#050505", corner_radius=15, border_width=1, border_color="#222222", height=200)
            banner_frame.pack(fill="x", padx=20, pady=(20, 10))
            banner_frame.pack_propagate(False)
            
            if banner_data.get("image") and os.path.exists(banner_data["image"]):
                try:
                    img = ctk.CTkImage(light_image=Image.open(banner_data["image"]), size=(1100, 200))
                    ctk.CTkLabel(banner_frame, image=img, text="").place(relx=0, rely=0, relwidth=1, relheight=1)
                    ctk.CTkFrame(banner_frame, fg_color="rgba(0,0,0,0.5)", corner_radius=15).place(relx=0, rely=0, relwidth=1, relheight=1)
                except: pass

            banner_label = ctk.CTkLabel(banner_frame, text=banner_data["text"], 
                                        text_color=banner_data["color"], 
                                        font=(banner_data["font"], banner_data["size"]),
                                        justify="center", fg_color="transparent")
            banner_label.place(relx=0.5, rely=0.5, anchor="center")

        if self.user_level >= 5:
            def edit_banner_ui():
                # ... (код редактирования остается прежним)
                def content(body, dialog):
                    dialog.configure(height=850)
                    ctk.CTkLabel(body, text="Текст баннера").pack()
                    t_e = ctk.CTkTextbox(body, width=400, height=100)
                    t_e.pack(pady=5); t_e.insert("1.0", banner_data["text"])
                    
                    ctk.CTkLabel(body, text="Цвет (HEX)").pack()
                    c_e = ctk.CTkEntry(body, width=400); c_e.pack(pady=5); c_e.insert(0, banner_data["color"])
                    
                    ctk.CTkLabel(body, text="Шрифт").pack()
                    f_e = ctk.CTkComboBox(body, values=["Arial Black", "Courier New", "Impact", "Verdana"], width=400)
                    f_e.pack(pady=5); f_e.set(banner_data["font"])
                    
                    ctk.CTkLabel(body, text="Размер шрифта").pack()
                    s_e = ctk.CTkEntry(body, width=400); s_e.pack(pady=5); s_e.insert(0, str(banner_data["size"]))

                    self.temp_banner_img = banner_data.get("image")
                    img_status = ctk.CTkLabel(body, text="Картинка не выбрана" if not self.temp_banner_img else "Картинка выбрана", text_color="gray")
                    
                    def pick_banner_img():
                        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
                        if path: 
                            self.temp_banner_img = path
                            img_status.configure(text="Картинка выбрана", text_color=PLAY_GREEN)
                    
                    ctk.CTkButton(body, text="ВЫБРАТЬ ФОН БАННЕРА", fg_color="#222222", command=pick_banner_img).pack(pady=10)
                    img_status.pack()

                    def save_b():
                        try:
                            new_data = {
                                "text": t_e.get("1.0", "end-1c"), 
                                "color": c_e.get(), 
                                "font": f_e.get(), 
                                "size": int(s_e.get()),
                                "image": self.temp_banner_img
                            }
                            with open(banner_file, "w", encoding="utf-8") as f: json.dump(new_data, f)
                            self.overlay.destroy(); self.show_main()
                        except Exception as e: self.notify(f"Ошибка: {e}")
                        
                    ctk.CTkButton(body, text="ОБНОВИТЬ БАННЕР", fg_color=PLAY_GREEN, height=45, command=save_b).pack(pady=20)
                self.show_overlay("РЕДАКТОР БАННЕРА", content)
            ctk.CTkButton(banner_frame, text="РЕДАКТИРОВАТЬ", width=100, height=20, font=("Arial", 10), 
                          fg_color="#1A1A1A", command=edit_banner_ui).place(relx=1.0, rely=1.0, x=-10, y=-10, anchor="se")
        # --------------------

        ctk.CTkLabel(scroll, text="ДОСТУПНЫЕ ПРОЕКТЫ", font=("Arial Black", 24)).pack(anchor="w", padx=30, pady=(10, 20))
        grid = ctk.CTkFrame(scroll, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=20)
        for i, app in enumerate(self.apps):
            card = ctk.CTkFrame(grid, width=340, height=220, fg_color="#0a0a0a", corner_radius=15, border_width=1, border_color="#222222")
            card.grid(row=i//2, column=i%2, padx=10, pady=10)
            card.pack_propagate(False)
            
            # Фон-скриншот на всю карточку
            imgs = app.get("images", [])
            if imgs and os.path.exists(imgs[0]):
                try:
                    img = ctk.CTkImage(light_image=Image.open(imgs[0]), size=(340, 220))
                    ctk.CTkLabel(card, image=img, text="").place(relx=0, rely=0, relwidth=1, relheight=1)
                    # Затемнение нижней части для читаемости текста
                    overlay = ctk.CTkFrame(card, fg_color="transparent")
                    overlay.place(relx=0, rely=0.6, relwidth=1, relheight=0.4)
                    # Имитация градиента через полупрозрачный фрейм
                    ctk.CTkFrame(card, fg_color="rgba(0,0,0,0.7)", corner_radius=0, height=60).place(relx=0, rely=1.0, relwidth=1, anchor="sw")
                except: pass

            # Название проекта (слева внизу)
            ctk.CTkLabel(card, text=app["name"].upper(), font=("Arial Black", 18), text_color="white", fg_color="transparent").place(relx=0.05, rely=0.85, anchor="w")
            
            # Кнопка выбора (справа внизу)
            ctk.CTkButton(card, text="ВЫБРАТЬ", fg_color=ACCENT_RED, hover_color="#CC0000", width=100, height=32, 
                          font=("Arial Black", 12), corner_radius=8,
                          command=lambda a=app: self.show_app_details(a)).place(relx=0.95, rely=0.85, anchor="e")
    def show_app_details(self, app):
        for w in self.main.winfo_children(): w.destroy()
        header = ctk.CTkFrame(self.main, fg_color="transparent"); header.pack(fill="x", pady=(20, 10), padx=20)
        ctk.CTkButton(header, text=" НАЗАД", width=100, fg_color="#1A1A1A", command=self.show_main).pack(side="left")
        ctk.CTkLabel(header, text=app["name"].upper(), font=("Arial Black", 28)).pack(side="left", padx=20)
        
        content = ctk.CTkFrame(self.main, fg_color="#0a0a0a", corner_radius=20, border_width=1, border_color="#222222"); content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая часть со скриншотами
        left = ctk.CTkFrame(content, fg_color="transparent"); left.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        main_view = ctk.CTkFrame(left, fg_color="#050505", corner_radius=15, height=350); main_view.pack(fill="x", pady=(0, 15)); main_view.pack_propagate(False)
        preview_l = ctk.CTkLabel(main_view, text="НЕТ СКРИНШОТОВ"); preview_l.pack(fill="both", expand=True)
        
        def set_preview(path):
            if os.path.exists(path):
                try:
                    img = ctk.CTkImage(light_image=Image.open(path), size=(550, 330))
                    preview_l.configure(image=img, text="")
                except: pass

        def change_main_image():
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
            if path:
                if "images" not in app: app["images"] = []
                if app["images"]:
                    app["images"][0] = path # Заменяем первое изображение
                else:
                    app["images"].append(path)
                self.save_data()
                set_preview(path)
                self.notify("Главное изображение обновлено", PLAY_GREEN)

        imgs = app.get("images", [])
        if imgs:
            set_preview(imgs[0])
            
        if self.user_level >= 5:
            ctk.CTkButton(left, text="ИЗМЕНИТЬ ПРЕВЬЮ", fg_color="#1A1A1A", height=30, 
                          command=change_main_image).pack(pady=5)

        if imgs and len(imgs) > 1:
            thumb_s = ctk.CTkScrollableFrame(left, orientation="horizontal", height=100, fg_color="transparent")
            thumb_s.pack(fill="x", pady=5)
            for p in imgs:
                try:
                    t_img = ctk.CTkImage(light_image=Image.open(p), size=(140, 80))
                    t_btn = ctk.CTkLabel(thumb_s, image=t_img, text="", cursor="hand2")
                    t_btn.pack(side="left", padx=8)
                    t_btn.bind("<Button-1>", lambda e, path=p: set_preview(path))
                except: pass

        # Правая часть с описанием
        right = ctk.CTkFrame(content, fg_color="transparent", width=350); right.pack(side="right", fill="both", padx=20, pady=20); right.pack_propagate(False)
        ctk.CTkLabel(right, text="ОПИСАНИЕ", font=("Arial Black", 20), text_color=ACCENT_RED).pack(anchor="w")
        desc_s = ctk.CTkScrollableFrame(right, fg_color="transparent", height=300); desc_s.pack(fill="both", expand=True, pady=10)
        ctk.CTkLabel(desc_s, text=app.get("desc", "Нет описания"), font=("Arial", 15), justify="left", wraplength=300).pack(anchor="nw")
        
        def launch():
            try:
                p = app.get("path")
                if p.endswith(".py"): subprocess.Popen(["python", p], shell=True)
                else: subprocess.Popen([p], shell=True)
                self.log_event(f"Запуск проекта: {app['name']}")
                self.notify("Запуск проекта...", PLAY_GREEN)
            except Exception as e: 
                self.log_event(f"Ошибка запуска {app['name']}: {e}")
                self.notify(f"Ошибка запуска: {e}")
            
        ctk.CTkButton(right, text="ЗАПУСТИТЬ", fg_color=PLAY_GREEN, height=60, font=("Arial Black", 18), corner_radius=15, command=launch).pack(side="bottom", fill="x")

    def show_apps_mgmt(self):
        for w in self.main.winfo_children(): w.destroy()
        header = ctk.CTkFrame(self.main, fg_color="transparent"); header.pack(fill="x", pady=20, padx=30)
        ctk.CTkLabel(header, text="УПРАВЛЕНИЕ ПРОЕКТАМИ", font=("Arial Black", 24)).pack(side="left")
        if self.user_level >= 5: ctk.CTkButton(header, text="+ ДОБАВИТЬ", fg_color=PLAY_GREEN, command=self.add_app_ui).pack(side="right")
        scroll = ctk.CTkScrollableFrame(self.main, fg_color="#0a0a0a", corner_radius=20); scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        for app in self.apps:
            f = ctk.CTkFrame(scroll, fg_color="#0a0a0a", height=60, border_width=1, border_color="#222222"); f.pack(fill="x", pady=5, padx=10); f.pack_propagate(False)
            ctk.CTkLabel(f, text=app['name'].upper()).pack(side="left", padx=20)
            
            if self.user_level >= 5:
                ctk.CTkButton(f, text="УДАЛИТЬ", fg_color="#440000", width=80, command=lambda a=app: self.delete_app(a)).pack(side="right", padx=10)
                
                # Кнопка назначения баннером
                is_b = app.get("is_banner", False)
                b_text = "★ ГЛАВНЫЙ" if is_b else "СДЕЛАТЬ ГЛАВНЫМ"
                b_color = ACCENT_RED if is_b else "#1A1A1A"
                
                ctk.CTkButton(f, text=b_text, fg_color=b_color, width=150, 
                              command=lambda a=app: self.set_main_banner(a)).pack(side="right", padx=10)

    def show_users_mgmt(self):
        for w in self.main.winfo_children(): w.destroy()
        ctk.CTkLabel(self.main, text="УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ", font=("Arial Black", 24)).pack(pady=20)
        scroll = ctk.CTkScrollableFrame(self.main, fg_color="transparent"); scroll.pack(fill="both", expand=True)
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT username, level, coins FROM users"); users = cur.fetchall(); conn.close()
        for u, l, c in users:
            f = ctk.CTkFrame(scroll, fg_color="#0D0D0D", height=60); f.pack(fill="x", pady=5, padx=10); f.pack_propagate(False)
            ctk.CTkLabel(f, text=f"{u} (LVL {l}) |  {c}").pack(side="left", padx=20)
            btn_f = ctk.CTkFrame(f, fg_color="transparent"); btn_f.pack(side="right", padx=10)
            if self.user_level >= 3:
                ctk.CTkButton(btn_f, text="ВЫДАТЬ 6D", width=90, height=30, fg_color="#A020F0", command=lambda user=u: self.give_6d_ui(user)).pack(side="left", padx=5)
            if self.user_level >= 5:
                ctk.CTkButton(btn_f, text="МОНЕТЫ", width=70, height=30, command=lambda user=u: self.give_coins_ui(user)).pack(side="left", padx=5)
                ctk.CTkButton(btn_f, text="LVL", width=50, height=30, command=lambda user=u, current=l: self.edit_lvl(user, current)).pack(side="left", padx=5)

    def give_6d_ui(self, user):
        def content(body, dialog):
            ctk.CTkLabel(body, text=f"ВЫБЕРИТЕ 6D РАМКУ ДЛЯ {user}").pack(pady=10)
            scroll = ctk.CTkScrollableFrame(body, fg_color="transparent", height=300); scroll.pack(fill="both", expand=True)
            for f in [fr for fr in AVATAR_FRAMES if fr["type"] == "6d"]:
                row = ctk.CTkFrame(scroll, fg_color="#111111", height=60); row.pack(fill="x", pady=5); row.pack_propagate(False)
                c = tk.Canvas(row, width=50, height=50, bg="#111111", highlightthickness=0); c.pack(side="left", padx=10)
                c.create_oval(5, 5, 45, 45, outline=f["color"], width=3); c.create_text(25, 25, text="", fill="white", font=("Arial", 10))
                ctk.CTkLabel(row, text=f["name"]).pack(side="left", padx=10)
                def give(f_id=f["id"]):
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT owned_frames FROM users WHERE username=?", (user,)); res = cur.fetchone()
                    if res:
                        owned = res[0].split(","); owned.append(f_id); new_owned = ",".join(list(set(owned)))
                        cur.execute("UPDATE users SET owned_frames=? WHERE username=?", (new_owned, user)); conn.commit()
                        self.notify(f"Рамка {f_id} выдана!", PLAY_GREEN)
                    conn.close(); self.overlay.destroy()
                ctk.CTkButton(row, text="ВЫДАТЬ", width=80, height=30, fg_color=f["color"], command=give).pack(side="right", padx=10)
        self.show_overlay("ВЫДАЧА 6D", content)

    def edit_lvl(self, user, current):
        def content(body, dialog):
            ctk.CTkLabel(body, text=f"УРОВЕНЬ ДЛЯ {user}", font=("Arial Black", 14)).pack(pady=10)
            e = ctk.CTkEntry(body, width=100, justify="center", font=("Arial Bold", 16)); e.pack(pady=20); e.insert(0, str(current))
            def save():
                try:
                    val = int(e.get())
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("UPDATE users SET level=? WHERE username=?", (val, user)); conn.commit(); conn.close(); self.overlay.destroy(); self.show_users_mgmt(); self.notify(f"Уровень {user} изменен на {val}", PLAY_GREEN)
                except ValueError: self.notify("Введите число!", ACCENT_RED)
            ctk.CTkButton(body, text="СОХРАНИТЬ", fg_color=ACCENT_RED, font=("Arial Bold", 14), height=40, command=save).pack(pady=10)
        self.show_overlay("ИЗМЕНЕНИЕ УРОВНЯ", content)

    def give_coins_ui(self, user):
        def content(body, dialog):
            ctk.CTkLabel(body, text=f"ВЫДАЧА МОНЕТ ДЛЯ {user}", font=("Arial Black", 14)).pack(pady=10)
            e = ctk.CTkEntry(body, placeholder_text="Введите сумму...", width=200, justify="center")
            e.pack(pady=20)
            
            def save():
                try:
                    amount = int(e.get())
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor()
                    cur.execute("UPDATE users SET coins = coins + ? WHERE username=?", (amount, user))
                    conn.commit(); conn.close()
                    self.overlay.destroy(); self.show_users_mgmt()
                    self.notify(f"Выдано {amount} монет пользователю {user}", PLAY_GREEN)
                    self.log_event(f"Выдача монет: {amount} для {user}", "SUCCESS")
                except ValueError:
                    self.notify("Введите число!", ACCENT_RED)
            
            ctk.CTkButton(body, text="ВЫДАТЬ", fg_color=PLAY_GREEN, width=200, height=40, command=save).pack(pady=10)
        self.show_overlay("МОНЕТЫ", content)

    def edit_lvl(self, user, current):
        def content(body, dialog):
            ctk.CTkLabel(body, text=f"УРОВЕНЬ ДЛЯ {user}").pack(pady=10)
            e = ctk.CTkEntry(body, width=100); e.pack(pady=10); e.insert(0, str(current))
            def save():
                try:
                    v = int(e.get())
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("UPDATE users SET level=? WHERE username=?", (v, user)); conn.commit(); conn.close()
                    self.overlay.destroy(); self.show_users_mgmt(); self.notify("Уровень изменен")
                except: pass
            ctk.CTkButton(body, text="СОХРАНИТЬ", command=save).pack(pady=10)
        self.show_overlay("ИЗМЕНЕНИЕ УРОВНЯ", content)

    def give_6d_ui(self, user):
        def content(body, dialog):
            ctk.CTkLabel(body, text=f"ВЫБЕРИТЕ 6D РАМКУ ДЛЯ {user}").pack(pady=10)
            scroll = ctk.CTkScrollableFrame(body, fg_color="transparent", height=300); scroll.pack(fill="both", expand=True)
            for f in [fr for fr in AVATAR_FRAMES if fr["type"] == "6d"]:
                row = ctk.CTkFrame(scroll, fg_color="#111111", height=50); row.pack(fill="x", pady=2); row.pack_propagate(False)
                ctk.CTkLabel(row, text=f["name"]).pack(side="left", padx=10)
                def give(f_id=f["id"]):
                    conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT owned_frames FROM users WHERE username=?", (user,)); res = cur.fetchone()
                    if res:
                        owned = res[0].split(","); owned.append(f_id); new_owned = ",".join(list(set(owned)))
                        cur.execute("UPDATE users SET owned_frames=? WHERE username=?", (new_owned, user)); conn.commit()
                        self.notify(f"Рамка выдана!", PLAY_GREEN)
                    conn.close(); self.overlay.destroy()
                ctk.CTkButton(row, text="ВЫДАТЬ", width=80, height=25, command=give).pack(side="right", padx=10)
        self.show_overlay("ВЫДАЧА 6D", content)

    def give_coins(self, user, amount):
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("UPDATE users SET coins = coins + ? WHERE username=?", (amount, user)); conn.commit(); conn.close(); self.show_users_mgmt()

    def show_logs(self):
        for w in self.main.winfo_children(): w.destroy()
        ctk.CTkLabel(self.main, text="ЛОГИ СИСТЕМЫ", font=("Arial Black", 24)).pack(pady=20)
        box = ctk.CTkTextbox(self.main, width=800, height=500); box.pack()
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f: 
                    box.insert("1.0", f.read())
            except: pass
    def on_closing(self): self.is_running = False; self.destroy()

    def set_main_banner(self, app):
        # Снимаем флаг со всех и ставим только выбранному (или снимаем, если уже был)
        target_state = not app.get("is_banner", False)
        for a in self.apps:
            a["is_banner"] = False
        app["is_banner"] = target_state
        
        self.save_data()
        self.show_apps_mgmt()
        self.notify("Главный баннер обновлен", PLAY_GREEN)
        self.log_event(f"Изменен главный баннер на: {app['name'] if target_state else 'Стандартный'}", "SUCCESS")

    def delete_app(self, app):
        if app in self.apps:
            self.apps.remove(app)
            self.save_data()
            self.show_apps_mgmt()
            self.notify("Проект удален")

    def add_app_ui(self):
        def content(body, dialog):
            dialog.configure(width=600, height=750)
            ctk.CTkLabel(body, text="Название проекта", font=("Arial Bold", 14)).pack(pady=(10, 0), anchor="w", padx=50)
            n_e = ctk.CTkEntry(body, placeholder_text="Введите название...", width=500); n_e.pack(pady=5)
            ctk.CTkLabel(body, text="Описание", font=("Arial Bold", 14)).pack(pady=(10, 0), anchor="w", padx=50)
            d_e = ctk.CTkTextbox(body, width=500, height=120); d_e.pack(pady=5)
            ctk.CTkLabel(body, text="Исполняемый файл (.exe / .py)", font=("Arial Bold", 14)).pack(pady=(10, 0), anchor="w", padx=50)
            path_f = ctk.CTkFrame(body, fg_color="transparent"); path_f.pack(fill="x", padx=50, pady=5)
            p_e = ctk.CTkEntry(path_f, placeholder_text="Путь к файлу...", width=380); p_e.pack(side="left")
            def pick_exe():
                path = filedialog.askopenfilename(filetypes=[("Executable/Python", "*.exe *.py"), ("All files", "*.*")])
                if path: p_e.delete(0, "end"); p_e.insert(0, path)
            ctk.CTkButton(path_f, text="ОБЗОР", width=110, command=pick_exe).pack(side="right")
            self.temp_imgs = []
            img_label = ctk.CTkLabel(body, text="Скриншоты не выбраны", text_color="gray")
            def pick_imgs():
                paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
                if paths: self.temp_imgs = list(paths); img_label.configure(text=f"Выбрано скриншотов: {len(self.temp_imgs)}", text_color=PLAY_GREEN)
            ctk.CTkButton(body, text="ВЫБРАТЬ СКРИНШОТЫ", fg_color="#222222", width=500, command=pick_imgs).pack(pady=15)
            img_label.pack()
            btn_row = ctk.CTkFrame(body, fg_color="transparent"); btn_row.pack(side="bottom", fill="x", pady=30, padx=50)
            def save():
                if n_e.get() and p_e.get():
                    self.apps.append({'name': n_e.get(), 'desc': d_e.get("1.0", "end-1c"), 'path': p_e.get(), 'images': self.temp_imgs})
                    self.save_data(); self.overlay.destroy(); self.show_apps_mgmt(); self.notify("Проект добавлен!", PLAY_GREEN)
                else: self.notify("Заполните название и путь!")
            ctk.CTkButton(btn_row, text="ОТМЕНА", fg_color="#1A1A1A", width=180, height=45, command=self.overlay.destroy).pack(side="left")
            ctk.CTkButton(btn_row, text="СОХРАНИТЬ", fg_color=PLAY_GREEN, width=300, height=45, command=save).pack(side="right")
        self.show_overlay("НОВЫЙ ПРОЕКТ", content)

    def show_inventory(self):
        for w in self.main.winfo_children(): w.destroy()
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("SELECT coins, owned_frames, frame FROM users WHERE username=?", (self.current_user,)); res = cur.fetchone(); conn.close()
        self.user_coins, owned_str, self.current_frame = res; self.owned_frames = owned_str.split(",")
        ctk.CTkLabel(self.main, text="МАГАЗИН 3D & 6D РАМОК", font=("Arial Black", 28), text_color=ACCENT_RED).pack(pady=30)
        scroll = ctk.CTkScrollableFrame(self.main, fg_color="#0a0a0a", border_width=1, border_color="#222222", corner_radius=20); scroll.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        grid = ctk.CTkFrame(scroll, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        def draw_preview(canvas, f_data):
            canvas.delete("all")
            color = f_data["color"]; width = f_data["width"]; effect = f_data["effect"]
            if effect == "6d_kitty":
                canvas.create_oval(15, 15, 85, 85, outline="#FFB6C1", width=4)
            elif effect == "6d_gold":
                canvas.create_rectangle(15, 15, 85, 85, outline="#FFD700", width=6)
                canvas.create_polygon(15, 15, 30, 15, 15, 30, fill="#FFD700")
            elif f_data["type"] == "stattrak":
                canvas.create_oval(15, 15, 85, 85, outline=color, width=width)
                canvas.create_rectangle(30, 10, 70, 25, fill="#111111", outline=STATTRAK_ORANGE)
                canvas.create_text(50, 17, text="0000", fill=STATTRAK_ORANGE, font=("Courier", 8))
            else:
                canvas.create_oval(15, 15, 85, 85, outline=color, width=width)
            canvas.create_text(50, 50, text="", fill="white", font=("Arial", 20))

        for i, frame in enumerate(AVATAR_FRAMES):
            is_owned = frame["id"] in self.owned_frames; is_active = self.current_frame == frame["id"]
            if frame["type"] == "6d" and not is_owned: continue
            card = ctk.CTkFrame(grid, width=180, height=260, fg_color="#111111", corner_radius=15, border_width=2 if is_active else 0, border_color=frame["color"])
            card.grid(row=i//4, column=i%4, padx=15, pady=15); card.pack_propagate(False)
            c = tk.Canvas(card, width=100, height=100, bg="#111111", highlightthickness=0); c.pack(pady=15)
            draw_preview(c, frame)
            ctk.CTkLabel(card, text=frame["name"], font=("Arial Bold", 13)).pack()
            if is_owned:
                if is_active: ctk.CTkLabel(card, text="АКТИВНО", text_color=PLAY_GREEN, font=("Arial Black", 10)).pack(pady=10)
                else: ctk.CTkButton(card, text="НАДЕТЬ", fg_color="#222222", height=30, command=lambda f=frame["id"]: self.equip_f(f)).pack(pady=10)
            else: ctk.CTkButton(card, text=f"КУПИТЬ: {frame['price']}", fg_color="#330000", height=30, command=lambda f=frame: self.buy_f(f)).pack(pady=10)

    def equip_f(self, f_id):
        conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("UPDATE users SET frame=? WHERE username=?", (f_id, self.current_user)); conn.commit(); conn.close(); self.show_inventory(); self.notify("Рамка надета!")

    def buy_f(self, f):
        if self.user_coins >= f["price"]:
            new_owned = ",".join(self.owned_frames + [f["id"]])
            conn = sqlite3.connect(DB_FILE); cur = conn.cursor(); cur.execute("UPDATE users SET coins = coins - ?, owned_frames = ? WHERE username=?", (f["price"], new_owned, self.current_user)); conn.commit(); conn.close(); self.show_inventory(); self.notify("Покупка успешна!", PLAY_GREEN)
        else: self.notify("Недостаточно монет!", ACCENT_RED)

    def show_logs(self, filter_type="ВСЕ"):
        for w in self.main.winfo_children(): w.destroy()
        
        header = ctk.CTkFrame(self.main, fg_color="transparent")
        header.pack(fill="x", pady=20, padx=30)
        
        ctk.CTkLabel(header, text="ЛОГИ СИСТЕМЫ", font=("Arial Black", 24), text_color=ACCENT_RED).pack(side="left")
        
        # Кнопки фильтрации
        filter_f = ctk.CTkFrame(header, fg_color="transparent")
        filter_f.pack(side="right")
        
        for t in ["ВСЕ", "INFO", "ERROR", "SUCCESS"]:
            btn = ctk.CTkButton(filter_f, text=t, width=80, height=30, 
                                fg_color=ACCENT_RED if filter_type == t else "#1A1A1A",
                                command=lambda x=t: self.show_logs(x))
            btn.pack(side="left", padx=5)

        # Текстовое поле для логов
        box = ctk.CTkTextbox(self.main, width=800, height=500, fg_color="#050505", border_width=1, border_color="#222222")
        box.pack(padx=20, pady=10, fill="both", expand=True)
        
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        if filter_type == "ВСЕ" or f"[{filter_type}]" in line:
                            box.insert("end", line)
            except Exception as e:
                box.insert("1.0", f"Ошибка чтения логов: {e}")
        else:
            box.insert("1.0", "Файл логов пуст или не создан.")
        
        box.configure(state="disabled")
        box.see("end") # Прокрутка вниз

if __name__ == "__main__":
    app = AdmHelper(); app.mainloop()
    app = AdmHelper(); app.mainloop()
