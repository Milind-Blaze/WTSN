"""
Module to store functions that create different schedules 

Author: Milind Kumar Vaddiraju, ChatGPT, CoPilot
"""

import numpy as np

from network_classes import *

def create_schedule(UE_names: list, schedule_name: str, start_time: float, end_time: float, **kwargs):
    """
    Create a schedule based on the given configuration

    Args:
        UE_names (list): List of UE names
        schedule_name (str): Name of the schedule
        start_time (float): Start time of the schedule in microseconds
        end_time (float): End time of the schedule in microseconds
    """

    if schedule_name == "roundrobin":

        assert "qbv_window_size" in kwargs, "Round Robin schedule requires 'qbv_window_size' parameter"
        qbv_window_size = kwargs["qbv_window_size"]

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