import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

BG_COLOR = "#ffffff"
CARD_BG = "#f3f3f3"
BORDER_COLOR = "#e5e5e5"
TEXT_COLOR = "#000000"
TEXT_SECONDARY = "#5f5f5f"
ACCENT_BLUE = "#0067b8"
ACCENT_HOVER = "#005293"
PROGRESS_BG = "#e0e0e0"

class Windows11InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VALORANT RPC - App Installer")
        self.root.geometry("520x400")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.style = ttk.Style()
        try:
            self.style.theme_use('vista')
        except Exception:
            pass

        self.style.configure("Fluent.Horizontal.TProgressbar", 
                             thickness=6, 
                             troughcolor=PROGRESS_BG, 
                             background=ACCENT_BLUE, 
                             bordercolor=BG_COLOR, 
                             lightcolor=ACCENT_BLUE, 
                             darkcolor=ACCENT_BLUE)

        self.default_install_dir = os.path.join(os.environ["LOCALAPPDATA"], "Valorant-RPC")
        self.install_dir = tk.StringVar(value=self.default_install_dir)

        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_shortcut = tk.BooleanVar(value=True)
        self.launch_after = tk.BooleanVar(value=True)
        
        self.current_step = 1 # 1: Welcome, 2: Directory Setup, 3: Installing, 4: Finished

        self.render_layout()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def render_layout(self):
        self.clear_screen()

        self.container = tk.Frame(self.root, bg=BG_COLOR)
        self.container.pack(fill="both", expand=True, padx=40, pady=30)

        if self.current_step == 1:
            self.show_welcome_screen()
        elif self.current_step == 2:
            self.show_directory_screen()
        elif self.current_step == 3:
            self.show_installing_screen()
        elif self.current_step == 4:
            self.show_finished_screen()

    def show_welcome_screen(self):
        header_frame = tk.Frame(self.container, bg=BG_COLOR)
        header_frame.pack(fill="x", pady=(0, 20))

        logo_canvas = tk.Canvas(header_frame, width=48, height=48, bg=BG_COLOR, highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 15))
        logo_canvas.create_oval(2, 2, 46, 46, fill=ACCENT_BLUE, outline="")
        logo_canvas.create_polygon(16, 14, 34, 14, 25, 34, fill=BG_COLOR)

        title_frame = tk.Frame(header_frame, bg=BG_COLOR)
        title_frame.pack(side="left", fill="both", expand=True, padx=12)

        app_title = tk.Label(title_frame, text="VALORANT RPC", font=("Segoe UI", 16, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        app_title.pack(anchor="w")

        publisher_lbl = tk.Label(title_frame, text="Version 3.2.3  •  Published by baeowsky", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR)
        publisher_lbl.pack(anchor="w")

        card = tk.Frame(self.container, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 20))

        card_title = tk.Label(card, text="Capabilities & Features:", font=("Segoe UI", 9, "bold"), fg=TEXT_COLOR, bg=CARD_BG)
        card_title.pack(anchor="w", padx=20, pady=(15, 8))

        features = [
            "🎮 Displays live map, agent, match score and lobby status on Discord.",
            "🔌 Includes global RPC Active toggle to instantly clear your status.",
            "🚀 Integrates with system startup and background tray menu.",
            "🛡️ Safe, light-weight, zero-token local presence connection."
        ]

        for ft in features:
            f_lbl = tk.Label(card, text=ft, font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=CARD_BG, justify="left", wraplength=400)
            f_lbl.pack(anchor="w", padx=20, pady=2)

        # Footer Buttons
        footer = tk.Frame(self.container, bg=BG_COLOR)
        footer.pack(fill="x", side="bottom")

        cancel_btn = tk.Button(footer, text="Cancel", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=CARD_BG, relief="flat", bd=0, highlightbackground=BORDER_COLOR, highlightthickness=1, cursor="hand2", command=self.root.quit, width=12)
        cancel_btn.pack(side="left", ipady=4)

        install_btn = tk.Button(footer, text="Install", font=("Segoe UI", 9, "bold"), fg=BG_COLOR, bg=ACCENT_BLUE, activebackground=ACCENT_HOVER, relief="flat", bd=0, cursor="hand2", command=self.go_to_directory, width=12)
        install_btn.pack(side="right", ipady=4)

    def go_to_directory(self):
        self.current_step = 2
        self.render_layout()

    def show_directory_screen(self):
        header_lbl = tk.Label(self.container, text="Choose installation settings", font=("Segoe UI", 14, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        header_lbl.pack(anchor="w", pady=(0, 20))

        lbl_dir = tk.Label(self.container, text="Install Location:", font=("Segoe UI", 9, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        lbl_dir.pack(anchor="w")

        picker_frame = tk.Frame(self.container, bg=BG_COLOR)
        picker_frame.pack(fill="x", pady=(5, 20))

        path_entry = tk.Entry(picker_frame, textvariable=self.install_dir, font=("Segoe UI", 9), fg=TEXT_COLOR, bg=BG_COLOR, insertbackground=TEXT_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, bd=0)
        path_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 10))

        browse_btn = tk.Button(picker_frame, text="Browse...", font=("Segoe UI", 8), bg=CARD_BG, relief="flat", bd=0, highlightbackground=BORDER_COLOR, highlightthickness=1, cursor="hand2", command=self.browse_folder, width=10)
        browse_btn.pack(side="right", ipady=2)

        opts_frame = tk.Frame(self.container, bg=BG_COLOR)
        opts_frame.pack(fill="x", pady=5)

        cb1 = tk.Checkbutton(opts_frame, text="Create Desktop Shortcut", variable=self.create_desktop_shortcut, font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR, bd=0)
        cb1.pack(anchor="w", pady=4)

        cb2 = tk.Checkbutton(opts_frame, text="Create Start Menu Shortcut", variable=self.create_start_shortcut, font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=BG_COLOR, selectcolor=BG_COLOR, bd=0)
        cb2.pack(anchor="w", pady=4)

        footer = tk.Frame(self.container, bg=BG_COLOR)
        footer.pack(fill="x", side="bottom")

        back_btn = tk.Button(footer, text="Back", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=CARD_BG, relief="flat", bd=0, highlightbackground=BORDER_COLOR, highlightthickness=1, cursor="hand2", command=self.go_back, width=12)
        back_btn.pack(side="left", ipady=4)

        install_btn = tk.Button(footer, text="Install Now", font=("Segoe UI", 9, "bold"), fg=BG_COLOR, bg=ACCENT_BLUE, activebackground=ACCENT_HOVER, relief="flat", bd=0, cursor="hand2", command=self.start_installation, width=12)
        install_btn.pack(side="right", ipady=4)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Install Folder")
        if selected:
            normalized = os.path.normpath(selected)
            if not normalized.endswith("Valorant-RPC"):
                normalized = os.path.join(normalized, "Valorant-RPC")
            self.install_dir.set(normalized)

    def go_back(self):
        self.current_step = 1
        self.render_layout()

    def show_installing_screen(self):
        title_lbl = tk.Label(self.container, text="Installing Valorant RPC", font=("Segoe UI", 14, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title_lbl.pack(anchor="w", pady=(20, 5))

        self.log_lbl = tk.Label(self.container, text="Preparing installation folder...", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_COLOR)
        self.log_lbl.pack(anchor="w", pady=(0, 20))

        self.progress = ttk.Progressbar(self.container, orient="horizontal", style="Fluent.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", pady=10)
        self.progress["maximum"] = 100
        self.progress["value"] = 5

    def start_installation(self):
        self.current_step = 3
        self.render_layout()
        self.root.after(200, self.perform_installation)

    def perform_installation(self):
        dest_dir = self.install_dir.get()

        try:
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            self.progress["value"] = 25
            self.log_lbl.config(text="Extracting program assets...")
            self.root.update()

            if getattr(sys, 'frozen', False):
                bundle_dir = sys._MEIPASS
            else:
                bundle_dir = os.path.dirname(os.path.abspath(__file__))

            src_exe = os.path.join(bundle_dir, "valorant-rpc.exe")
            
            if not os.path.exists(src_exe):
                src_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "valorant-rpc.exe")

            if not os.path.exists(src_exe):
                raise FileNotFoundError(f"Source executable not found at: {src_exe}")

            dest_exe = os.path.join(dest_dir, "valorant-rpc.exe")

            shutil.copy2(src_exe, dest_exe)
            self.progress["value"] = 60
            self.log_lbl.config(text="Creating desktop shortcuts...")
            self.root.update()

            if self.create_desktop_shortcut.get():
                desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
                shortcut_path = os.path.join(desktop_dir, "Valorant RPC.lnk")
                self.create_win_shortcut(dest_exe, shortcut_path, dest_dir)

            if self.create_start_shortcut.get():
                start_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                shortcut_path = os.path.join(start_dir, "Valorant RPC.lnk")
                self.create_win_shortcut(dest_exe, shortcut_path, dest_dir)

            self.progress["value"] = 85
            self.log_lbl.config(text="Registering uninstaller information...")
            self.root.update()

            self.register_uninstaller(dest_dir, dest_exe)

            self.progress["value"] = 100
            self.log_lbl.config(text="Installation completed successfully!")
            self.root.update()

            self.root.after(500, self.go_to_finished)

        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n{e}")
            self.current_step = 2
            self.render_layout()

    def create_win_shortcut(self, target_path, shortcut_path, working_dir):
        try:
            powershell_cmd = (
                f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}'); "
                f"$s.TargetPath = '{target_path}'; "
                f"$s.WorkingDirectory = '{working_dir}'; "
                f"$s.Save()"
            )
            subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True)
        except Exception:
            pass

    def register_uninstaller(self, install_dir, exe_path):
        uninstaller_bat = os.path.join(install_dir, "uninstall.bat")
        
        bat_content = f"""@echo off
taskkill /f /im valorant-rpc.exe >nul 2>&1
timeout /t 1 /nobreak >nul
del /q "{os.path.join(os.environ["USERPROFILE"], "Desktop", "Valorant RPC.lnk")}" >nul 2>&1
del /q "{os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Valorant RPC.lnk")}" >nul 2>&1
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC" /f >nul 2>&1
cd ..
rd /s /q "{install_dir}"
"""
        with open(uninstaller_bat, "w", encoding="utf-8") as f:
            f.write(bat_content)

        try:
            reg_cmd = (
                f"reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC\" /v \"DisplayName\" /t REG_SZ /d \"Valorant RPC\" /f; "
                f"reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC\" /v \"UninstallString\" /t REG_SZ /d \"\\\"{uninstaller_bat}\\\"\" /f; "
                f"reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC\" /v \"DisplayVersion\" /t REG_SZ /d \"3.2.3\" /f; "
                f"reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC\" /v \"InstallLocation\" /t REG_SZ /d \"{install_dir}\" /f; "
                f"reg add \"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Valorant-RPC\" /v \"DisplayIcon\" /t REG_SZ /d \"{exe_path}\" /f"
            )
            subprocess.run(["powershell", "-Command", reg_cmd], capture_output=True)
        except Exception:
            pass

    def go_to_finished(self):
        self.current_step = 4
        self.render_layout()

    def show_finished_screen(self):
        title_lbl = tk.Label(self.container, text="Installation Completed!", font=("Segoe UI", 16, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title_lbl.pack(anchor="w", pady=(30, 5))

        desc_lbl = tk.Label(self.container, text="Valorant RPC has been successfully installed on your system.", font=("Segoe UI", 10), fg=TEXT_SECONDARY, bg=BG_COLOR)
        desc_lbl.pack(anchor="w", pady=(0, 30))

        cb_launch = tk.Checkbutton(self.container, text="Launch VALORANT RPC Now", variable=self.launch_after, font=("Segoe UI", 10, "bold"), fg=TEXT_COLOR, bg=BG_COLOR, selectcolor=BG_COLOR, bd=0, activebackground=BG_COLOR)
        cb_launch.pack(anchor="w", pady=10)

        footer = tk.Frame(self.container, bg=BG_COLOR)
        footer.pack(fill="x", side="bottom")

        finish_btn = tk.Button(footer, text="Finish", font=("Segoe UI", 9, "bold"), fg=BG_COLOR, bg=ACCENT_BLUE, activebackground=ACCENT_HOVER, relief="flat", bd=0, cursor="hand2", command=self.finish_installer, width=12)
        finish_btn.pack(side="right", ipady=4)

    def finish_installer(self):
        if self.launch_after.get():
            dest_exe = os.path.join(self.install_dir.get(), "valorant-rpc.exe")
            try:
                subprocess.Popen([dest_exe], cwd=self.install_dir.get())
            except Exception:
                pass
        self.root.destroy()

if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = Windows11InstallerApp(root)
    root.mainloop()