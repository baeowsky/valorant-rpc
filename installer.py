import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

BG_COLOR = "#0c0c0e"
CARD_BG = "#141418"
BORDER_COLOR = "#22222a"
TEXT_COLOR = "#ffffff"
TEXT_SECONDARY = "#a3a3a3"
ACCENT_COLOR = "#bcb1e7"
ACCENT_HOVER = "#9a8fd1"
ACCENT_GREEN = "#4ade80"

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VALORANT RPC Installer")
        self.root.geometry("540x380")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("TProgressbar", thickness=12, troughcolor=CARD_BG, background=ACCENT_COLOR, bordercolor=BORDER_COLOR)

        self.default_install_dir = os.path.join(os.environ["LOCALAPPDATA"], "Valorant-RPC")
        self.install_dir = tk.StringVar(value=self.default_install_dir)

        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_shortcut = tk.BooleanVar(value=True)
        self.launch_after = tk.BooleanVar(value=True)

        self.setup_welcome_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def setup_welcome_screen(self):
        self.clear_screen()

        title_lbl = tk.Label(self.root, text="VALORANT RPC", font=("Poppins", 20, "bold"), fg=ACCENT_COLOR, bg=BG_COLOR)
        title_lbl.pack(pady=(30, 5))

        subtitle_lbl = tk.Label(self.root, text="Setup Installer", font=("Poppins", 10, "medium"), fg=TEXT_SECONDARY, bg=BG_COLOR)
        subtitle_lbl.pack(pady=(0, 20))

        info_frame = tk.Frame(self.root, bg=CARD_BG, highlightbackground=BORDER_COLOR, highlightthickness=1)
        info_frame.pack(padx=30, pady=10, fill="x")

        path_lbl_title = tk.Label(info_frame, text="Select Installation Directory:", font=("Poppins", 9, "bold"), fg=TEXT_COLOR, bg=CARD_BG)
        path_lbl_title.pack(anchor="w", padx=15, pady=(15, 5))

        path_entry_frame = tk.Frame(info_frame, bg=CARD_BG)
        path_entry_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.path_entry = tk.Entry(path_entry_frame, textvariable=self.install_dir, font=("Consolas", 9), fg=TEXT_COLOR, bg=BG_COLOR, insertbackground=TEXT_COLOR, highlightbackground=BORDER_COLOR, highlightthickness=1, bd=0)
        self.path_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))

        browse_btn = tk.Button(path_entry_frame, text="Browse...", font=("Poppins", 8, "bold"), fg=BG_COLOR, bg=ACCENT_COLOR, activebackground=ACCENT_HOVER, activeforeground=BG_COLOR, bd=0, cursor="hand2", command=self.browse_folder)
        browse_btn.pack(side="right", ipadx=10, ipady=4)

        opts_frame = tk.Frame(self.root, bg=BG_COLOR)
        opts_frame.pack(fill="x", padx=30, pady=10)

        cb1 = tk.Checkbutton(opts_frame, text="Create Desktop Shortcut", variable=self.create_desktop_shortcut, font=("Poppins", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR, selectcolor=BG_COLOR, bd=0)
        cb1.pack(anchor="w")

        cb2 = tk.Checkbutton(opts_frame, text="Create Start Menu Shortcut", variable=self.create_start_shortcut, font=("Poppins", 9), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR, selectcolor=BG_COLOR, bd=0)
        cb2.pack(anchor="w")

        footer_frame = tk.Frame(self.root, bg=BG_COLOR)
        footer_frame.pack(side="bottom", fill="x", padx=30, pady=20)

        cancel_btn = tk.Button(footer_frame, text="Cancel", font=("Poppins", 9, "bold"), fg=TEXT_SECONDARY, bg=BG_COLOR, activebackground=BG_COLOR, activeforeground=TEXT_COLOR, bd=0, cursor="hand2", command=self.root.quit)
        cancel_btn.pack(side="left")

        install_btn = tk.Button(footer_frame, text="Install Now", font=("Poppins", 9, "bold"), fg=BG_COLOR, bg=ACCENT_COLOR, activebackground=ACCENT_HOVER, activeforeground=BG_COLOR, bd=0, cursor="hand2", command=self.start_installation)
        install_btn.pack(side="right", ipadx=20, ipady=6)

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Install Folder")
        if selected:
            normalized = os.path.normpath(selected)
            if not normalized.endswith("Valorant-RPC"):
                normalized = os.path.join(normalized, "Valorant-RPC")
            self.install_dir.set(normalized)

    def start_installation(self):
        self.clear_screen()

        title_lbl = tk.Label(self.root, text="Installing VALORANT RPC...", font=("Poppins", 16, "bold"), fg=TEXT_COLOR, bg=BG_COLOR)
        title_lbl.pack(pady=(40, 5))

        self.log_lbl = tk.Label(self.root, text="Preparing installation folder...", font=("Poppins", 9), fg=TEXT_SECONDARY, bg=BG_COLOR)
        self.log_lbl.pack(pady=(0, 20))

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.progress["maximum"] = 100
        self.progress["value"] = 5

        self.root.after(100, self.perform_installation)

    def perform_installation(self):
        dest_dir = self.install_dir.get()

        try:
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            self.progress["value"] = 20
            self.log_lbl.config(text="Extracting executable files...")
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
            self.log_lbl.config(text="Creating shortcut items...")
            self.root.update()

            if self.create_desktop_shortcut.get():
                desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
                shortcut_path = os.path.join(desktop_dir, "Valorant RPC.lnk")
                self.create_win_shortcut(dest_exe, shortcut_path, dest_dir)

            if self.create_start_shortcut.get():
                start_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
                shortcut_path = os.path.join(start_dir, "Valorant RPC.lnk")
                self.create_win_shortcut(dest_exe, shortcut_path, dest_dir)

            self.progress["value"] = 80
            self.log_lbl.config(text="Registering uninstaller information...")
            self.root.update()

            self.register_uninstaller(dest_dir, dest_exe)

            self.progress["value"] = 100
            self.log_lbl.config(text="Installation successful!")
            self.root.update()

            self.root.after(500, self.setup_success_screen)

        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to complete installation:\n{e}")
            self.setup_welcome_screen()

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

    def setup_success_screen(self):
        self.clear_screen()

        success_lbl = tk.Label(self.root, text="Installation Completed!", font=("Poppins", 18, "bold"), fg=ACCENT_GREEN, bg=BG_COLOR)
        success_lbl.pack(pady=(40, 5))

        desc_lbl = tk.Label(self.root, text="Valorant RPC has been successfully installed.", font=("Poppins", 10), fg=TEXT_SECONDARY, bg=BG_COLOR)
        desc_lbl.pack(pady=(0, 25))

        cb_launch = tk.Checkbutton(self.root, text="Launch VALORANT RPC Now", variable=self.launch_after, font=("Poppins", 10, "bold"), fg=TEXT_COLOR, bg=BG_COLOR, activebackground=BG_COLOR, activeforeground=ACCENT_COLOR, selectcolor=BG_COLOR, bd=0)
        cb_launch.pack(pady=20)

        footer_frame = tk.Frame(self.root, bg=BG_COLOR)
        footer_frame.pack(side="bottom", fill="x", padx=30, pady=30)

        finish_btn = tk.Button(footer_frame, text="Finish", font=("Poppins", 10, "bold"), fg=BG_COLOR, bg=ACCENT_COLOR, activebackground=ACCENT_HOVER, activeforeground=BG_COLOR, bd=0, cursor="hand2", command=self.finish_installer)
        finish_btn.pack(side="right", ipadx=30, ipady=6)

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
    app = InstallerApp(root)
    root.mainloop()