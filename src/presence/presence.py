from pypresence import Presence as PyPresence
from pypresence.exceptions import InvalidPipe, DiscordNotFound, InvalidID, DiscordError
from pypresence.utils import get_ipc_path
from InquirerPy.utils import color_print
import time, sys, traceback, os, ctypes, asyncio, websockets, json, base64, ssl, struct

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

from ..utilities.config.app_config import Config
from ..content.content_loader import Loader
from ..localization.localization import Localizer
from .presences import (ingame,menu,startup,pregame)

kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
hWnd = kernel32.GetConsoleWindow()

class CustomPresence(PyPresence):
    async def handshake(self):
        ipc_path = get_ipc_path(self.pipe)
        if not ipc_path:
            raise DiscordNotFound

        await self.create_reader_writer(ipc_path)

        self.send_data(0, {"v": 1, "client_id": self.client_id})
        preamble = await self.sock_reader.read(8)
        if len(preamble) < 8:
            raise InvalidPipe
        code, length = struct.unpack("<ii", preamble)
        data = json.loads(await self.sock_reader.read(length))
        
        if "code" in data:
            if data["message"] == "Invalid Client ID":
                raise InvalidID
            raise DiscordError(data["code"], data["message"])
            
        if "data" in data and "user" in data["data"]:
            self.user = data["data"]["user"]
        elif "user" in data:
            self.user = data["user"]
        else:
            self.user = {}
            
        if self._events_on:
            self.sock_reader.feed_data = self.on_event

class Presence:

    def __init__(self,config):
        self.config = config
        self.client = None
        self.saved_locale = None
        try:
            self.rpc = CustomPresence(client_id=str(Localizer.get_config_value("client_id")))
            self.rpc.connect()
        except InvalidPipe as e:
            raise Exception(e)
        self.content_data = {}
    
    def main_loop(self):
        # async with websockets.connect(f'wss://riot:{self.client.lockfile["password"]}@localhost:{self.client.lockfile["port"]}', ssl=ssl_context) as websocket:
        #     await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')    # subscribing to presence event
            
        #     while True:
        #         response = await websocket.recv()
        #         if response != "":
        #             response = json.loads(response)
        #             if response[2]['data']['presences'][0]['puuid'] == self.client.puuid:
        #                 presence_data = json.loads(base64.b64decode((response[2]['data']['presences'][0]['private'])))
        #                 if presence_data is not None:
        #                     self.update_presence(presence_data["sessionLoopState"],presence_data)
        #                     # print(presence_data)
        #                 else:
        #                     os._exit(1)

        #                 if Localizer.locale != self.saved_locale:
        #                     self.saved_locale = Localizer.locale
        #                     self.content_data = Loader.load_all_content(self.client)


        while True:
            presence_data = self.client.fetch_presence()
            if presence_data is not None:
                match_data = presence_data.get("matchPresenceData", {})
                session_loop_state = match_data.get("sessionLoopState") or presence_data.get("sessionLoopState", "MENUS")
                self.update_presence(session_loop_state, presence_data)
                # print(presence_data)
            else:
                os._exit(1)

            if Localizer.locale != self.saved_locale:
                self.saved_locale = Localizer.locale
                self.content_data = Loader.load_all_content(self.client)
            time.sleep(Localizer.get_config_value("presence_refresh_interval"))


    def init_loop(self):
        try:
            self.content_data = Loader.load_all_content(self.client)
            color_print([("LimeGreen bold", Localizer.get_localized_text("prints","presence","presence_running"))])
            presence_data = self.client.fetch_presence()

            if presence_data is not None:
                match_data = presence_data.get("matchPresenceData", {})
                session_loop_state = match_data.get("sessionLoopState") or presence_data.get("sessionLoopState", "MENUS")
                self.update_presence(session_loop_state, presence_data)
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            #asyncio.ensure_future(self.main_loop())
            self.main_loop()

                    
        except Exception as e:
            user32.ShowWindow(hWnd, 1)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), (0x4|0x80|0x20|0x2|0x10|0x1|0x40|0x100))
            color_print([("Red bold",Localizer.get_localized_text("prints","errors","error_message"))])
            traceback.print_exc()
            input(Localizer.get_localized_text("prints","errors","exit"))
            os._exit(1)

    def update_presence(self,ptype,data=None):
        if not self.config.get("rpc_enabled", True):
            try:
                self.rpc.clear()
            except Exception:
                pass
            return

        presence_types = {
            "startup": startup,
            "MENUS": menu,
            "PREGAME": pregame,
            "INGAME": ingame,
        }
        if ptype in presence_types.keys():
            presence_types[ptype].presence(self.rpc,client=self.client,data=data,content_data=self.content_data,config=self.config)