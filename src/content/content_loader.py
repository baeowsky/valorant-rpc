import requests
import concurrent.futures

from ..localization.localization import Localizer

class Loader:

    @staticmethod 
    def fetch(endpoint="/", session=None, language="all"):
        if session:
            data = session.get(f"https://valorant-api.com/v1{endpoint}?language={language}")
        else:
            data = requests.get(f"https://valorant-api.com/v1{endpoint}?language={language}")
        return data.json()

    @staticmethod 
    def load_all_content(client):
        content_data = {
            "agents": {},
            "maps": {},
            "modes": [],   
            "comp_tiers": {},
            "season": {},
            "queue_aliases": { #i'm so sad these have to be hardcoded but oh well :(
                "newmap": "New Map",
                "competitive": "Competitive",
                "unrated": "Unrated",
                "spikerush": "Spike Rush",
                "deathmatch": "Deathmatch",
                "ggteam": "Escalation",
                "onefa": "Replication",
                "custom": "Custom",
                "snowball": "Snowball Fight",
                "swiftplay": "Swiftplay",
                "hurm": "Team Deathmatch",
                "": "Custom",
            },
            "team_aliases": {
                "TeamOne": "Defender",
                "TeamTwo": "Attacker",
                "TeamSpectate": "Observer",
                "TeamOneCoaches": "Defender Coach",
                "TeamTwoCoaches": "Attacker Coach",
            },
            "team_image_aliases": {
                "TeamOne": "team_defender",
                "TeamTwo": "team_attacker",
                "Red": "team_defender",
                "Blue": "team_attacker",
            },
            "modes_with_icons": ["ggteam","onefa","snowball","spikerush","unrated","deathmatch","swiftplay","hurm"]
        }
        all_content = client.fetch_content()

        current_locale = Localizer.locale
        needs_localization = current_locale != "en-US"

        with requests.Session() as session:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                f_agents_en = executor.submit(Loader.fetch, "/agents", session, "en-US")
                f_maps_en = executor.submit(Loader.fetch, "/maps", session, "en-US")
                f_modes_en = executor.submit(Loader.fetch, "/gamemodes", session, "en-US")
                f_tiers_en = executor.submit(Loader.fetch, "/competitivetiers", session, "en-US")

                f_agents_loc = None
                f_maps_loc = None
                f_modes_loc = None
                f_tiers_loc = None

                if needs_localization:
                    f_agents_loc = executor.submit(Loader.fetch, "/agents", session, current_locale)
                    f_maps_loc = executor.submit(Loader.fetch, "/maps", session, current_locale)
                    f_modes_loc = executor.submit(Loader.fetch, "/gamemodes", session, current_locale)
                    f_tiers_loc = executor.submit(Loader.fetch, "/competitivetiers", session, current_locale)

                agents_en = f_agents_en.result()["data"]
                maps_en = f_maps_en.result()["data"]
                modes_en = f_modes_en.result()["data"]
                tiers_en = f_tiers_en.result()["data"][-1]["tiers"]

                agents_loc = f_agents_loc.result()["data"] if f_agents_loc else agents_en
                maps_loc = f_maps_loc.result()["data"] if f_maps_loc else maps_en
                modes_loc = f_modes_loc.result()["data"] if f_modes_loc else modes_en
                tiers_loc = f_tiers_loc.result()["data"][-1]["tiers"] if f_tiers_loc else tiers_en
        
        # Create lookup maps for localized data to ensure O(1) access
        agents_loc_map = {a["uuid"]: a for a in agents_loc}
        maps_loc_map = {m["mapUrl"]: m for m in maps_loc}
        modes_loc_map = {m["uuid"]: m for m in modes_loc}
        tiers_loc_map = {t["tier"]: t for t in tiers_loc}

        for season in all_content["Seasons"]:
            if season["IsActive"] and season["Type"] == "act":
                content_data["season"] = {
                    "competitive_uuid": season["ID"],
                    "season_uuid": season["ID"],
                    "display_name": season["Name"]
                }

        for agent in agents_en:
            uuid = agent["uuid"]
            loc_agent = agents_loc_map.get(uuid, agent)
            content_data["agents"][uuid] = {
                "uuid": uuid,
                "display_name": agent["displayName"],
                "display_name_localized": loc_agent["displayName"],
                "internal_name": agent["developerName"]
            }

        for game_map in maps_en:
            url = game_map["mapUrl"]
            loc_map = maps_loc_map.get(url, game_map)
            content_data["maps"][url] = {
                "uuid": game_map["uuid"],
                "display_name": game_map["displayName"],
                "display_name_localized": loc_map["displayName"],
                "path": url,
                "internal_name": url.split("/")[-1]
            }

        for mode in modes_en:
            uuid = mode["uuid"]
            loc_mode = modes_loc_map.get(uuid, mode)
            content_data["modes"].append({
                "uuid": uuid,
                "display_name": mode["displayName"],
                "display_name_localized": loc_mode["displayName"],
            })

        for tier in tiers_en:
            tier_id = tier["tier"]
            loc_tier = tiers_loc_map.get(tier_id, tier)
            content_data["comp_tiers"][tier_id] = {
                "display_name": tier["tierName"],
                "display_name_localized": loc_tier["tierName"],
                "id": tier_id,
            }

        return content_data
