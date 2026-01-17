import psutil
import os

class Processes:

    @staticmethod
    def are_processes_running(required_processes=["VALORANT-Win64-Shipping.exe", "RiotClientServices.exe"]):
        required_processes = set(required_processes)
        for proc in psutil.process_iter():
            if proc.name() in required_processes:
                required_processes.remove(proc.name())
            if not required_processes:
                return True
        return False

    @staticmethod
    def is_program_already_running():
        count = 0
        for proc in psutil.process_iter():
            if proc.name() == "valorant-rpc.exe":
                count += 1
        return count > 2