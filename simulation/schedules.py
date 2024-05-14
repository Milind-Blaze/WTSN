"""
Module to store functions that create different schedules 

Author: Milind Kumar Vaddiraju, ChatGPT, CoPilot
"""

import numpy as np

from network_classes import *

def create_schedule(UE_names: list, start_time: float, end_time: float, schedule_config: dict):
    """
    Create a schedule based on the given configuration

    Args:
        UE_names (list): List of UE names
        schedule_name (str): Name of the schedule
        start_time (float): Start time of the schedule in microseconds
        end_time (float): End time of the schedule in microseconds
    """
    assert "schedule_name" in schedule_config, "Schedule name not found in the schedule configuration"
    schedule_name = schedule_config["schedule_name"]

    if schedule_name == "roundrobin":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_name = UE_names[(num_slot % num_UEs)]
            UE_names_temp = [UE_name]
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return schedule_contention
    
    elif schedule_name == "grouped roundrobin":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        assert "num_UEs_together" in schedule_config, "Round Robin schedule requires 'num_UEs_together' parameter"

        qbv_window_size = schedule_config["qbv_window_size"]
        num_UEs_together = schedule_config["num_UEs_together"]
        assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
             or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            for i in range(num_UEs_together):
                UE_names_temp.append(UE_names[((num_slot + i) % num_UEs)])
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return schedule_contention
    
    elif schedule_name == "schedule 3":

        assert "qbv_window_size" in schedule_config, "schedule 3 requires 'qbv_window_size' parameter"
        assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "contention_window_size" in schedule_config, "schedule 3 requires 'contention_window_size' parameter"

        qbv_window_size = schedule_config["qbv_window_size"]
        num_UEs_together = schedule_config["num_UEs_together"]
        contention_window_size = schedule_config["contention_window_size"]

        assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
             or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                for i in range(num_UEs_together):
                    UE_names_temp.append(UE_names[(int(num_slot/2 + i) % num_UEs)])
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            else:
                UE_names_temp = UE_names
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return schedule_contention