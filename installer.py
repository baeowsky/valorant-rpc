import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

WIN_BG = "#f0f0f0"
WIN_WHITE = "#ffffff"
WIN_BORDER = "#d0d0d0"
TEXT_COLOR = "#000000"
TEXT_SECONDARY = "#505050"
ACCENT_BLUE = "#0a5bc6"
SIDEBAR_BLUE = "#4a3c9e"

class WindowsInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Setup - VALORANT RPC")
        self.root.geometry("500x360")
        self.root.configure(bg=WIN_BG)
        self.root.resizable(False, False)

        self.style = ttk.Style()
        try:
            self.style.theme_use('vista')
        except Exception:
            try:
                self.style.theme_use('winnative')
            except Exception:
                pass

        self.default_install_dir = os.path.join(os.environ["LOCALAPPDATA"], "Valorant-RPC")
        self.install_dir = tk.StringVar(value=self.default_install_dir)

        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_start_shortcut = tk.BooleanVar(value=True)
        self.launch_after = tk.BooleanVar(value=True)
        
        self.current_step = 1 # 1: Welcome, 2: Directory, 3: Ready, 4: Installing, 5: Finished

        self.render_layout()

    def render_layout(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.bottom_frame = tk.Frame(self.root, bg=WIN_BG, height=48)
        self.bottom_frame.pack(side="bottom", fill="x")

        sep = tk.Frame(self.root, bg=WIN_BORDER, height=1)
        sep.pack(side="bottom", fill="x")

        self.main_area = tk.Frame(self.root, bg=WIN_BG)
        self.main_area.pack(side="top", fill="both", expand=True)

        if self.current_step == 1:
            self.show_welcome_screen()
        elif self.current_step == 2:
            self.show_directory_screen()
        elif self.current_step == 3:
            self.show_ready_screen()
        elif self.current_step == 4:
            self.show_installing_screen()
        elif self.current_step == 5:
            self.show_finished_screen()

    def add_bottom_buttons(self, back_enabled=True, next_enabled=True, next_text="Next >", cancel_enabled=True, next_cmd=None):
        cancel_btn = tk.Button(self.bottom_frame, text="Cancel", font=("Tahoma", 8), command=self.root.quit, state="normal" if cancel_enabled else "disabled", width=10)
        cancel_btn.pack(side="right", padx=(10, 15), pady=12)

        next_cmd = next_cmd if next_cmd else self.go_next
        next_btn = tk.Button(self.bottom_frame, text=next_text, font=("Tahoma", 8), command=next_cmd, state="normal" if next_enabled else "disabled", width=10)
        next_btn.pack(side="right", padx=2, pady=12)

        back_btn = tk.Button(self.bottom_frame, text="< Back", font=("Tahoma", 8), command=self.go_back, state="normal" if back_enabled else "disabled", width=10)
        back_btn.pack(side="right", padx=2, pady=12)

    def go_next(self):
        self.current_step += 1
        self.render_layout()

    def go_back(self):
        self.current_step -= 1
        self.render_layout()

    def show_welcome_screen(self):
        sidebar = tk.Frame(self.main_area, bg=SIDEBAR_BLUE, width=160)
        sidebar.pack(side="left", fill="y")
        
        logo_lbl = tk.Label(sidebar, text="VALORANT\nRPC", font=("Tahoma", 16, "bold"), fg=WIN_WHITE, bg=SIDEBAR_BLUE)
        logo_lbl.pack(pady=40)

        content = tk.Frame(self.main_area, bg=WIN_WHITE)
        content.pack(side="right", fill="both", expand=True)

        title = tk.Label(content, text="Welcome to the Valorant RPC\nSetup Wizard", font=("Tahoma", 12, "bold"), justify="left", fg=TEXT_COLOR, bg=WIN_WHITE)
        title.pack(anchor="w", padx=20, pady=(30, 15))

        desc = tk.Label(content, text="This will install Valorant Discord Rich Presence on your computer.\n\nIt is recommended that you close all other applications before continuing.\n\nClick Next to continue, or Cancel to exit Setup.", font=("Tahoma", 8), justify="left", fg=TEXT_SECONDARY, bg=WIN_WHITE, wraplength=280)
        desc.pack(anchor="w", padx=20, pady=10)

        self.add_bottom_buttons(back_enabled=False)

    def show_directory_screen(self):
        header = tk.Frame(self.main_area, bg=WIN_WHITE, height=58, highlightbackground=WIN_BORDER, highlightthickness=1)
        header.pack(side="top", fill="x")

        header_title = tk.Label(header, text="Select Destination Location", font=("Tahoma", 8, "bold"), fg=TEXT_COLOR, bg=WIN_WHITE)
        header_title.pack(anchor="w", padx=15, pady=(8, 2))

        header_sub = tk.Label(header, text="Where should Valorant RPC be installed?", font=("Tahoma", 8), fg=TEXT_SECONDARY, bg=WIN_WHITE)
        header_sub.pack(anchor="w", padx=25)

        body = tk.Frame(self.main_area, bg=WIN_BG)
        body.pack(fill="both", expand=True, padx=25, pady=15)

        lbl = tk.Label(body, text="Setup will install Valorant RPC into the following folder.\nTo continue, click Next. If you would like to select a different folder, click Browse.", font=("Tahoma", 8), justify="left", fg=TEXT_COLOR, bg=WIN_BG, wraplength=450)
        lbl.pack(anchor="w", pady=(0, 15))

        picker_frame = tk.Frame(body, bg=WIN_BG)
        picker_frame.pack(fill="x", pady=5)

        path_entry = tk.Entry(picker_frame, textvariable=self.install_dir, font=("Tahoma", 8), bg=WIN_WHITE, highlightbackground=WIN_BORDER, highlightthickness=1, bd=0)
        path_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 10))

        browse_btn = tk.Button(picker_frame, text="Browse...", font=("Tahoma", 8), command=self.browse_folder, width=10)
        browse_btn.pack(side="right")

        cb_frame = tk.Frame(body, bg=WIN_BG)
        cb_frame.pack(fill="x", pady=(15, 0))

        cb1 = tk.Checkbutton(cb_frame, text="Create a desktop shortcut", variable=self.create_desktop_shortcut, font=("Tahoma", 8), bg=WIN_BG, activebackground=WIN_BG)
        cb1.pack(anchor="w", pady=2)

        cb2 = tk.Checkbutton(cb_frame, text="Create a Start Menu shortcut", variable=self.create_start_shortcut, font=("Tahoma", 8), bg=WIN_BG, activebackground=WIN_BG)
        cb2.pack(anchor="w", pady=2)

        self.add_bottom_buttons()

    def browse_folder(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Install Folder")
        if selected:
            normalized = os.path.normpath(selected)
            if not normalized.endswith("Valorant-RPC"):
                normalized = os.path.join(normalized, "Valorant-RPC")
            self.install_dir.set(normalized)

    def show_ready_screen(self):
        header = tk.Frame(self.main_area, bg=WIN_WHITE, height=58, highlightbackground=WIN_BORDER, highlightthickness=1)
        header.pack(side="top", fill="x")

        header_title = tk.Label(header, text="Ready to Install", font=("Tahoma", 8, "bold"), fg=TEXT_COLOR, bg=WIN_WHITE)
        header_title.pack(anchor="w", padx=15, pady=(8, 2))

        header_sub = tk.Label(header, text="Setup is now ready to begin installing Valorant RPC on your computer.", font=("Tahoma", 8), fg=TEXT_SECONDARY, bg=WIN_WHITE)
        header_sub.pack(anchor="w", padx=25)

        body = tk.Frame(self.main_area, bg=WIN_BG)
        body.pack(fill="both", expand=True, padx=25, pady=15)

        lbl = tk.Label(body, text="Click Install to continue with the installation, or click Back if you want to review or change any settings.", font=("Tahoma", 8), justify="left", fg=TEXT_COLOR, bg=WIN_BG, wraplength=450)
        lbl.pack(anchor="w", pady=(0, 10))

        recap_box = tk.Text(body, font=("Tahoma", 8), bg=WIN_WHITE, highlightbackground=WIN_BORDER, highlightthickness=1, bd=0, height=8)
        recap_box.pack(fill="both", expand=True)

        recap_text = (
            "Destination location:\n"
            f"      {self.install_dir.get()}\n\n"
            "Shortcut items:\n"
        )
        if self.create_desktop_shortcut.get():
            recap_text += "      - Create a desktop shortcut\n"
        if self.create_start_shortcut.get():
            recap_text += "      - Create a Start Menu shortcut\n"

        recap_box.insert("1.0", recap_text)
        recap_box.config(state="disabled")

        self.add_bottom_buttons(next_text="Install", next_cmd=self.start_installation)

    def show_installing_screen(self):
        header = tk.Frame(self.main_area, bg=WIN_WHITE, height=58, highlightbackground=WIN_BORDER, highlightthickness=1)
        header.pack(side="top", fill="x")

        header_title = tk.Label(header, text="Installing", font=("Tahoma", 8, "bold"), fg=TEXT_COLOR, bg=WIN_WHITE)
        header_title.pack(anchor="w", padx=15, pady=(8, 2))

        header_sub = tk.Label(header, text="Please wait while Setup installs Valorant RPC on your computer.", font=("Tahoma", 8), fg=TEXT_SECONDARY, bg=WIN_WHITE)
        header_sub.pack(anchor="w", padx=25)

        body = tk.Frame(self.main_area, bg=WIN_BG)
        body.pack(fill="both", expand=True, padx=25, pady=25)

        self.log_lbl = tk.Label(body, text="Extracting files...", font=("Tahoma", 8), fg=TEXT_COLOR, bg=WIN_BG)
        self.log_lbl.pack(anchor="w", pady=(0, 5))

        self.progress = ttk.Progressbar(body, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)
        self.progress["maximum"] = 100
        self.progress["value"] = 5

        self.add_bottom_buttons(back_enabled=False, next_enabled=False, cancel_enabled=False)

    def start_installation(self):
        self.current_step = 4
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
                raise FileNotFoundError(f"Source file not found at: {src_exe}")

            dest_exe = os.path.join(dest_dir, "valorant-rpc.exe")

            shutil.copy2(src_exe, dest_exe)
            self.progress["value"] = 60
            self.log_lbl.config(text="Creating program shortcuts...")
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
            messagebox.showerror("Setup Error", f"An error occurred during installation:\n{e}")
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
        self.current_step = 5
        self.render_layout()

    def show_finished_screen(self):
        sidebar = tk.Frame(self.main_area, bg=SIDEBAR_BLUE, width=160)
        sidebar.pack(side="left", fill="y")

        logo_lbl = tk.Label(sidebar, text="VALORANT\nRPC", font=("Tahoma", 16, "bold"), fg=WIN_WHITE, bg=SIDEBAR_BLUE)
        logo_lbl.pack(pady=40)

        content = tk.Frame(self.main_area, bg=WIN_WHITE)
        content.pack(side="right", fill="both", expand=True)

        title = tk.Label(content, text="Completing the Valorant RPC\nSetup Wizard", font=("Tahoma", 12, "bold"), justify="left", fg=TEXT_COLOR, bg=WIN_WHITE)
        title.pack(anchor="w", padx=20, pady=(30, 15))

        desc = tk.Label(content, text="Setup has finished installing Valorant RPC on your computer. The application may be launched by selecting the installed shortcuts.\n\nClick Finish to exit Setup.", font=("Tahoma", 8), justify="left", fg=TEXT_SECONDARY, bg=WIN_WHITE, wraplength=280)
        desc.pack(anchor="w", padx=20, pady=5)

        cb_launch = tk.Checkbutton(content, text="Launch VALORANT RPC Now", variable=self.launch_after, font=("Tahoma", 8, "bold"), fg=TEXT_COLOR, bg=WIN_WHITE, selectcolor=WIN_WHITE, bd=0, activebackground=WIN_WHITE)
        cb_launch.pack(anchor="w", padx=20, pady=15)

        self.add_bottom_buttons(back_enabled=False, next_text="Finish", next_cmd=self.finish_installer, cancel_enabled=False)

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
    app = WindowsInstallerApp(root)
    root.mainloop()