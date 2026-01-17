import time
import requests
import sys
import os

# Add current directory to path to ensure imports work
sys.path.append(os.getcwd())

from src.content.content_loader import Loader
from src.localization.localization import Localizer

# Mock Client
class MockClient:
    def fetch_content(self):
        return {
            "Seasons": [
                {
                    "IsActive": True,
                    "Type": "act",
                    "ID": "0df5adb9-4dcb-6899-1306-3e9860661dd3",
                    "Name": "EPISODE 7 // ACT 1"
                }
            ]
        }

def benchmark():
    client = MockClient()

    # Initialize Localizer since it's used in load_all_content
    # Localizer.locale defaults to "en-US", which is fine.

    print("Starting benchmark...")
    start_time = time.time()

    try:
        content = Loader.load_all_content(client)
    except Exception as e:
        print(f"Error during loading: {e}")
        import traceback
        traceback.print_exc()
        return

    end_time = time.time()
    duration = end_time - start_time

    print(f"Benchmark finished.")
    print(f"Time taken: {duration:.4f} seconds")

    # Basic validation
    print(f"Loaded {len(content['agents'])} agents")
    print(f"Loaded {len(content['maps'])} maps")
    print(f"Loaded {len(content['modes'])} modes")
    print(f"Loaded {len(content['comp_tiers'])} comp tiers")

if __name__ == "__main__":
    benchmark()
