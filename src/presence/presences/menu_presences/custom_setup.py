from ...presence_utilities import Utilities
from ....localization.localization import Localizer

from .away import presence as away

def presence(rpc,client=None,data=None,content_data=None,config=None):
    if data is None:
        return
    
    is_afk = data.get("isIdle", False)
    if is_afk:
        away(rpc,client,data,content_data,config)  
   
    else: 
        party_state,party_size = Utilities.build_party_state(data)
        data["MapID"] = data.get("matchMap", "")
        game_map,map_name = Utilities.fetch_map_data(data,content_data)
        custom_game_team = data.get("customGameTeam", "")
        team_image_aliases = content_data.get("team_image_aliases", {}) if content_data else {}
        team_aliases = content_data.get("team_aliases", {}) if content_data else {}
        team = team_image_aliases.get(custom_game_team, "game_icon_white")
        team_patched = team_aliases.get(custom_game_team) if custom_game_team in team_aliases.keys() else None
        team_patched = Utilities.localize_content_name(team_patched, "presences", "team_names", custom_game_team)
        buttons = Utilities.get_join_state(client,config,data)

        rpc.update(
            state=party_state,
            details=Localizer.get_localized_text("presences","client_states","custom_setup"),
            large_image=f"splash_{game_map.lower()}" if game_map else "game_icon",
            large_text=map_name if map_name else "Custom",
            small_image=team,
            small_text=team_patched,
            party_size=party_size,
            party_id=data.get("partyId", ""),
            buttons=buttons
        )