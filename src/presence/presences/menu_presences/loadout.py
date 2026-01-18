from ....localization.localization import Localizer
from ...presence_utilities import Utilities

def presence(rpc,client=None,data=None,content_data=None,config=None):
    if data is None:
        return

    # Check if skin showcase is enabled
    if not config["presences"]["menu"]["show_equipped_skin"]:
        from .default import presence as default_presence
        default_presence(rpc, client, data, content_data, config)
        return

    party_state, party_size = Utilities.build_party_state(data)
    buttons = Utilities.get_join_state(client, config, data)

    # Fetch loadout
    try:
        loadout = client.fetch_player_loadout()
        weapon_pref = config["presences"]["menu"]["skin_weapon_preference"].lower() # e.g. "vandal"
        
        # Find weapon ID by name (rough search)
        # 9c82e19d-4575-0200-1a81-3eacf00cf872 -> Vandal
        # ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a -> Phantom
        # This mapping should ideally be in content_loader but hardcoding common ones for now or searching
        
        target_weapon_id = None
        target_weapon_name = ""

        # Simple mapping for popular weapons to UUIDs
        # We could also search content_data["skins"] if we stored weapon data there, but skins are flat list usually
        # Let's try to map the preference string to a uuid using the weapons endpoint if we had it, 
        # but since we don't have weapons in content_data yet, let's use known IDs or just iterate loadout
        
        # for now, let's just grab the FIRST gun in the loadout that isn't a knife/pistol if possible, 
        # or just fallback to Vandal/Phantom if found.
        
        # Actually, let's just stick to the plan: fetch loadout and finding the skin.
        # We need the weapon map. 
        # Since I didn't add weapons to content_loader, let's add a quick lookup here or just use the skin data directly if we can link it.
        # Loadout gives us: Guns: [{ID:..., SkinID:..., ...}]
        
        # Let's iterate and look for the preferred weapon name based on UUID if we had it, 
        # but we lack weapon UUID->Name in content_data (only have maps/agents/skins).
        # We can try to identify by checking if the Skin's name contains "Vandal" or "Phantom" etc in the future,
        # but for now let's just look at the first primary weapon.
        
        skin_name = "Unknown Skin"
        # UUIDs for Vandal and Phantom
        vandal_id = "9c82e19d-4575-0200-1a81-3eacf00cf872"
        phantom_id = "ee8e8d15-496b-07ac-e5f6-8fae5d4c7b1a"
        
        weapon_id = vandal_id if "vandal" in weapon_pref else phantom_id
        if "phantom" in weapon_pref: weapon_id = phantom_id # logic fix
        
        equipped_skin_id = None
        for gun in loadout["Guns"]:
            if gun["ID"] == weapon_id:
                equipped_skin_id = gun["SkinID"]
                break
        
        # print(f"DEBUG: Found skin ID {equipped_skin_id} for weapon preference {weapon_pref}")

        
        if equipped_skin_id and equipped_skin_id in content_data["skins"]:
            skin_name = content_data["skins"][equipped_skin_id]["display_name_localized"]
        else:
            # Fallback if preferred weapon not found or skin not in list
             skin_name = f"Unknown {weapon_pref.capitalize()} Skin"

        large_text = f"{Localizer.get_localized_text('presences','leveling','level')} {data.get('playerPresenceData', {}).get('accountLevel', '?')}"
        details = f"{Localizer.get_localized_text('presences','client_states','menu')} - {skin_name}"

        join_secret = Utilities.get_join_secret(data)

        rpc.update(
            state=party_state,
            details=details,
            large_image="game_icon", # We could try to show skin image if we had assets, but stick to icon
            large_text=large_text,
            small_image="rank_0", # Default or rank
            small_text="Menu",
            party_size=party_size,
            party_id=data.get("partyId", ""),
            join=join_secret, # Add join secret for native "Ask to Join"
            buttons=buttons
        )

    except Exception as e:
        # Fallback to default if loadout fetch fails
        print(f"DEBUG: Loadout presence failed: {e}")
        from .default import presence as default_presence
        default_presence(rpc, client, data, content_data, config)
