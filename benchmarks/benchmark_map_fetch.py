import timeit
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from src.presence.presence_utilities import Utilities

def benchmark():
    # Setup mock data for DICT implementation (new)
    num_maps = 1000
    target_map_path = f"/Game/Maps/Map_{num_maps - 1}"

    # New structure: Dict of dicts keyed by path
    content_data = {
        "maps": {
            f"/Game/Maps/Map_{i}": {
                "path": f"/Game/Maps/Map_{i}",
                "display_name": f"Map {i}",
                "display_name_localized": f"Map {i} Loc"
            } for i in range(num_maps)
        }
    }

    coregame_data = {"MapID": target_map_path}

    # Verify implementation works as expected
    print(f"Testing with {num_maps} maps (Dictionary Lookup)")
    result = Utilities.fetch_map_data(coregame_data, content_data)
    expected = (f"Map {num_maps - 1}", f"Map {num_maps - 1} Loc")

    if result != expected:
        print(f"Validation Failed! Got {result}, expected {expected}")
        return

    # Benchmark
    def run_fetch():
        return Utilities.fetch_map_data(coregame_data, content_data)

    iterations = 100000
    time_taken = timeit.timeit(run_fetch, number=iterations)

    print(f"Time for {iterations} lookups: {time_taken:.4f} seconds")
    print(f"Average time per lookup: {time_taken/iterations*1e6:.4f} microseconds")

if __name__ == "__main__":
    benchmark()
