import psutil
import os

class Processes:

    @staticmethod
    def are_processes_running(required_processes=["VALORANT-Win64-Shipping.exe", "RiotClientServices.exe"]):
        required = set(required_processes)
        for proc in psutil.process_iter(['name']):
            name = proc.info.get('name')
            if name in required:
                required.remove(name)

            if not required:
                return True
        
        return False

    @staticmethod
    def is_program_already_running():
        count = 0
        for proc in psutil.process_iter():
            if proc.name() == "valorant-rpc.exe":
                count += 1
        return count > 2