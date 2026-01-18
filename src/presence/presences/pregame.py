from ..presence_utilities import Utilities
from ...localization.localization import Localizer
from valclient.exceptions import PhaseError
import time

def presence(rpc,client=None,data=None,content_data=None,config=None):
    party_state,party_size = Utilities.build_party_state(data)
    
    try:
        pregame = client.pregame_fetch_player()
        match_id = pregame["MatchID"]
        pregame_data = client.pregame_fetch_match(match_id)
        puuid = client.puuid

        pregame_player_data = {}
        for player in pregame_data["AllyTeam"]["Players"]:
            if player["Subject"] == puuid:
                pregame_player_data = player

        pregame_end_time = (pregame_data['PhaseTimeRemainingNS'] // 1000000000) + time.time()

        agent_image, agent_name = Utilities.fetch_agent_data(pregame_player_data["CharacterID"],content_data)
        select_state = Localizer.get_localized_text("presences","pregame","locked") if pregame_player_data["CharacterSelectionState"] == "locked" else Localizer.get_localized_text("presences","pregame","selecting")
        small_image, mode_name = Utilities.fetch_mode_data(data,content_data)

        # Build team composition string
        team_agents = []
        for player in pregame_data["AllyTeam"]["Players"]:
            character_id = player["CharacterID"]
            _, char_name = Utilities.fetch_agent_data(character_id, content_data)
            if char_name != "?":
                team_agents.append(char_name)
        
        team_comp_str = ", ".join(team_agents)
        if not team_comp_str:
            team_comp_str = "Selecting..."

        # Cycle functionality could require keeping state, but for now let's just show the list or truncate
        # To strictly "cycle", we'd need a global timer or similar in the class instance. 
        # Given this is a stateless function call, let's just display all or truncate.
        # Alternatively, use time.time() to key into the list.
        
        if len(team_agents) > 0:
             # Cycle through team agents every 2 seconds
            idx = int(time.time() / 2) % len(team_agents)
            displayed_teammate = team_agents[idx]
            team_details = f"Team: {team_comp_str}" # Show full list if fitting
            # If too long, maybe cycle? RPC limit is 128 chars usually.
        else:
            team_details = "Team: Selecting..."

        rpc.update(
            state=team_details, # Display team in state
            details=f"{Localizer.get_localized_text('presences','client_states','pregame')} - {mode_name}",
            end=pregame_end_time,
            large_image=agent_image,
            large_text=f"{select_state} - {agent_name}",
            small_image=small_image,
            small_text=mode_name,
            party_size=party_size,
            party_id=data["partyId"],
        )
    except PhaseError:
        pass