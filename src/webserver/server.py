from flask import Flask, request, cli, jsonify, Response, send_from_directory
from flask_cors import CORS
import urllib3, logging, os, sys, threading, time
from pathlib import Path

urllib3.disable_warnings()

# Locate the assets/web folder for static assets
if getattr(sys, 'frozen', False):
    base_dir = Path(sys._MEIPASS)
else:
    base_dir = Path(__file__).resolve().parents[2]

web_dir = base_dir / 'assets' / 'web'

app = Flask(__name__, static_folder=str(web_dir), static_url_path='/static')
CORS(app)
cli.show_server_banner = lambda *_: None
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

client = None 
config = None
presence_obj = None

from ..utilities.config.app_config import Config
from ..utilities.processes import Processes
from ..utilities.filepath import Filepath
from ..localization.localization import Localizer

@app.route('/')
@app.route('/config')
def home():
    if app.static_folder and os.path.exists(os.path.join(app.static_folder, 'index.html')):
        return send_from_directory(app.static_folder, 'index.html')
    return 'VALORANT RPC Dashboard (static files not found)'

@app.route('/api/config', methods=['GET'])
def get_config():
    cfg = Config.fetch_config()
    return jsonify(cfg)

@app.route('/api/config', methods=['POST'])
def post_config():
    new_cfg = request.get_json()
    saved_cfg = Config.modify_config(new_cfg)
    if presence_obj is not None:
        presence_obj.config = saved_cfg
    return jsonify(saved_cfg)

@app.route('/api/status', methods=['GET'])
def get_status():
    is_val_running = Processes.are_processes_running()
    is_disc_running = False
    p_name = ""
    p_tag = ""
    p_region = ""
    game_info = {}
    d_user = {}

    if client is not None:
        p_region = getattr(client, 'region', "")
        p_name = getattr(client, 'player_name', "")
        p_tag = getattr(client, 'player_tag', "")
        
        try:
            presence = client.fetch_presence()
            if presence is not None:
                is_disc_running = True
                match_data = presence.get("matchPresenceData", {})
                
                state_loop = match_data.get("sessionLoopState") or presence.get("sessionLoopState", "MENUS")
                party_size = match_data.get("partySize", 1)
                max_party_size = match_data.get("maxPartySize", 5)
                
                game_info = {
                    "details": state_loop,
                    "state": f"Party ({party_size}/{max_party_size})",
                    "start_time": presence.get("time", time.time() if hasattr(presence, "time") else None)
                }
        except Exception:
            pass

    if presence_obj is not None and getattr(presence_obj, 'rpc', None) is not None:
        try:
            user_data = getattr(presence_obj.rpc, 'user', None)
            if user_data:
                u_id = user_data.get('id')
                u_avatar = user_data.get('avatar')
                u_banner = user_data.get('banner')
                u_banner_color = user_data.get('banner_color')
                u_accent = user_data.get('accent_color')
                
                avatar_url = ""
                if u_id:
                    if u_avatar:
                        avatar_url = f"https://cdn.discordapp.com/avatars/{u_id}/{u_avatar}.png?size=128"
                    else:
                        avatar_url = f"https://cdn.discordapp.com/embed/avatars/{int(u_id) % 5}.png"
                
                banner_url = ""
                if u_id and u_banner:
                    banner_url = f"https://cdn.discordapp.com/banners/{u_id}/{u_banner}.png?size=600"
                
                banner_color = u_banner_color
                if not banner_color and u_accent:
                    banner_color = f"#{u_accent:06x}"
                if not banner_color:
                    banner_color = "#5865f2"

                d_user = {
                    "username": user_data.get('username', 'Agent_Baeowsky'),
                    "discriminator": user_data.get('discriminator', '0'),
                    "avatar_url": avatar_url,
                    "banner_url": banner_url,
                    "banner_color": banner_color
                }
        except Exception:
            pass

    return jsonify({
        "is_valorant_running": is_val_running,
        "is_discord_running": is_disc_running or is_val_running,
        "player_name": p_name,
        "player_tag": p_tag,
        "region": p_region,
        "version": Config.fetch_config().get("version", "v3.2.3"),
        "game_info": game_info,
        "discord_user": d_user
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    log_path = Filepath.get_path(os.path.join(Filepath.get_appdata_folder(), 'rpc.log'))
    try:
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            clean_lines = [line.strip() for line in lines if line.strip()]
            return jsonify({"logs": clean_lines[-60:]})
        else:
            return jsonify({"logs": ["[SYSTEM] Log file 'rpc.log' not found yet."]})
    except Exception as e:
        return jsonify({"logs": [f"[SYSTEM] Error reading log file: {e}"]})

@app.route('/api/restart', methods=['POST'])
def api_restart():
    from ..utilities.systray import Systray
    threading.Thread(target=Systray.restart, daemon=True).start()
    return jsonify({"status": "restarting"})

@app.route('/valorant/request/<party_id>/<friend_id>')
def request_party(party_id,friend_id):
    region = request.args.get('region')
    if region == client.region:
        data = client.party_request_to_join(party_id,friend_id)
        for player in data["Requests"]:
            if client.puuid == player["RequestedBySubject"]:
                return "<script>window.onload = window.close();</script>"
        return data
    else:
        return f"you're not in the right region! (their region: {region}, your region: {client.region})"

@app.route('/valorant/join/<party_id>')
def join_party(party_id):
    region = request.args.get('region')
    if region == client.region:
        data = client.party_join(party_id)
        if "CurrentPartyID" in data.keys():
            return "<script>window.onload = window.close();</script>"
        return data

    return f"you're not in the right region! (their region: {region}, your region: {client.region})"


def start():
    app.run(port=4100)
