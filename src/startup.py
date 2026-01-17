from InquirerPy.utils import color_print
import sys, psutil, time, cursor, valclient, ctypes, traceback, os, subprocess

from .utilities.killable_thread import Thread
from .utilities.config.app_config import Config
from .utilities.config.modify_config import Config_Editor
from .utilities.processes import Processes
from .utilities.rcs import Riot_Client_Services
from .utilities.systray import Systray
from .utilities.version_checker import Checker
from .utilities.logging import Logger
from .utilities.program_data import Program_Data

from .localization.localization import Localizer

from .presence.presence import Presence

from .webserver import server

# weird console window management stuff
kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
hWnd = kernel32.GetConsoleWindow()
kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x00|0x100)) #disable inputs to console
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7) #allow for ANSI sequences

class Startup:
    def __init__(self):
        if not Processes.is_program_already_running():
            cursor.hide()
            Logger.create_logger()
            Program_Data.update_file_location()

            self.config = Config.fetch_config()
            if "locale" in self.config.keys():
                if self.config["locale"][0] == "":
                    config = Localizer.prompt_locale(self.config)
                    Config.modify_config(config)
                    Systray.restart()

            self.installs = Program_Data.fetch_installs()
            Localizer.set_locale(self.config)
            self.config = Config.check_config()
            Localizer.config = self.config

            Logger.debug(self.config)
            self.client = None                

            if Localizer.get_config_value("region",0) == "": # try to autodetect region on first launch
                self.check_region() 

            ctypes.windll.kernel32.SetConsoleTitleW(f"valorant-rpc {Localizer.get_config_value('version')}") 

            color_print([("Red", Localizer.get_localized_text("prints","startup","wait_for_rpc"))])
            try:
                self.presence = Presence(self.config)
                Startup.clear_line()
            except Exception as e:
                traceback.print_exc()
                color_print([("Cyan",f"{Localizer.get_localized_text('prints','startup','discord_not_detected')} ({e})")])
                if not Processes.are_processes_running():
                    color_print([("Red", Localizer.get_localized_text("prints","startup","starting_valorant"))])
                    self.start_game()
                    os._exit(1)

            self.run()


    def run(self):
        self.presence.update_presence("startup")
        Checker.check_version(self.config)
        if not Processes.are_processes_running():
            color_print([("Red", Localizer.get_localized_text("prints","startup","starting_valorant"))])
            self.start_game()
        
        self.setup_client()

        self.systray = Systray(self.client,self.config)
        self.dispatch_systray()
        
        if self.client.fetch_presence() is None:
            self.wait_for_presence()

        self.check_run_cli()
        self.dispatch_presence()
        self.dispatch_webserver() 
        
        color_print([("LimeGreen",f"{Localizer.get_localized_text('prints','startup','startup_successful')}\n")])
        time.sleep(5)
        user32.ShowWindow(hWnd, 0) #hide window

        self.systray_thread.join()
        self.presence_thread.stop()
        

    def dispatch_webserver(self):
        server.client = self.client 
        server.config = self.config
        self.webserver_thread = Thread(target=server.start,daemon=True)
        self.webserver_thread.start()
        
    def dispatch_presence(self):
        self.presence_thread = Thread(target=self.presence.init_loop,daemon=True)
        self.presence_thread.start()

    def dispatch_systray(self):
        self.systray_thread = Thread(target=self.systray.run)
        self.systray_thread.start()

    def setup_client(self):
        try:
            self.client = valclient.Client(region=Localizer.get_config_value("region",0))
            self.client.activate()
            self.presence.client = self.client
        except:
            self.check_region()

    def wait_for_presence(self):
        presence_timeout = Localizer.get_config_value("startup","presence_timeout")
        presence_timer = 0 
        print()
        while self.client.fetch_presence() is None:
            Startup.clear_line()
            color_print([("Cyan", "["),("White",f"{presence_timer}"),("Cyan", f"] {Localizer.get_localized_text('prints','startup','waiting_for_presence')}")])
            presence_timer += 1
            # Check if we've exceeded the timeout for Discord presence detection
            if presence_timer >= presence_timeout:
                print()
                color_print([("Red", f"Timed out waiting for Discord Presence after {presence_timeout} seconds.")])
                if hasattr(self, 'systray'):
                    self.systray.exit()
                # Wait for user input so they can read the error message before the window closes
                input("Press Enter to exit...")
                os._exit(1)
            time.sleep(1)
        Startup.clear_line()
        Startup.clear_line()

    def start_game(self):
        launch_timeout = Localizer.get_config_value("startup","game_launch_timeout")
        launch_timer = 0
        
        try:
            rcs_path = Riot_Client_Services.get_rcs_path()
            if rcs_path:
                Logger.debug(f"Launching Valorant via RiotClientServices executable at {rcs_path}...")
                subprocess.Popen([rcs_path, "--launch-product=valorant", "--launch-patchline=live"])
            else:
                Logger.debug("Attempting to launch Valorant via riotclient URI...")
                # os.startfile is the equivalent of double-clicking or running "start ..." in cmd
                # but handles the system association directly.
                # Using the URI scheme is more robust than finding the executable path manually.
                os.startfile("riotclient://launch-product?product=valorant&patchline=live")
        except Exception as e:
            color_print([("Red", f"Failed to launch Valorant: {e}")])
            Logger.debug(f"Failed to launch Valorant: {e}")

        print()
        while not Processes.are_processes_running():
            Startup.clear_line()
            color_print([("Cyan", "["),("White",f"{launch_timer}"),("Cyan", f"] {Localizer.get_localized_text('prints','startup','waiting_for_valorant')}")])
            launch_timer += 1
            if launch_timer >= launch_timeout:
                print()
                color_print([("Red", f"Timed out waiting for Valorant to start after {launch_timeout} seconds.")])
                color_print([("Yellow", "Please ensure Valorant is installed and can be launched manually.")])
                if hasattr(self, 'systray'):
                    self.systray.exit()
                input("Press Enter to exit...")
                os._exit(1)
            time.sleep(1)
        Startup.clear_line()

    def check_run_cli(self):
        if Localizer.get_config_value("startup","auto_launch_skincli"):
            skincli_path = self.installs.get("valorant-skin-cli")
            if skincli_path is not None:
                subprocess.Popen(f"start {skincli_path}", shell=True)

    def check_region(self):
        color_print([("Red bold",Localizer.get_localized_text("prints","startup","autodetect_region"))])
        client = valclient.Client(region="na")
        client.activate()
        sessions = client.riotclient_session_fetch_sessions()
        for _,session in sessions.items():
            if session["productId"] == "valorant":
                launch_args = session["launchConfiguration"]["arguments"]
                for arg in launch_args:
                    if "-ares-deployment" in arg:
                        region = arg.replace("-ares-deployment=","")
                        self.config[Localizer.get_config_key("region")][0] = region
                        Config.modify_config(self.config)
                        color_print([("LimeGreen",f"{Localizer.get_localized_text('prints','startup','autodetected_region')} {Localizer.get_config_value('region',0)}")])
                        time.sleep(5)
                        Systray.restart()

    @staticmethod
    def clear_line():
        sys.stdout.write("\033[F") # move cursor up one line
        sys.stdout.write("\r\033[K")