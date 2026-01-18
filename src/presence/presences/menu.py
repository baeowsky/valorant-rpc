from .menu_presences import (default,queue,custom_setup,loadout)

def presence(rpc,client=None,data=None,content_data=None,config=None):
    state_types = {
        "DEFAULT": loadout, # Replaced default with loadout (which falls back to default if disabled)
        "MATCHMAKING": queue,
        "CUSTOM_GAME_SETUP": custom_setup,
    }
    party_data = data.get('partyPresenceData', {}) if data else {}
    match_data = data.get('matchPresenceData', {}) if data else {}
    party_state = party_data.get('partyState') or match_data.get('partyState') or data.get('partyState', 'DEFAULT') if data else 'DEFAULT'
    
    if party_state in state_types.keys():
        state_types[party_state].presence(rpc,client=client,data=data,content_data=content_data,config=config)