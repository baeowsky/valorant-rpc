import time
import sys
import os
import uuid
import random

# Add current directory to path
sys.path.append(os.getcwd())

from src.presence.presence_utilities import Utilities

def benchmark():
    # Setup data with a dict (new implementation)
    agents_dict = {}

    target_uuid = str(uuid.uuid4())

    # Generate 50 agents
    for i in range(50):
        uid = str(uuid.uuid4())
        if i == 25: # Put target in the middle
            uid = target_uuid

        agent = {
            "uuid": uid,
            "display_name": f"Agent {i}",
            "display_name_localized": f"Agent Localized {i}",
            "internal_name": f"AgentDev {i}"
        }
        agents_dict[uid] = agent

    # Mimic the content_data structure
    content_data = {"agents": agents_dict}

    print("Running benchmark with 1,000,000 lookups...")

    start_time = time.time()
    for _ in range(1000000):
        Utilities.fetch_agent_data(target_uuid, content_data)
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    benchmark()
