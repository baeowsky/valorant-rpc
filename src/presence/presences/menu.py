from .menu_presences import (default,queue,custom_setup)

def presence(rpc,client=None,data=None,content_data=None,config=None):
    state_types = {
        "DEFAULT": default,
        "MATCHMAKING": queue,
        "CUSTOM_GAME_SETUP": custom_setup,
    }
    party_state = data.get('partyState', 'DEFAULT') if data else 'DEFAULT'
    if party_state in state_types.keys():
        state_types[party_state].presence(rpc,client=client,data=data,content_data=content_data,config=config)