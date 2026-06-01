import webview
import sys
import os

class GUI:
    window = None

    @staticmethod
    def start_gui():
        GUI.window = webview.create_window(
            title='VALORANT RPC Dashboard',
            url='http://127.0.0.1:4100/config',
            width=1120,
            height=780,
            resizable=True
        )
        
        GUI.window.events.closing += GUI.on_closing
        
        webview.start()

    @staticmethod
    def on_closing():
        if GUI.window is not None:
            GUI.window.hide()
        return False

    @staticmethod
    def show():
        if GUI.window is not None:
            GUI.window.show()