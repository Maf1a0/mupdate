import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import threading, time, os, platform, json, random, sys, base64, io
import urllib.request
import urllib.error
import tempfile
import shutil
import subprocess
import hashlib

if platform.system() == "Windows":
    try:
        import ctypes
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00000080)
        try:
            import win32process
            win32process.SetProcessWorkingSetSize(-1, -1, -1)
        except: pass
    except: pass

PY_AUTO = False
HAS_KEYBOARD = False
HAS_PYNPUT = False
pyautogui = None
keyboard = None
pynput = None
mouse = None
pynput_keyboard = None

try:
    import pyautogui as pg
    pg.FAILSAFE = False
    pyautogui = pg
    PY_AUTO = True
except: pass

try:
    import keyboard as kb
    keyboard = kb
    HAS_KEYBOARD = True
except: pass

try:
    import pynput as pn
    from pynput import mouse as pm, keyboard as pk
    pynput = pn
    mouse = pm
    pynput_keyboard = pk
    HAS_PYNPUT = True
except: pass

COLORS = {
    "bg_main": "#0f0f0f",
    "bg_card": "#1a1a1a",
    "bg_accent": "#252525",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "accent_cyan": "#0099cc",
    "accent_pink": "#cc0052",
    "accent_purple": "#6b46c1",
    "accent_orange": "#cc7700",
    "accent_green": "#00cc66",
    "accent_blue": "#0080cc",
    "accent_red": "#cc0000",
}

GITHUB_REPO_OWNER = "Maf1a0"
GITHUB_REPO_NAME = "Mupdate"
CURRENT_VERSION = "1.0.2"
CORRECT_PASSWORD = "808maf1a808"

def get_maf1a_path():
    documents_path = os.path.expanduser("~\\Documents") if platform.system() == "Windows" else os.path.expanduser("~/Documents")
    maf1a_path = os.path.join(documents_path, "System py [MaF1a]")
    if not os.path.exists(maf1a_path):
        try:
            os.makedirs(maf1a_path)
        except:
            pass
    return maf1a_path

MAF1A_PATH = get_maf1a_path()
POSITIONS_FILE = os.path.join(MAF1A_PATH, "pos.txt")
SETTINGS_FILE = os.path.join(MAF1A_PATH, "set.json")

APP_NAMES = ["Discord", "Microsoft Edge","Google Chrome", "Spotify",
             "Steam", "WhatsApp", "Telegram", "Skype", "Zoom", "Visual Studio Code",
             "Slack", "Notepad", "Calculator", "Windows Explorer", "Media Player",
             "Adobe Reader", "Photoshop", "Word", "Excel", "PowerPoint"]

ICON_BASE64 = """
"""

class PasswordManager:
    """إدارة كلمة المرور عبر Windows Registry"""

    @staticmethod
    def _get_registry_key():
        """الحصول على مفتاح Registry"""
        if platform.system() == "Windows":
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                except:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                return key, winreg
            except:
                return None, None
        return None, None

    @staticmethod
    def _hash_password(password):
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def save_password_hash(password):
        """حفظ hash كلمة المرور في Registry"""
        key, winreg = PasswordManager._get_registry_key()
        if key and winreg:
            try:
                hashed = PasswordManager._hash_password(password)
                winreg.SetValueEx(key, "SystemConfig", 0, winreg.REG_SZ, hashed)
                winreg.CloseKey(key)
                return True
            except:
                pass
        return False

    @staticmethod
    def is_password_saved():
        """التحقق من وجود كلمة مرور محفوظة"""
        key, winreg = PasswordManager._get_registry_key()
        if key and winreg:
            try:
                value, _ = winreg.QueryValueEx(key, "SystemConfig")
                winreg.CloseKey(key)
                return value is not None and len(value) > 0
            except:
                pass
        return False

    @staticmethod
    def verify_password(password):
        """التحقق من كلمة المرور"""
        key, winreg = PasswordManager._get_registry_key()
        if key and winreg:
            try:
                saved_hash, _ = winreg.QueryValueEx(key, "SystemConfig")
                winreg.CloseKey(key)
                return saved_hash == PasswordManager._hash_password(password)
            except:
                pass
        return False

class PasswordWindow:
    """نافذة إدخال كلمة المرور"""

    def __init__(self):
        self.password_correct = False
        self.window = tk.Tk()
        self.window.title("Authentication")
        self.window.geometry("280x160")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["bg_main"])
        self.window.attributes('-topmost', True)

        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (280 // 2)
        y = (self.window.winfo_screenheight() // 2) - (160 // 2)
        self.window.geometry(f"280x160+{x}+{y}")

        self._build_ui()

        self.window.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _build_ui(self):
        title_frame = tk.Frame(self.window, bg=COLORS["bg_card"], height=45)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="🔐 Password Required",
                fg=COLORS["accent_cyan"], bg=COLORS["bg_card"],
                font=("Segoe UI", 11, "bold")).pack(expand=True)

        info_frame = tk.Frame(self.window, bg=COLORS["bg_card"])
        info_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(info_frame, text="Please enter password:",
                fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                font=("Segoe UI", 9)).pack(pady=(5, 3))

        self.password_entry = tk.Entry(info_frame, width=25, show="*",
                                      bg=COLORS["bg_accent"], fg=COLORS["text_primary"],
                                      font=("Segoe UI", 10), relief="flat", bd=0,
                                      insertbackground=COLORS["accent_cyan"])
        self.password_entry.pack(pady=5, ipady=4)
        self.password_entry.focus()
        self.password_entry.bind('<Return>', lambda e: self.check_password())

        self.error_label = tk.Label(info_frame, text="",
                                    fg=COLORS["accent_red"], bg=COLORS["bg_card"],
                                    font=("Segoe UI", 8))
        self.error_label.pack(pady=2)

        btn_frame = tk.Frame(self.window, bg=COLORS["bg_main"])
        btn_frame.pack(fill="x", padx=10, pady=10)

        from tkinter import Button

        ok_btn = Button(btn_frame, text="OK", command=self.check_password,
                       bg=COLORS["accent_green"], fg="white",
                       font=("Segoe UI", 9, "bold"), relief="flat",
                       bd=0, padx=20, pady=5, cursor="hand2")
        ok_btn.pack(side="left", padx=5)

        cancel_btn = Button(btn_frame, text="Cancel", command=self.on_cancel,
                           bg=COLORS["accent_pink"], fg="white",
                           font=("Segoe UI", 9, "bold"), relief="flat",
                           bd=0, padx=20, pady=5, cursor="hand2")
        cancel_btn.pack(side="right", padx=5)

    def check_password(self):
        entered_password = self.password_entry.get()

        if entered_password == CORRECT_PASSWORD:
            PasswordManager.save_password_hash(entered_password)
            self.password_correct = True
            self.window.destroy()
        else:
            self.error_label.config(text="❌ Incorrect password!")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

    def on_cancel(self):
        self.password_correct = False
        self.window.destroy()
        sys.exit(0)

    def show(self):
        self.window.mainloop()
        return self.password_correct

class UpdateWindow:
    def __init__(self, parent, latest_version, download_url):
        self.parent = parent
        self.latest_version = latest_version
        self.download_url = download_url
        self.updating = False

        self.window = tk.Toplevel(parent)
        self.window.title("Update Available")
        self.window.geometry("350x250")
        self.window.resizable(False, False)
        self.window.configure(bg=COLORS["bg_main"])
        self.window.attributes('-topmost', True)

        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.window.winfo_screenheight() // 2) - (250 // 2)
        self.window.geometry(f"350x250+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        title_frame = tk.Frame(self.window, bg=COLORS["bg_card"], height=50)
        title_frame.pack(fill="x", padx=10, pady=(10, 5))
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="🔔 New Update Available",
                fg=COLORS["accent_cyan"], bg=COLORS["bg_card"],
                font=("Segoe UI", 12, "bold")).pack(expand=True)

        info_frame = tk.Frame(self.window, bg=COLORS["bg_card"])
        info_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(info_frame, text=f"تم العثور على تحديث جديد",
                fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                font=("Segoe UI", 10)).pack(pady=5)

        tk.Label(info_frame, text=f"الإصدار الجديد: {self.latest_version}",
                fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                font=("Segoe UI", 9)).pack(pady=2)

        status_frame = tk.Frame(self.window, bg=COLORS["bg_card"])
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(status_frame, text="Status:",
                fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=5, pady=(5,2))

        self.status_text = tk.Text(status_frame, height=4, width=40,
                                   bg=COLORS["bg_accent"], fg=COLORS["text_primary"],
                                   font=("Consolas", 8), relief="flat", bd=0,
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_status("Ready to update...")

        btn_frame = tk.Frame(self.window, bg=COLORS["bg_main"])
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.update_btn = ModernButton(btn_frame, "Start Update", self.start_update,
                                       COLORS["accent_green"], width=150, height=35)
        self.update_btn.pack(side="left", padx=5)

        self.later_btn = ModernButton(btn_frame, "Later", self.close_window,
                                      COLORS["accent_pink"], width=150, height=35)
        self.later_btn.pack(side="right", padx=5)

    def update_status(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.window.update()

    def start_update(self):
        if self.updating:
            return

        self.updating = True
        self.update_btn.config(state='disabled')

        def update_thread():
            try:
                self.update_status("Checking...")
                time.sleep(0.5)

                self.update_status("Downloading update...")

                temp_dir = tempfile.gettempdir()
                update_file = os.path.join(temp_dir, "autoclicker_update.py")

                urllib.request.urlretrieve(self.download_url, update_file)

                self.update_status("Installing...")
                time.sleep(0.5)

                current_file = os.path.abspath(sys.argv[0])
                backup_file = current_file + ".backup"

                if os.path.exists(current_file):
                    shutil.copy2(current_file, backup_file)

                shutil.copy2(update_file, current_file)

                self.update_status("Done!")
                self.update_status("البرنامج سيتم إعادة تشغيله...")
                time.sleep(1)

                python = sys.executable
                os.execl(python, python, *sys.argv)

            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                self.updating = False
                self.update_btn.config(state='normal')

        threading.Thread(target=update_thread, daemon=True).start()

    def close_window(self):
        self.window.destroy()

class GitHubUpdater:
    def __init__(self, repo_owner, repo_name, current_version):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version

    def check_for_updates(self):
        try:
            api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"

            req = urllib.request.Request(api_url)
            req.add_header('User-Agent', 'AutoClicker-Updater')

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

                latest_version = data.get('tag_name', '').lstrip('v')
                download_url = None

                for asset in data.get('assets', []):
                    if asset['name'].endswith('.py'):
                        download_url = asset['browser_download_url']
                        break

                if not download_url:
                    download_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/autoclicker.py"

                if self._compare_versions(latest_version, self.current_version) > 0:
                    return True, latest_version, download_url

            return False, None, None

        except Exception as e:
            print(f"Update check error: {e}")
            return False, None, None

    def _compare_versions(self, v1, v2):
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]

            for i in range(max(len(parts1), len(parts2))):
                p1 = parts1[i] if i < len(parts1) else 0
                p2 = parts2[i] if i < len(parts2) else 0

                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1

            return 0
        except:
            return 0

class GlobalHotkeys:
    def __init__(self, app):
        self.app = app
        self.hotkeys_set = False
        self.global_listener = None

    def start(self):
        def start_async():
            if not HAS_PYNPUT:
                if HAS_KEYBOARD and keyboard:
                    try:
                        keyboard.add_hotkey('f2', lambda: self.app.root.after(0, self.app.on_start), suppress=False)
                        keyboard.add_hotkey('f3', lambda: self.app.root.after(0, self.app.on_stop), suppress=False)
                        keyboard.add_hotkey('f4', lambda: self.app.root.after(0, self.app.stop_tracking), suppress=False)
                        keyboard.add_hotkey('f5', lambda: self.app.root.after(0, self.app.toggle_visibility), suppress=False)
                        keyboard.add_hotkey('f9', lambda: self.app.root.after(0, self.app.reset_esc_count), suppress=False)
                        keyboard.add_hotkey('f10', lambda: self.app.root.after(0, self.app.on_exit), suppress=False)
                        self.hotkeys_set = True
                    except Exception:
                        pass
                return

            if HAS_PYNPUT and pynput_keyboard:
                try:
                    def on_key_press(key):
                        try:
                            if hasattr(key, 'name'):
                                key_name = key.name
                            else:
                                key_name = str(key).replace("'", "")

                            if key_name == 'f2':
                                self.app.root.after(0, self.app.on_start)
                            elif key_name == 'f3':
                                self.app.root.after(0, self.app.on_stop)
                            elif key_name == 'f4':
                                self.app.root.after(0, self.app.stop_tracking)
                            elif key_name == 'f5':
                                self.app.root.after(0, self.app.toggle_visibility)
                            elif key_name == 'f9':
                                self.app.root.after(0, self.app.reset_esc_count)
                            elif key_name == 'f10':
                                self.app.root.after(0, self.app.on_exit)
                        except Exception:
                            pass

                    self.global_listener = pynput_keyboard.Listener(on_press=on_key_press, suppress=False)
                    self.global_listener.start()
                    self.hotkeys_set = True
                except Exception:
                    pass

        threading.Thread(target=start_async, daemon=True).start()

    def stop(self):
        if self.global_listener:
            try:
                self.global_listener.stop()
            except Exception:
                pass

        if self.hotkeys_set and HAS_KEYBOARD and keyboard:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass

        self.hotkeys_set = False

class AutoClicker:
    def __init__(self):
        self.positions = []
        self.click_delay = 0.001
        self.running = False
        self.thread = None
        self.hold_e = False
        self.press_enter_enabled = False
        self.press_f_enabled = False
        self.press_q_enabled = False
        self.press_e_every_minute = False
        self.right_click_every_half_second = False
        self.unhold_mode = False
        self.out_mode = False
        self.out_start_delay = 0
        self.out_push_delay = 0
        self.out_counter = 0
        self.last_enter_time = time.time()
        self.last_f_time = time.time()
        self.last_q_time = time.time()
        self.last_e_minute_time = time.time()
        self.last_right_click_time = time.time()
        self.last_unhold_position_index = 0
        self.last_unhold_click_time = time.time()
        self.stop_event = threading.Event()
        self.out_active = False

    def add_position(self, x, y, btn="left", hold_duration=0.0):
        self.positions.append((x, y, btn, hold_duration))
        self.save_positions_txt()
        return True

    def remove_position(self, index):
        if 0 <= index < len(self.positions):
            self.positions.pop(index)
            self.save_positions_txt()
            return True
        return False

    def clear_positions(self):
        self.positions = []
        self.save_positions_txt()
        return True

    def save_positions_txt(self, path=None):
        try:
            file_path = path or POSITIONS_FILE
            with open(file_path, "w", encoding="utf-8") as f:
                for x, y, btn, hold_duration in self.positions:
                    f.write(f"{x},{y},{btn},{hold_duration}\n")
            return True
        except Exception:
            return False

    def load_positions_txt(self, path=None):
        try:
            file_path = path or POSITIONS_FILE
            if not os.path.exists(file_path):
                return True

            self.positions = []

            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    parts = line.split(",")
                    if len(parts) >= 2:
                        x = int(parts[0].strip())
                        y = int(parts[1].strip())
                        btn = parts[2].strip() if len(parts) > 2 else "left"
                        hold_duration = float(parts[3]) if len(parts) > 3 else 0.0
                        self.positions.append((x, y, btn, hold_duration))
            return True
        except Exception:
            return False

    def _run_loop(self):
        try:
            out_cycle_start_time = time.time()
            out_sequence_started = False
            out_positions_executed = False

            while self.running and not self.stop_event.is_set():
                current_time = time.time()

                if self.out_mode:
                    time_since_out_cycle = current_time - out_cycle_start_time

                    if not out_sequence_started and time_since_out_cycle >= self.out_start_delay:
                        self._execute_out_sequence()
                        out_sequence_started = True
                        self.out_active = True
                        self.last_out_execution_time = current_time

                    elif out_sequence_started and not out_positions_executed and (current_time - self.last_out_execution_time) >= self.out_push_delay:
                        if self.positions:
                            if self.hold_e:
                                if HAS_KEYBOARD and keyboard:
                                    try:
                                        keyboard.press_and_release('e')
                                    except Exception:
                                        pass
                                elif PY_AUTO and pyautogui:
                                    try:
                                        pyautogui.press('e')
                                    except Exception:
                                        pass
                                time.sleep(0.001)

                            if self.unhold_mode:
                                for x, y, btn, hold_duration in self.positions:
                                    if not self.running or self.stop_event.is_set():
                                        break
                                    if PY_AUTO and pyautogui:
                                        try:
                                            calculated_delay = max(0.0001, float(self.click_delay))
                                            pyautogui.moveTo(x, y, duration=calculated_delay)
                                            pyautogui.click(button=btn, clicks=1)
                                        except Exception:
                                            pass
                                    time.sleep(0.5)
                            else:
                                for x, y, btn, hold_duration in self.positions:
                                    if not self.running or self.stop_event.is_set():
                                        break
                                    if PY_AUTO and pyautogui:
                                        try:
                                            calculated_delay = max(0.0001, float(self.click_delay))
                                            pyautogui.moveTo(x, y, duration=calculated_delay)
                                            pyautogui.click(button=btn, clicks=1)
                                        except Exception:
                                            pass
                                    time.sleep(0.001)

                        out_positions_executed = True
                        out_cycle_start_time = current_time
                        out_sequence_started = False
                        out_positions_executed = False
                        self.out_active = False
                else:
                    if not self.unhold_mode:
                        if self.positions:
                            if self.hold_e:
                                if HAS_KEYBOARD and keyboard:
                                    try:
                                        keyboard.press_and_release('e')
                                    except Exception:
                                        pass
                                elif PY_AUTO and pyautogui:
                                    try:
                                        pyautogui.press('e')
                                    except Exception:
                                        pass
                                time.sleep(0.001)

                            for x, y, btn, hold_duration in self.positions:
                                if not self.running or self.stop_event.is_set():
                                    break

                                if PY_AUTO and pyautogui:
                                    try:
                                        calculated_delay = max(0.0001, float(self.click_delay))
                                        pyautogui.moveTo(x, y, duration=calculated_delay)
                                        pyautogui.click(button=btn, clicks=1)
                                    except Exception:
                                        pass
                                time.sleep(max(0.0001, float(self.click_delay)))

                if self.press_enter_enabled and (current_time - self.last_enter_time) >= 0.25:
                    if HAS_KEYBOARD and keyboard:
                        try:
                            keyboard.press_and_release('enter')
                        except Exception:
                            pass
                    elif PY_AUTO and pyautogui:
                        try:
                            pyautogui.press('enter')
                        except Exception:
                            pass
                    self.last_enter_time = current_time

                if self.press_f_enabled and (current_time - self.last_f_time) >= 2.0:
                    if HAS_KEYBOARD and keyboard:
                        try:
                            keyboard.press_and_release('f')
                        except Exception:
                            pass
                    elif PY_AUTO and pyautogui:
                        try:
                            pyautogui.press('f')
                        except Exception:
                            pass
                    self.last_f_time = current_time

                if self.press_q_enabled and (current_time - self.last_q_time) >= 2.0:
                    if HAS_KEYBOARD and keyboard:
                        try:
                            keyboard.press_and_release('q')
                        except Exception:
                            pass
                    elif PY_AUTO and pyautogui:
                        try:
                            pyautogui.press('q')
                        except Exception:
                            pass
                    self.last_q_time = current_time

                if self.press_e_every_minute and (current_time - self.last_e_minute_time) >= 60.0:
                    if HAS_KEYBOARD and keyboard:
                        try:
                            keyboard.press_and_release('e')
                        except Exception:
                            pass
                    elif PY_AUTO and pyautogui:
                        try:
                            pyautogui.press('e')
                        except Exception:
                            pass
                    self.last_e_minute_time = current_time

                if self.right_click_every_half_second and (current_time - self.last_right_click_time) >= 0.25:
                    if PY_AUTO and pyautogui:
                        try:
                            pyautogui.click(button='right', clicks=1)
                            time.sleep(0.25)
                            pyautogui.click(button='right', clicks=1)
                        except Exception:
                            pass
                    self.last_right_click_time = current_time

                if self.unhold_mode and self.positions:
                    if (current_time - self.last_unhold_click_time) >= 0.25:
                        try:
                            for x, y, btn, hold_duration in self.positions:
                                if not self.running or self.stop_event.is_set():
                                    break

                                if PY_AUTO and pyautogui:
                                    try:
                                        calculated_delay = max(0.0001, float(self.click_delay))
                                        pyautogui.moveTo(x, y, duration=calculated_delay)
                                        pyautogui.click(button=btn, clicks=1)
                                    except Exception:
                                        pass

                                time.sleep(0.5)

                            self.last_unhold_click_time = current_time
                        except Exception:
                            pass

                time.sleep(0.001)
        except Exception:
            pass

    def _execute_out_sequence(self):
        time.sleep(2.0)

        if HAS_KEYBOARD and keyboard:
            try:
                keyboard.press_and_release('esc')
            except Exception:
                pass
        elif PY_AUTO and pyautogui:
            try:
                pyautogui.press('esc')
            except Exception:
                pass

        self.out_counter += 1

        time.sleep(1)

        if HAS_KEYBOARD and keyboard:
            try:
                keyboard.press_and_release('enter')
            except Exception:
                pass
        elif PY_AUTO and pyautogui:
            try:
                pyautogui.press('enter')
            except Exception:
                pass

        time.sleep(0.001)

        if HAS_KEYBOARD and keyboard:
            try:
                keyboard.press_and_release('enter')
            except Exception:
                pass
        elif PY_AUTO and pyautogui:
            try:
                pyautogui.press('enter')
            except Exception:
                pass

        time.sleep(1)

        if HAS_KEYBOARD and keyboard:
            try:
                keyboard.press_and_release('enter')
            except Exception:
                pass
        elif PY_AUTO and pyautogui:
            try:
                pyautogui.press('enter')
            except Exception:
                pass

    def start(self):
        if self.running:
            return
        self.stop_event.clear()
        self.running = True
        self.last_unhold_position_index = 0
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.stop_event.set()
        try:
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=0.5)
        except Exception:
            pass

class GlobalMouseTracker:
    def __init__(self, app):
        self.app = app
        self.mouse_listener = None
        self.tracking = False
        self.continuous_mode = False

    def start_tracking(self, continuous=False):
        if self.tracking:
            return

        self.tracking = True
        self.continuous_mode = continuous

        def start_async():
            if HAS_PYNPUT and mouse:
                def on_click(x, y, button, pressed):
                    if pressed and self.tracking:
                        try:
                            self.app.root.after(0, lambda: self.app.add_global_position_silent(x, y, 0.0))
                        except Exception:
                            pass

                try:
                    self.mouse_listener = mouse.Listener(on_click=on_click)
                    self.mouse_listener.start()
                    return True
                except Exception:
                    return False
            return False

        threading.Thread(target=start_async, daemon=True).start()
        return True

    def stop_tracking(self):
        if not self.tracking:
            return

        self.tracking = False

        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, color, width=120, height=32):
        super().__init__(parent, width=width, height=height, bg=COLORS["bg_main"],
                        highlightthickness=0, relief='flat')

        self.command = command
        self.color = color
        self.text = text
        self.width = width
        self.height = height
        self.is_hovered = False

        self.draw_button()
        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

    def draw_button(self):
        self.delete('all')

        color = self.lighten_color(self.color) if self.is_hovered else self.color

        radius = self.height // 2
        x1, y1 = 2, 2
        x2, y2 = self.width - 2, self.height - 2

        self.create_arc(x1, y1, x1 + 2*radius, y2, start=90, extent=180,
                       fill=color, outline='')
        self.create_arc(x2 - 2*radius, y1, x2, y2, start=270, extent=180,
                       fill=color, outline='')
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                            fill=color, outline='')

        self.create_text(self.width // 2, self.height // 2,
                        text=self.text, fill='white',
                        font=('Segoe UI', 9, 'bold'))

    def lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, int(r * 1.15))
        g = min(255, int(g * 1.15))
        b = min(255, int(b * 1.15))
        return f'#{r:02x}{g:02x}{b:02x}'

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.is_hovered = True
        self.draw_button()
        self.config(cursor='hand2')

    def on_leave(self, event):
        self.is_hovered = False
        self.draw_button()
        self.config(cursor='')

class ModernApp:
    def __init__(self, root):
        self.root = root
        self.current_app_name = random.choice(APP_NAMES)
        self.root.title(self.current_app_name)
        self.root.geometry("230x380")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg_main"])

        self.set_icon_from_base64(ICON_BASE64)

        self.root.attributes('-alpha', 0.80)
        self.root.attributes('-topmost', False)

        if platform.system() == "Windows":
            try:
                self.root.attributes('-toolwindow', False)
                self.change_task_manager_name()
            except:
                pass

        self.clicker = AutoClicker()
        self.hotkeys = GlobalHotkeys(self)
        self.mouse_tracker = GlobalMouseTracker(self)
        self.tracking_mouse = False
        self.hidden = False
        self.last_counter_value = -1

        self.load_settings()
        self._build_ui()

        threading.Thread(target=self._load_positions_async, daemon=True).start()
        threading.Thread(target=self.hotkeys.start, daemon=True).start()

        threading.Thread(target=self.check_updates_on_startup, daemon=True).start()

        self.root.after(300000, self._change_window_title)
        self.root.after(100, self._update_counter_display)

    def check_updates_on_startup(self):
        try:
            time.sleep(2)

            updater = GitHubUpdater(GITHUB_REPO_OWNER, GITHUB_REPO_NAME, CURRENT_VERSION)
            has_update, latest_version, download_url = updater.check_for_updates()

            if has_update and latest_version and download_url:
                self.root.after(0, lambda: UpdateWindow(self.root, latest_version, download_url))

        except Exception as e:
            print(f"Update check failed: {e}")

    def set_icon_from_base64(self, base64_string):
        try:
            import tkinter as tk
            icon_data = base64.b64decode(base64_string)
            self.icon_image = tk.PhotoImage(data=icon_data)
            self.root.iconphoto(True, self.icon_image)
        except Exception as e:
            try:
                self.root.iconbitmap(default='')
            except:
                pass

    def change_task_manager_name(self):
        if platform.system() == "Windows":
            try:
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW(self.current_app_name)
            except:
                pass

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    self.saved_hold_e = settings.get('hold_e', False)
                    self.saved_enter = settings.get('press_enter', False)
                    self.saved_f = settings.get('press_f', False)
                    self.saved_q = settings.get('press_q', False)
                    self.saved_e_minute = settings.get('press_e_minute', False)
                    self.saved_right_click = settings.get('right_click', False)
                    self.saved_unhold = settings.get('unhold', False)
                    self.saved_out = settings.get('out_mode', False)
                    self.saved_out_start_delay = settings.get('out_start_delay', 0)
                    self.saved_out_push_delay = settings.get('out_push_delay', 0)
                    self.saved_click_delay = settings.get('click_delay', 0.001)
            else:
                self.saved_hold_e = False
                self.saved_enter = False
                self.saved_f = False
                self.saved_q = False
                self.saved_e_minute = False
                self.saved_right_click = False
                self.saved_unhold = False
                self.saved_out = False
                self.saved_out_start_delay = 0
                self.saved_out_push_delay = 0
                self.saved_click_delay = 0.001
        except Exception:
            self.saved_hold_e = False
            self.saved_enter = False
            self.saved_f = False
            self.saved_q = False
            self.saved_e_minute = False
            self.saved_right_click = False
            self.saved_unhold = False
            self.saved_out = False
            self.saved_out_start_delay = 0
            self.saved_out_push_delay = 0
            self.saved_click_delay = 0.001

    def save_settings(self):
        try:
            settings = {
                'hold_e': self.chk_hold_e_var.get(),
                'press_enter': self.chk_enter_var.get(),
                'press_f': self.chk_f_var.get(),
                'press_q': self.chk_q_var.get(),
                'press_e_minute': self.chk_e_minute_var.get(),
                'right_click': self.chk_right_click_var.get(),
                'unhold': self.chk_unhold_var.get(),
                'out_mode': self.chk_out_var.get(),
                'out_start_delay': float(self.out_start_delay_entry.get() or 0),
                'out_push_delay': float(self.out_push_delay_entry.get() or 0),
                'click_delay': float(self.delay_entry.get() or 0.001)
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f)
        except Exception:
            pass

    def _change_window_title(self):
        try:
            self.current_app_name = random.choice(APP_NAMES)
            self.root.title(self.current_app_name)

            if platform.system() == "Windows":
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetConsoleTitleW(self.current_app_name)
                except:
                    pass
        except:
            pass
        self.root.after(300000, self._change_window_title)

    def _load_positions_async(self):
        self.clicker.load_positions_txt()
        self.root.after(0, self.refresh_positions)

    def _update_counter_display(self):
        try:
            if self.clicker.out_counter != self.last_counter_value:
                self.out_counter_label.config(text=f"C: {self.clicker.out_counter}")
                self.last_counter_value = self.clicker.out_counter
        except Exception:
            pass
        self.root.after(100, self._update_counter_display)

    def toggle_visibility(self):
        if self.hidden:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.hidden = False
        else:
            self.root.withdraw()
            self.hidden = True

    def reset_esc_count(self):
        self.clicker.out_counter = 0
        self.out_counter_label.config(text=f"C: {self.clicker.out_counter}")
        self.last_counter_value = 0

    def _build_ui(self):
        main = tk.Frame(self.root, bg=COLORS["bg_main"])
        main.pack(fill="both", expand=True, padx=2, pady=2)

        config_section = tk.Frame(main, bg=COLORS["bg_card"], relief="flat")
        config_section.pack(fill="x", pady=(0,2))

        tk.Label(config_section, text="⚙ Configuration", fg=COLORS["accent_cyan"],
                 bg=COLORS["bg_card"], font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=5, pady=(2,1))

        options_grid = tk.Frame(config_section, bg=COLORS["bg_card"])
        options_grid.pack(fill="x", padx=5, pady=(0,2))

        self.chk_hold_e_var = tk.BooleanVar(value=self.saved_hold_e)
        self.chk_enter_var = tk.BooleanVar(value=self.saved_enter)
        self.chk_f_var = tk.BooleanVar(value=self.saved_f)
        self.chk_q_var = tk.BooleanVar(value=self.saved_q)
        self.chk_e_minute_var = tk.BooleanVar(value=self.saved_e_minute)
        self.chk_right_click_var = tk.BooleanVar(value=self.saved_right_click)
        self.chk_unhold_var = tk.BooleanVar(value=self.saved_unhold)
        self.chk_out_var = tk.BooleanVar(value=self.saved_out)

        chk1 = tk.Checkbutton(options_grid, text="E before", variable=self.chk_hold_e_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk1.grid(row=0, column=0, sticky="w", padx=2, pady=1)

        chk2 = tk.Checkbutton(options_grid, text="F", variable=self.chk_f_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk2.grid(row=0, column=1, sticky="w", padx=2, pady=1)

        chk2b = tk.Checkbutton(options_grid, text="Q", variable=self.chk_q_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk2b.grid(row=1, column=0, sticky="w", padx=2, pady=1)

        chk3 = tk.Checkbutton(options_grid, text="E/1min", variable=self.chk_e_minute_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk3.grid(row=0, column=2, sticky="w", padx=2, pady=1)

        chk4 = tk.Checkbutton(options_grid, text="Enter", variable=self.chk_enter_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk4.grid(row=1, column=1, sticky="w", padx=2, pady=1)

        chk5 = tk.Checkbutton(options_grid, text="Unhold", variable=self.chk_unhold_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk5.grid(row=1, column=2, sticky="w", padx=2, pady=1)

        chk6 = tk.Checkbutton(options_grid, text="Out", variable=self.chk_out_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk6.grid(row=2, column=1, sticky="w", padx=2, pady=1)

        self.out_counter_label = tk.Label(options_grid, text=f"C: {self.clicker.out_counter}",
                                          fg=COLORS["accent_cyan"], bg=COLORS["bg_card"],
                                          font=("Segoe UI", 7))
        self.out_counter_label.grid(row=2, column=2, sticky="w", padx=2, pady=1)

        chk7 = tk.Checkbutton(options_grid, text="R-Click", variable=self.chk_right_click_var,
                            fg=COLORS["text_primary"], bg=COLORS["bg_card"],
                            selectcolor=COLORS["bg_accent"],
                            activebackground=COLORS["bg_card"],
                            activeforeground=COLORS["text_primary"],
                            font=("Segoe UI", 7), command=self.save_settings)
        chk7.grid(row=2, column=0, sticky="w", padx=2, pady=1)

        out_frame = tk.Frame(config_section, bg=COLORS["bg_card"])
        out_frame.pack(fill="x", padx=5, pady=(0,2))

        tk.Label(out_frame, text="Out.S:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=("Segoe UI", 8)).pack(side="left", padx=(0,1))
        self.out_start_delay_entry = tk.Entry(out_frame, width=4, bg=COLORS["bg_accent"],
                                     fg=COLORS["text_primary"], font=("Segoe UI", 8),
                                     relief="flat", bd=0, insertbackground=COLORS["accent_cyan"])
        self.out_start_delay_entry.insert(0, str(self.saved_out_start_delay))
        self.out_start_delay_entry.pack(side="left", ipady=1)
        self.out_start_delay_entry.bind('<FocusOut>', lambda e: self.save_settings())

        tk.Label(out_frame, text="Out.P:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=("Segoe UI", 8)).pack(side="left", padx=(4,1))
        self.out_push_delay_entry = tk.Entry(out_frame, width=4, bg=COLORS["bg_accent"],
                                     fg=COLORS["text_primary"], font=("Segoe UI", 8),
                                     relief="flat", bd=0, insertbackground=COLORS["accent_cyan"])
        self.out_push_delay_entry.insert(0, str(self.saved_out_push_delay))
        self.out_push_delay_entry.pack(side="left", ipady=1)
        self.out_push_delay_entry.bind('<FocusOut>', lambda e: self.save_settings())

        delay_frame = tk.Frame(config_section, bg=COLORS["bg_card"])
        delay_frame.pack(fill="x", padx=5, pady=(2,2))

        tk.Label(delay_frame, text="Delay:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=("Segoe UI", 7)).pack(side="left", padx=(0,1))
        self.delay_entry = tk.Entry(delay_frame, width=5, bg=COLORS["bg_accent"],
                                     fg=COLORS["text_primary"], font=("Segoe UI", 7),
                                     relief="flat", bd=0, insertbackground=COLORS["accent_cyan"])
        self.delay_entry.insert(0, str(self.saved_click_delay))
        self.delay_entry.pack(side="left", ipady=1)
        self.delay_entry.bind('<FocusOut>', lambda e: self.save_settings())

        tk.Label(delay_frame, text="Speed:", fg=COLORS["text_secondary"],
                 bg=COLORS["bg_card"], font=("Segoe UI", 7)).pack(side="left", padx=(4,1))
        self.speed_entry = tk.Entry(delay_frame, width=4, bg=COLORS["bg_accent"],
                                     fg=COLORS["text_primary"], font=("Segoe UI", 7),
                                     relief="flat", bd=0, insertbackground=COLORS["accent_cyan"])
        self.speed_entry.insert(0, str(self.saved_click_delay))
        self.speed_entry.pack(side="left", ipady=1)
        self.speed_entry.bind('<FocusOut>', lambda e: self.save_settings())

        track_section = tk.Frame(main, bg=COLORS["bg_card"], relief="flat")
        track_section.pack(fill="x", pady=(0,2))

        self.track_btn = ModernButton(track_section, "Track (F4)", self.toggle_tracking,
                                      COLORS["accent_red"], width=220, height=28)
        self.track_btn.pack(pady=3, padx=5, fill="x")

        list_section = tk.Frame(main, bg=COLORS["bg_card"], relief="flat")
        list_section.pack(fill="both", expand=True, pady=(0,2))

        list_btn_frame = tk.Frame(list_section, bg=COLORS["bg_card"])
        list_btn_frame.pack(fill="x", padx=5, pady=(0,2))

        ModernButton(list_btn_frame, "Clear", self.on_clear,
                    COLORS["accent_orange"], width=52, height=24).pack(side="left", padx=1)

        ModernButton(list_btn_frame, "Del", self.delete_position,
                    COLORS["accent_pink"], width=52, height=24).pack(side="left", padx=1)

        ModernButton(list_btn_frame, "Open", self.load_from_file,
                    COLORS["accent_purple"], width=52, height=24).pack(side="left", padx=1)

        ModernButton(list_btn_frame, "Save", self.save_to_file,
                    COLORS["accent_blue"], width=52, height=24).pack(side="left", padx=1)

        self.pos_text = tk.Text(list_section, height=1,
                                bg=COLORS["bg_accent"], fg=COLORS["text_primary"],
                                font=("Consolas", 7), relief="flat", bd=0,
                                selectbackground=COLORS["accent_cyan"],
                                selectforeground=COLORS["bg_main"],
                                insertbackground=COLORS["accent_cyan"],
                                wrap=tk.NONE)
        self.pos_text.pack(fill="both", expand=True, padx=5, pady=(0,2))

        self.pos_text.bind('<MouseWheel>', self._on_mousewheel)
        self.pos_text.bind('<Button-4>', self._on_mousewheel)
        self.pos_text.bind('<Button-5>', self._on_mousewheel)

        ctrl_section = tk.Frame(main, bg=COLORS["bg_main"])
        ctrl_section.pack(fill="x")

        main_controls = tk.Frame(ctrl_section, bg=COLORS["bg_main"])
        main_controls.pack()

        self.start_btn = ModernButton(main_controls, "Start", self.on_start,
                                      COLORS["accent_green"], width=50, height=25)
        self.start_btn.pack(side="left", padx=1)

        self.stop_btn = ModernButton(main_controls, "Stop", self.on_stop,
                                     COLORS["accent_pink"], width=50, height=25)
        self.stop_btn.pack(side="left", padx=1)

        self.hide_btn = ModernButton(main_controls, "Hide", self.toggle_visibility,
                                     COLORS["accent_blue"], width=50, height=25)
        self.hide_btn.pack(side="left", padx=1)

        self.root.bind('<F2>', lambda e: self.on_start())
        self.root.bind('<F3>', lambda e: self.on_stop())
        self.root.bind('<F4>', lambda e: self.stop_tracking())
        self.root.bind('<F5>', lambda e: self.toggle_visibility())
        self.root.bind('<F9>', lambda e: self.reset_esc_count())
        self.root.bind('<F10>', lambda e: self.on_exit())
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def _on_mousewheel(self, event):
        try:
            if event.num == 5 or event.delta < 0:
                self.pos_text.yview_scroll(3, "units")
            elif event.num == 4 or event.delta > 0:
                self.pos_text.yview_scroll(-3, "units")
        except:
            pass

    def toggle_tracking(self):
        if not self.tracking_mouse:
            self.tracking_mouse = True
            self.track_btn.color = COLORS["accent_red"]
            self.track_btn.text = "Stop Track (F4)"
            self.track_btn.draw_button()

            self.root.withdraw()
            self.hidden = True

            if self.mouse_tracker.start_tracking(continuous=True):
                pass
        else:
            self.stop_tracking()

    def stop_tracking(self):
        if self.tracking_mouse:
            self.tracking_mouse = False
            self.track_btn.color = COLORS["accent_red"]
            self.track_btn.text = "Track (F4)"
            self.track_btn.draw_button()
            self.mouse_tracker.stop_tracking()

            if self.hidden:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.hidden = False

    def add_global_position_silent(self, x, y, hold_duration):
        try:
            btn = "left"
            self.clicker.add_position(x, y, btn, hold_duration)
            self.refresh_positions()
        except Exception:
            pass

    def refresh_positions(self):
        try:
            self.pos_text.config(state=tk.NORMAL)
            self.pos_text.delete(1.0, tk.END)

            idx = 1
            for x, y, btn, hold_duration in self.clicker.positions:
                hold_info = f" [{hold_duration:.2f}s]" if hold_duration > 0 else ""
                self.pos_text.insert(tk.END, f"{idx}: ({x},{y}) {btn}{hold_info}\n")
                idx += 1

            self.pos_text.config(state=tk.DISABLED)
        except Exception:
            pass

    def on_clear(self):
        result = messagebox.askyesno("Confirm", "Clear all positions?", parent=self.root)
        if result:
            self.clicker.clear_positions()
            self.refresh_positions()

    def delete_position(self):
        try:
            sel = self.pos_text.tag_ranges(tk.SEL)
            if sel:
                text = self.pos_text.get(sel[0], sel[1]).strip()
                if ":" in text:
                    idx_str = text.split(":")[0].strip()
                    try:
                        idx = int(idx_str) - 1
                        self.clicker.remove_position(idx)
                        self.refresh_positions()
                    except ValueError:
                        messagebox.showwarning("Warning", "Invalid selection", parent=self.root)
            else:
                messagebox.showwarning("Warning", "Select a position first", parent=self.root)
        except Exception:
            messagebox.showwarning("Warning", "Select a position first", parent=self.root)

    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Open Positions File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            parent=self.root
        )
        if file_path:
            if self.clicker.load_positions_txt(file_path):
                self.refresh_positions()
                messagebox.showinfo("Success", "Positions loaded successfully", parent=self.root)
            else:
                messagebox.showerror("Error", "Failed to load positions", parent=self.root)

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Positions File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            parent=self.root
        )
        if file_path:
            if self.clicker.save_positions_txt(file_path):
                messagebox.showinfo("Success", "Positions saved successfully", parent=self.root)
            else:
                messagebox.showerror("Error", "Failed to save positions", parent=self.root)

    def on_start(self):
        try:
            self.clicker.click_delay = float(self.speed_entry.get() or 0.001)

            self.clicker.hold_e = bool(self.chk_hold_e_var.get())
            self.clicker.press_enter_enabled = bool(self.chk_enter_var.get())
            self.clicker.press_f_enabled = bool(self.chk_f_var.get())
            self.clicker.press_q_enabled = bool(self.chk_q_var.get())
            self.clicker.press_e_every_minute = bool(self.chk_e_minute_var.get())
            self.clicker.right_click_every_half_second = bool(self.chk_right_click_var.get())
            self.clicker.unhold_mode = bool(self.chk_unhold_var.get())
            self.clicker.out_mode = bool(self.chk_out_var.get())

            self.clicker.out_start_delay = float(self.out_start_delay_entry.get() or 0)
            self.clicker.out_push_delay = float(self.out_push_delay_entry.get() or 0)

            self.save_settings()

            if not self.clicker.out_mode:
                self.clicker.out_counter = 0

            self.out_counter_label.config(text=f"C: {self.clicker.out_counter}")

            self.clicker.start()

            self.root.withdraw()
            self.hidden = True
        except Exception:
            pass

    def on_stop(self):
        try:
            self.clicker.stop()

            if self.hidden:
                self.root.deiconify()
                self.root.lift()
                self.root.focus_force()
                self.hidden = False
        except Exception:
            pass

    def on_exit(self):
        try:
            self.save_settings()
        except:
            pass
        try:
            self.hotkeys.stop()
        except Exception:
            pass
        try:
            self.mouse_tracker.stop_tracking()
        except Exception:
            pass
        self.clicker.stop()
        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

def main():
    if not PasswordManager.is_password_saved():
        password_window = PasswordWindow()
        if not password_window.show():
            return

    try:
        import socket
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        lock_socket.bind(("localhost", 65432))
    except Exception:
        try:
            root_tmp = tk.Tk()
            root_tmp.withdraw()
            messagebox.showerror("Error", "Application already running")
            root_tmp.destroy()
        except Exception:
            pass
        return

    root = tk.Tk()

    if platform.system() == "Windows":
        try:
            root.attributes('-toolwindow', False)
        except:
            pass

    app = ModernApp(root)

    try:
        root.mainloop()
    except Exception:
        pass

if __name__ == "__main__":
    main()
