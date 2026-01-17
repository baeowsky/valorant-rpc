import timeit
import sys
import os

# Add current directory to path to ensure imports work
sys.path.append(os.getcwd())

from src.presence.presence_utilities import Utilities
from src.localization.localization import Localizer

# Mock Client
class MockClient:
    def fetch_mmr(self):
        return {
            "QueueSkills": {
                "competitive": {
                    "SeasonalInfoBySeasonID": {
                        "season_uuid": {
                            "CompetitiveTier": 50, # Search for ID 50
                            "RankedRating": 50,
                            "LeaderboardRank": 0
                        }
                    }
                }
            }
        }

def create_mock_content_data(num_tiers=100):
    comp_tiers = {}
    for i in range(num_tiers):
        comp_tiers[i] = {
            "id": i,
            "display_name": f"Tier {i}",
            "display_name_localized": f"Tier Localized {i}"
        }

    return {
        "season": {
            "season_uuid": "season_uuid"
        },
        "comp_tiers": comp_tiers
    }

def benchmark():
    client = MockClient()
    content_data = create_mock_content_data(100) # 100 tiers

    # Test one run to ensure it works
    try:
        image, text = Utilities.fetch_rank_data(client, content_data)
        # print(f"Result: {image}, {text}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # Benchmark
    number = 100000
    time = timeit.timeit(lambda: Utilities.fetch_rank_data(client, content_data), number=number)
    print(f"Time for {number} iterations: {time:.4f} seconds")
    print(f"Average time per iteration: {time/number*1e6:.4f} microseconds")

if __name__ == "__main__":
    benchmark()
