from datetime import datetime, timezone
from ..utilities.logging import Logger 
from ..localization.localization import Localizer
debug = Logger.debug

class Utilities:

    @staticmethod 
    def build_party_state(data):
        party_state = Localizer.get_localized_text("presences","party_states","solo")
        party_size_val = data.get("partySize", 1)
        party_accessibility = data.get("partyAccessibility", "CLOSED")
        max_party_size = data.get("maxPartySize", 5)
        
        if party_size_val > 1:
            party_state = Localizer.get_localized_text("presences","party_states","in_party")   
        elif party_accessibility == "OPEN":
            party_state = Localizer.get_localized_text("presences","party_states","open")

        party_size = [party_size_val, max_party_size] if party_size_val > 1 or party_accessibility == "OPEN" else None
        if party_size is not None:
            if party_size[0] == 0: 
                party_size[0] = 1
            if party_size[1] < 1:
                party_size[1] = 1
        return party_state, party_size 

    @staticmethod 
    def iso8601_to_epoch(time):
        if time == "0001.01.01-00.00.00":
            return None
        dt = datetime.strptime(time, "%Y.%m.%d-%H.%M.%S").replace(tzinfo=timezone.utc)
        return dt.timestamp()

    @staticmethod 
    def fetch_rank_data(client,content_data):
        try:
            mmr = client.fetch_mmr()["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][content_data["season"]["season_uuid"]]
        except:
            return "rank_0","Rank not found"
        rank_data = content_data["comp_tiers"][mmr["CompetitiveTier"]]
        rank_image = f"rank_{rank_data['id']}"
        rank_text = f"{rank_data['display_name_localized']} - {mmr['RankedRating']}{Localizer.get_localized_text('presences','leveling','ranked_rating')}" + (f" // #{mmr['LeaderboardRank']}" if mmr['LeaderboardRank'] != 0 else "") 

        return rank_image, rank_text
        
    @staticmethod 
    def fetch_map_data(coregame_data,content_data):
        map_id = coregame_data["MapID"]
        gmap = content_data["maps"].get(map_id)
        if gmap:
            return gmap["display_name"], gmap["display_name_localized"]
        return "", ""
 
    @staticmethod 
    def fetch_agent_data(uuid,content_data):
        agent = content_data["agents"].get(uuid)
        if agent:
            agent_image = f"agent_{agent['display_name'].lower().replace('/','')}"
            agent_name = agent['display_name_localized']
            return agent_image, agent_name
        return "rank_0","?"

    @staticmethod
    def fetch_mode_data(data, content_data):
        queue_id = data.get('queueId', '') if data else ''
        image = f"mode_{queue_id if queue_id in content_data.get('modes_with_icons', []) else 'discovery'}"
        mode_name = content_data.get('queue_aliases', {}).get(queue_id, "Custom") if queue_id in content_data.get("queue_aliases", {}).keys() else "Custom"
        mode_name = Utilities.localize_content_name(mode_name, "presences", "modes", queue_id)
        return image,mode_name

    @staticmethod 
    def get_content_preferences(client,pref,presence,player_data,coregame_data,content_data):
        if pref == Localizer.get_localized_text("config", "rank"):
            return Utilities.fetch_rank_data(client,content_data)
        if pref == Localizer.get_localized_text("config", "map"): 
            gmap = Utilities.fetch_map_data(coregame_data,content_data)
            return f"splash_{gmap[0].lower()}", gmap[1]
        if pref == Localizer.get_localized_text("config", "agent"): 
            return Utilities.fetch_agent_data(player_data["CharacterID"],content_data)

    @staticmethod
    def localize_content_name(default,*keys):
        localized = Localizer.get_localized_text(*keys)
        if localized is not None:
            return localized 
        return default

    @staticmethod 
    def get_join_state(client,config,presence=None):
        # Since we don't have a registered protocol handler on colinhartigan.github.io for this specific fork,
        # we can't reliably use the URL method for "Ask to Join" unless we host our own or use the Discord Game Invite system directly.
        # The Discord Game Invite system requires 'party_id' and 'join' secret to be set in the Rich Presence payload.
        # However, pypresence/discord-rpc doesn't support 'buttons' AND 'join' secret simultaneously well in some versions 
        # or behaves differently. Buttons are URL based. "Ask to Join" is a specific RPC event.

        # To enable "Ask to Join", we need to supply the 'join' secret in the rpc.update() call, NOT a button.
        # This function returns 'buttons', so it might be named confusingly for what we want.

        # But if the user wants the BUTTON "Ask to Join", that is a native Discord feature triggered by the presence of a join secret.
        # So we should return the join secret here (or rather, the caller should use it). 
        # But this function returns a list of buttons.

        # Let's see how 'menu_presences/default.py' uses this. It assigns to 'buttons='.
        # Discord RPC has 'buttons' (list of labels/urls) AND 'join' (secret string).
        # If we return None here, no buttons.
        
        # We will instead return a join secret if applicable? No, the caller expects buttons.
        # The user requested "Ask to Join" which typically means the native Discord "Ask to Join" button 
        # that appears on the profile overlay, not a rich presence interaction button.
        
        # To support native "Ask to Join", we need to pass `join=party_id` to rpc.update().
        # This function should probably return the join secret if appropriate, or we handle it in the caller.

        # However, let's look at the commented out code. It was using a custom URL scheme and a redirector service.
        # If we want NATIVE integration, we just need to pass the party ID as the secret.

        # For this task, "Ask to Join" usually refers to the native integration.
        # So we will modify this to return None for buttons (unless we want to keep them),
        # but the CALLER needs to know whether to add the 'join' secret.

        # Let's leave this returning buttons (as intended by original author) but maybe we can repurpose it 
        # or leave it as None if we are doing native join.
        
        # Actually, let's implementing the NATIVE 'join' secret logic in the callers (default.py, loadout.py)
        # using a helper here.
        
        return None

    @staticmethod
    def get_join_secret(data):
        # Native Discord "Ask to Join" requires a join secret.
        # We use the party ID as the secret.
        if data.get("partyAccessibility") == "CLOSED" or data.get("partyAccessibility") == "OPEN":
             # Only allow if party is not full?
            party_size = data.get("partySize", 1)
            max_party_size = data.get("maxPartySize", 5)
            if party_size < max_party_size:
                return data.get("partyId")
        return None
