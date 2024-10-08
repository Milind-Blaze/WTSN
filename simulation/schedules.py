"""
Module to store functions that create different schedules 

Author: Milind Kumar Vaddiraju, ChatGPT, CoPilot
"""

import numpy as np
import random
import typing
from typing import List, Tuple, Dict, Optional

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


    if schedule_name == "CSMA":

        
        slots_temp = {}
        num_slot = 0
        
        slots_temp[0] = Slot(0, start_time, end_time, "contention", UE_names)

        schedule_contention = Schedule(start_time, end_time, 1, slots_temp)
        cycle_time = end_time

        return (schedule_contention, cycle_time)

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

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "33ms slots 1 UE":

        assert "qbv_window_size" in schedule_config, "33ms schedule requires 'qbv_window_size' parameter"
        assert "data_start_time" in schedule_config, "33ms schedule requires 'data_start_time' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]
        data_start_time = schedule_config["data_start_time"]

        
        slots_temp = {}
        qbv_start_time = data_start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = ["UE0"]
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_start_time + 33.3*1000

            
        cycle_time = end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    

    if schedule_name == "OFDMA slots":

        assert "qbv_window_size" in schedule_config, "OFDMA slots requires 'qbv_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = UE_names
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "OFDMA",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "grouped roundrobin":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        assert "num_UEs_together" in schedule_config, "Round Robin schedule requires 'num_UEs_together' parameter"

        qbv_window_size = schedule_config["qbv_window_size"]
        num_UEs_together = schedule_config["num_UEs_together"]
        assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
             or equal to the total number of UEs"
        
        if "offset" in schedule_config:
            offset = schedule_config["offset"]
            assert offset > 0, "Offset should be greater than 0"
        else:
            offset = 1

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            for i in range(num_UEs_together):
                UE_names_temp.append(UE_names[((num_slot + i*offset) % num_UEs)])
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "schedule 3":
        """steps behind prison bars
        """
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

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "schedule 4":
        "relay handover"

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
                for i in range(1):
                    UE_names_temp.append(UE_names[(int(num_slot/2 + i) % num_UEs)])
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            else:
                for i in range(num_UEs_together):
                    UE_names_temp.append(UE_names[(int(num_slot/2 + i) % num_UEs)])
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time
            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "roundrobin blank":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        # Create the first slot with all the UEs
        slots_temp[num_slot] = Slot(num_slot,\
                                    qbv_start_time,\
                                    qbv_start_time + qbv_window_size,
                                    "contention",
                                    UE_names)
        num_slot += 1
        qbv_start_time += qbv_window_size


        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "schedule 5":
        

        assert "qbv_window_size" in schedule_config, "schedule 3 requires 'qbv_window_size' parameter"
        assert "num_UEs_together_qbv" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "contention_window_size" in schedule_config, "schedule 3 requires 'contention_window_size' parameter"
        assert "num_UEs_together_contention" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"

        qbv_window_size = schedule_config["qbv_window_size"]
        num_UEs_together_qbv = schedule_config["num_UEs_together_qbv"]
        contention_window_size = schedule_config["contention_window_size"]
        num_UEs_together_contention = schedule_config["num_UEs_together_contention"]

        assert num_UEs_together_qbv < len(UE_names), "Number of UEs together should be less than \
             or equal to the total number of UEs"
        assert num_UEs_together_contention < len(UE_names), "Number of UEs together should be less than \
             or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time

        forward = True
        forward_counter = 0
        backward_counter = num_UEs - 1

        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []

            if forward:
                for i in range(num_UEs_together_qbv):
                    UE_names_temp.append(UE_names[(forward_counter + i) % num_UEs])
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
                forward_counter += 1
            else:
                for i in range(num_UEs_together_contention):
                    UE_names_temp.append(UE_names[(backward_counter - i) % num_UEs])
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
                backward_counter -= 1

            forward = not forward

            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time
            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, 10*cycle_time)
    
    elif schedule_name == "contention 5 apart 10UEs":

        assert "qbv_window_size" in schedule_config, "Schedule requires 'qbv_window_size' parameter"
        assert "contention_window_size" in schedule_config, "Schedule requires 'contention_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]
        contention_window_size = schedule_config["contention_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0



        schedule = [["UE0"], ["UE1"], ["UE2"], ["UE3"], ["UE4"], ["UE0","UE9"],\
                    ["UE5"], ["UE6"], ["UE7"], ["UE8"], ["UE9"], ["UE4", "UE5"]]

        while qbv_start_time < end_time:
            
            

            if (schedule[num_slot%len(schedule)] == ["UE0", "UE9"] or \
                schedule[num_slot%len(schedule)] == ["UE4", "UE5"]):
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
            else:
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)

            


            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        schedule[num_slot%len(schedule)])
            num_slot += 1

            qbv_start_time = qbv_end_time

            if num_slot == num_UEs+2:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, 10*cycle_time)
    
    elif schedule_name == "roundrobin then contention":

        assert "qbv_window_size" in schedule_config, "Schedule requires 'qbv_window_size' parameter"
        assert "contention_window_size" in schedule_config, "Schedule requires 'contention_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]
        contention_window_size = schedule_config["contention_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0



        schedule = [[UE_names[i]] for i in range(num_UEs)]
        schedule.append(UE_names)

        while qbv_start_time < end_time:
            
            

            if (num_slot%len(schedule) == num_UEs):
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
            else:
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)

            


            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        schedule[num_slot%len(schedule)])
            num_slot += 1

            qbv_start_time = qbv_end_time

            if num_slot == num_UEs+1:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "random roundrobin":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_name = random.choice(UE_names)
            UE_names_temp = [UE_name]
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    

    if schedule_name == "shuffle roundrobin":

        assert "qbv_window_size" in schedule_config, "Round Robin schedule requires 'qbv_window_size' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)

            if num_slot%num_UEs == 0:
                random.shuffle(UE_names)

            UE_name = UE_names[(num_slot % num_UEs)]
            UE_names_temp = [UE_name]
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    elif schedule_name == "roundrobin then partial contention":

        assert "qbv_window_size" in schedule_config, "Schedule requires 'qbv_window_size' parameter"
        assert "contention_window_size" in schedule_config, "Schedule requires 'contention_window_size' parameter"
        assert "contention_UE_indices" in schedule_config, "Schedule requires 'contention_UE_indices' parameter"
        qbv_window_size = schedule_config["qbv_window_size"]
        contention_window_size = schedule_config["contention_window_size"]
        contention_UE_indices = schedule_config["contention_UE_indices"]

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0



        schedule = [[UE_names[i]] for i in range(num_UEs)]
        schedule.append(UE_names)

        while qbv_start_time < end_time:
            
            

            if (num_slot%len(schedule) == num_UEs):
                qbv_end_time = min(qbv_start_time + contention_window_size, end_time)
                UEs_temp = [UE_names[i] for i in contention_UE_indices]
            else:
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
                UEs_temp = schedule[num_slot%len(schedule)]

            


            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UEs_temp)
            num_slot += 1

            qbv_start_time = qbv_end_time

            if num_slot == num_UEs+1:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "arbitrary urllc then embb schedule":
        """urllc then embb
        """
        assert "urllc_window_size" in schedule_config, "schedule requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'contention_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "schedule requires 'urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"


        embb_counter = 0
        urllc_counter = 0

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                embb_counter += 1
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "OFDMA UL urllc then SU DL CSMA then embb":
        """urllc then embb
        """
        assert "UL_urllc_window_size" in schedule_config, "schedule requires 'UL_urllc_window_size' parameter"
        assert "DL_urllc_window_size" in schedule_config, "schedule  requires 'DL_urllc_window_size' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'embb_window_size' parameter"
        assert "UL_urllc_schedule" in schedule_config, "schedule requires 'UL_urllc schedule' parameter"
        assert "DL_urllc_schedule" in schedule_config, "schedule requires 'DL_urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"


        UL_urllc_window_size = schedule_config["UL_urllc_window_size"]
        DL_urllc_window_size = schedule_config["DL_urllc_window_size"]
        UL_urllc_schedule = schedule_config["UL_urllc_schedule"]
        DL_urllc_schedule = schedule_config["DL_urllc_schedule"]
        embb_window_size = schedule_config["embb_window_size"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        embb_counter = 0

        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%3 == 0:
                UE_names_temp = UL_urllc_schedule[0]
                qbv_end_time = min(qbv_start_time + UL_urllc_window_size, end_time)
                slot_type = "OFDMA"
            elif num_slot%3 == 1:
                UE_names_temp = DL_urllc_schedule[0]
                qbv_end_time = min(qbv_start_time + DL_urllc_window_size, end_time)
                slot_type = "contention"
            else:
                UE_names_temp = embb_schedule[0]
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                slot_type = "contention"
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        slot_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "OFDMA UL urllc then SU DL CSMA then embb OFDMA + SU":
        """urllc then embb
        """
        assert "UL_urllc_window_size" in schedule_config, "schedule requires 'UL_urllc_window_size' parameter"
        assert "DL_urllc_window_size" in schedule_config, "schedule  requires 'DL_urllc_window_size' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'embb_window_size' parameter"
        assert "UL_urllc_schedule" in schedule_config, "schedule requires 'UL_urllc schedule' parameter"
        assert "DL_urllc_schedule" in schedule_config, "schedule requires 'DL_urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"


        UL_urllc_window_size = schedule_config["UL_urllc_window_size"]
        DL_urllc_window_size = schedule_config["DL_urllc_window_size"]
        UL_urllc_schedule = schedule_config["UL_urllc_schedule"]
        DL_urllc_schedule = schedule_config["DL_urllc_schedule"]
        embb_window_size = schedule_config["embb_window_size"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        embb_counter = 0

        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%3 == 0:
                UE_names_temp = UL_urllc_schedule[0]
                qbv_end_time = min(qbv_start_time + UL_urllc_window_size, end_time)
                slot_type = "OFDMA"
            elif num_slot%3 == 1:
                UE_names_temp = DL_urllc_schedule[0]
                qbv_end_time = min(qbv_start_time + DL_urllc_window_size, end_time)
                slot_type = "contention"
            else:
                if embb_counter%num_UEs == 0:
                    UE_names_temp = embb_schedule[0]
                    qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                    slot_type = "contention"
                else:
                    UE_names_temp = embb_schedule[1]
                    qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                    slot_type = "OFDMA"
                embb_counter += 1
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        slot_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)

    if schedule_name == "OFDMA UL RR then SU DL":
        """OFDMA RR then SU
        """
        assert "UL_window_size" in schedule_config, "schedule requires 'UL_urllc_window_size' parameter"
        assert "DL_window_size" in schedule_config, "schedule  requires 'DL_urllc_window_size' parameter"
        assert "UL_schedule" in schedule_config, "schedule requires 'UL_urllc schedule' parameter"
        assert "DL_schedule" in schedule_config, "schedule requires 'DL_urllc schedule' parameter"
        assert "num_slots" in schedule_config, "schedule requires 'num_slots' parameter"


        UL_window_size = schedule_config["UL_window_size"]
        DL_window_size = schedule_config["DL_window_size"]
        UL_schedule = schedule_config["UL_schedule"]
        DL_schedule = schedule_config["DL_schedule"]
        num_slots = schedule_config["num_slots"]
        

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%num_slots == 0:
                UE_names_temp = DL_schedule[0]
                qbv_end_time = min(qbv_start_time + DL_window_size, end_time)
                slot_type = "contention"
            else:
                UE_names_temp = UL_schedule[0]
                qbv_end_time = min(qbv_start_time + UL_window_size, end_time)
                slot_type = "OFDMA"
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        slot_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)

    
    


def create_schedule_dynamic(UE_names: list, start_time: float, end_time: float, config: dict, \
                            lambda_value: float, delivery_latency: list[float]):
    """
    Create a schedule based on the given configuration

    Args:
        UE_names (list): List of UE names
        schedule_name (str): Name of the schedule
        start_time (float): Start time of the schedule in microseconds
        end_time (float): End time of the schedule in microseconds
    """
    assert "schedule_name" in config["schedule_config"], "Schedule name not found in the schedule configuration"
    schedule_name = config["schedule_config"]["schedule_name"]
    schedule_config = config["schedule_config"]

    if schedule_name == "dynamic roundrobin":

        num_UEs = len(UE_names)
        wifi_slot_time = config["wifi_slot_time"] # microseconds
        DIFS = config["DIFS"] # microseconds
        CWmin = config["CWmin"]
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        # computing the qbv_window_size based on the lambda value and delivery latency
        for delivery_latency_index in range(len(delivery_latency)):
            delivery_latency_value = delivery_latency[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
            if num_UEs*slot_length_temp*lambda_value < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp





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

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "dynamic roundrobin blank":

        num_UEs = len(UE_names)
        wifi_slot_time = config["wifi_slot_time"] # microseconds
        DIFS = config["DIFS"] # microseconds
        CWmin = config["CWmin"]
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        # computing the qbv_window_size based on the lambda value and delivery latency
        for delivery_latency_index in range(len(delivery_latency)):
            delivery_latency_value = delivery_latency[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
            if num_UEs*slot_length_temp*lambda_value < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp


        # Create the first slot with all the UEs
        slots_temp[num_slot] = Slot(num_slot,\
                                    qbv_start_time,\
                                    qbv_start_time + qbv_window_size,
                                    "contention",
                                    UE_names)
        num_slot += 1
        qbv_start_time += qbv_window_size


        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    

    if schedule_name == "dynamic grr":
        

        schedule_config = config["schedule_config"]

        assert "num_UEs_together" in schedule_config, "Round Robin schedule requires 'num_UEs_together' parameter"

        num_UEs_together = schedule_config["num_UEs_together"]

        if "offset" in schedule_config:
            offset = schedule_config["offset"]
            assert offset > 0, "Offset should be greater than 0"
        else:
            offset = 1


        if "scaling_factor" in schedule_config:
            scaling_factor = schedule_config["scaling_factor"]
            assert scaling_factor >= 1, "Scaling factor should be greater than 0"
        else: 
            scaling_factor = 1

        num_UEs = len(UE_names)
        wifi_slot_time = config["wifi_slot_time"] # microseconds
        DIFS = config["DIFS"] # microseconds
        CWmin = config["CWmin"]
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0

        # computing the qbv_window_size based on the lambda value and delivery latency
        for delivery_latency_index in range(len(delivery_latency)):
            delivery_latency_value = delivery_latency[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
            if num_UEs*slot_length_temp*lambda_value < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp


        qbv_window_size = qbv_window_size*scaling_factor



        while qbv_start_time < end_time:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            for i in range(num_UEs_together):
                UE_names_temp.append(UE_names[((num_slot + i*offset) % num_UEs)])
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "dynamic HBC":
        """
        In this schedule, the length of the URLLC slot is kept fixed and the 
        length of the alternating eMBB slot is varied based on the lambda value.
        Note that URLLC and eMBB slots alternate. Note that the eMBB slots can be 
        no farther apart than the maximum allowed interval between URLLC slots.
        This is based on the idea that the LLC with the 1.5 ms separated slots worked
        well.
        """

        num_UEs = len(UE_names)
        wifi_slot_time = config["wifi_slot_time"] # microseconds
        DIFS = config["DIFS"] # microseconds
        CWmin = config["CWmin"]

        # lambda_fraction_embb is for the schedule creation i.e slots are sized based on much
        # traffic would have gone through the eMBB slots. lambda_fraction is for the actual
        # traffic generation: to be used depending on whether URLLC or eMBB is being simulated
        assert "lambda_fraction_embb" in schedule_config, "Schedule requires 'lambda_fraction_embb' parameter"
        assert "lambda_fraction" in schedule_config, "Schedule requires 'lambda_fraction' parameter"
        assert "delivery_latency_spec" in schedule_config, "Schedule requires 'delivery_latency_embb' parameter"
        assert "delivery_latency_embb" in schedule_config["delivery_latency_spec"], "Schedule requires 'delivery_latency_embb' parameter"
        assert "maximum_urllc_interval" in schedule_config, "Schedule requires 'maximum_urllc_interval' parameter"
        assert "urllc_window_size" in schedule_config, "Schedule requires 'urllc_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "Schedule requires 'urllc_schedule' parameter"
        assert "embb_schedule" in schedule_config, "Schedule requires 'embb_schedule' parameter"
        

        lambda_fraction_embb = schedule_config["lambda_fraction_embb"]
        delivery_latency_spec = schedule_config["delivery_latency_spec"]
        delivery_latency_embb = schedule_config["delivery_latency_spec"]["delivery_latency_embb"]
        maximum_urllc_interval = schedule_config["maximum_urllc_interval"]
        urllc_window_size = schedule_config["urllc_window_size"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        assert maximum_urllc_interval > 500, "Maximum URLLC interval should be greater than 500 \
                                             microseconds, to allow at least some transmission"
        assert delivery_latency_spec["MCS"] == 7, "Hardcoded MCS value for now, ensure embb \
                                                    latencies are used"

        # TODO: add a config parameter that chooses different MCS delivery times


        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        embb_counter = 0
        urllc_counter = 0

        # computing the qbv_window_size based on the lambda value and delivery latency
        for delivery_latency_index in range(len(delivery_latency_embb)):
            delivery_latency_value = delivery_latency_embb[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value

            time_to_slot = num_UEs*(urllc_window_size + slot_length_temp)
            packets_accumulated = lambda_fraction_embb*lambda_value*time_to_slot

            if slot_length_temp >= maximum_urllc_interval: 
                # This if condition is assuming some reasonable MCS and maximum_urllc_interval
                delivery_latency_value = delivery_latency_embb[delivery_latency_index - 1]
                slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
                qbv_window_size = slot_length_temp
                break
            elif packets_accumulated < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp





        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
                embb_counter += 1
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time


            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)

    if schedule_name == "dynamic HBC and LLC":
        """
        In this schedule, the length of the URLLC slot and the 
        length of the eMBB slot are varied based on the lambda value.
        Note that URLLC and eMBB slots alternate. 
        """

        num_UEs = len(UE_names)
        wifi_slot_time = config["wifi_slot_time"] # microseconds
        DIFS = config["DIFS"] # microseconds
        CWmin = config["CWmin"]

        # lambda_fraction_embb is for the schedule creation i.e slots are sized based on much
        # traffic would have gone through the eMBB slots. lambda_fraction is for the actual
        # traffic generation: to be used depending on whether URLLC or eMBB is being simulated
        assert "lambda_fraction_embb" in schedule_config, "Schedule requires 'lambda_fraction_embb' parameter"
        assert "lambda_fraction" in schedule_config, "Schedule requires 'lambda_fraction' parameter"
        assert "delivery_latency_spec" in schedule_config, "Schedule requires 'delivery_latency_embb' parameter"
        assert "delivery_latency_embb" in schedule_config["delivery_latency_spec"], "Schedule requires 'delivery_latency_embb' parameter"
        assert "maximum_urllc_interval" in schedule_config, "Schedule requires 'maximum_urllc_interval' parameter"
        # assert "urllc_window_size" in schedule_config, "Schedule requires 'urllc_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "Schedule requires 'urllc_schedule' parameter"
        assert "embb_schedule" in schedule_config, "Schedule requires 'embb_schedule' parameter"
        

        lambda_fraction_embb = schedule_config["lambda_fraction_embb"]
        delivery_latency_spec = schedule_config["delivery_latency_spec"]
        delivery_latency_embb = schedule_config["delivery_latency_spec"]["delivery_latency_embb"]
        maximum_urllc_interval = schedule_config["maximum_urllc_interval"]
        urllc_buffer = schedule_config["urllc_buffer"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        assert maximum_urllc_interval > 500, "Maximum URLLC interval should be greater than 500 \
                                             microseconds, to allow at least some transmission"
        assert delivery_latency_spec["MCS"] == 7, "Hardcoded MCS value for now, ensure embb \
                                                    latencies are used"

        # TODO: add a config parameter that chooses different MCS delivery times


        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        embb_counter = 0
        urllc_counter = 0

        # computing the qbv_window_size based on the lambda value and delivery latency
        for delivery_latency_index in range(len(delivery_latency_embb)):
            delivery_latency_value = delivery_latency_embb[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
            urllc_window_size = slot_length_temp + urllc_buffer
            time_to_slot = num_UEs*(urllc_window_size + slot_length_temp)
            packets_accumulated = lambda_fraction_embb*lambda_value*time_to_slot

            if slot_length_temp >= maximum_urllc_interval: 
                # This if condition is assuming some reasonable MCS and maximum_urllc_interval
                delivery_latency_value = delivery_latency_embb[delivery_latency_index - 1]
                slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
                qbv_window_size = slot_length_temp
                break
            elif packets_accumulated < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp





        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
                embb_counter += 1
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time


            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time 

        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)  



def create_max_weight_schedule(UE_names: list, start_time: float, end_time: float, config: dict, \
                            lambda_value: Optional[float], delivery_latency: Optional[list[float]]):
    
    assert "schedule_config" in config, "Schedule configuration not found in the configuration"
    assert "schedule_name" in config["schedule_config"], "Schedule name not found in the schedule \
        configuration"
    assert "is_dynamic" in config["schedule_config"], "Dynamic parameter not found in the schedule \
        configuration"
    assert "measurement_periodicity" in config["schedule_config"], "Measurement periodicity not \
        found in the schedule configuration"
    assert "measurement_window_size" in config["schedule_config"], "Measurement window size not \
        found in the schedule configuration"
    
    schedule_name = config["schedule_config"]["schedule_name"]
    is_dynamic = config["schedule_config"]["is_dynamic"]
    measurement_periodicity = config["schedule_config"]["measurement_periodicity"]
    measurement_window_size = config["schedule_config"]["measurement_window_size"]


    num_UEs = len(UE_names)
    wifi_slot_time = config["wifi_slot_time"] # microseconds
    DIFS = config["DIFS"] # microseconds
    CWmin = config["CWmin"]
    slots_temp = {}
    qbv_start_time = start_time
    num_slot = 0
    num_slot_measurement = 0

    # computing the qbv_window_size based on the lambda value and delivery latency
    if is_dynamic:

        assert lambda_value is not None, "Lambda value not found in the configuration"
        assert delivery_latency is not None, "Delivery latency not found in the configuration"

        amortized_measurement_window_size = measurement_window_size/measurement_periodicity
        for delivery_latency_index in range(len(delivery_latency)):
            delivery_latency_value = delivery_latency[delivery_latency_index]
            slot_length_temp = DIFS + CWmin*wifi_slot_time + delivery_latency_value
            if num_UEs*(slot_length_temp + amortized_measurement_window_size)*lambda_value \
                < delivery_latency_index:
                qbv_window_size = slot_length_temp
                break
            elif delivery_latency_index == len(delivery_latency) - 1:
                qbv_window_size = slot_length_temp
    else:
        assert "qbv_window_size" in config["schedule_config"], "Schedule requires 'qbv_window_size' parameter"
        qbv_window_size = config["schedule_config"]["qbv_window_size"]


    # Create the first slot with all the UEs
    slots_temp[num_slot] = Slot(num_slot,\
                                qbv_start_time,\
                                qbv_start_time + qbv_window_size,
                                "contention",
                                UE_names)
    num_slot += 1
    qbv_start_time += qbv_window_size


    while qbv_start_time < end_time:
        if num_slot - num_slot_measurement > measurement_periodicity:
            num_slot_measurement = num_slot
            qbv_end_time = min(qbv_start_time + measurement_window_size, end_time)
            UE_names_temp = []
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        schedule_name,
                                        UE_names_temp)
        else:
            qbv_end_time = min(qbv_start_time + qbv_window_size, end_time)
            UE_names_temp = []
            slots_temp[num_slot] = Slot(num_slot,\
                                    qbv_start_time,\
                                    qbv_end_time,
                                    "contention",
                                    UE_names_temp)
        num_slot += 1
        qbv_start_time = qbv_end_time

        if num_slot == num_UEs:
            cycle_time = qbv_end_time 

    schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

    return (schedule_contention, cycle_time)


def create_schedule_HVCs(UE_names: list, start_time: float, end_time: float, schedule_config: dict):
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

    if schedule_name == "urllc then embb":
        """urllc then embb
        """
        assert "urllc_window_size" in schedule_config, "schedule 3 requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule 3 requires 'contention_window_size' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = [UE_names[i] + "_shadow" for i in range(num_UEs)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
            else:
                UE_names_temp = UE_names
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "arbitrary schedule":
        """urllc then embb
        """
        assert "urllc_window_size" in schedule_config, "schedule requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'contention_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "schedule requires 'urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"


        embb_counter = 0
        urllc_counter = 0

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                embb_counter += 1
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        "contention",
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)

    if schedule_name == "OFDMA urllc then embb":
        """urllc then embb
        """
        assert "urllc_window_size" in schedule_config, "schedule 3 requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule 3 requires 'contention_window_size' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = [UE_names[i] + "_shadow" for i in range(num_UEs)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                slot_type = "OFDMA"
            else:
                UE_names_temp = UE_names
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                slot_type = "contention"
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        slot_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)


    if schedule_name == "arbitrary OFDMA schedule":
        """urllc then embb
        """
        assert "urllc_window_size" in schedule_config, "schedule requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'contention_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "schedule requires 'urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"


        embb_counter = 0
        urllc_counter = 0

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if num_slot%2 == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
                schedule_type = "OFDMA"
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                embb_counter += 1
                if "embb_schedule_type" in schedule_config:
                    schedule_type = schedule_config["embb_schedule_type"]
                else:
                    schedule_type = "contention"
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        schedule_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
    
    if schedule_name == "OFDMA CSMA-AP":
        """APs have random access to the channel
        """
        assert "urllc_window_size" in schedule_config, "schedule requires 'qbv_window_size' parameter"
        # assert "num_UEs_together" in schedule_config, "schedule 3 requires 'num_UEs_together' parameter"
        assert "embb_window_size" in schedule_config, "schedule requires 'contention_window_size' parameter"
        assert "urllc_schedule" in schedule_config, "schedule requires 'urllc schedule' parameter"
        assert "embb_schedule" in schedule_config, "schedule requires 'embb schedule' parameter"

        urllc_window_size = schedule_config["urllc_window_size"]
        embb_window_size = schedule_config["embb_window_size"]
        urllc_schedule = schedule_config["urllc_schedule"]
        embb_schedule = schedule_config["embb_schedule"]

        # num_UEs_together = schedule_config["num_UEs_together"]
        # assert num_UEs_together < len(UE_names), "Number of UEs together should be less than \
        #      or equal to the total number of UEs"


        embb_counter = 0
        urllc_counter = 0

        num_UEs = len(UE_names)
        slots_temp = {}
        qbv_start_time = start_time
        num_slot = 0
        while qbv_start_time < end_time:
            
            UE_names_temp = []
            if random.choice([True,False]) == 0:
                UE_names_temp = urllc_schedule[urllc_counter%len(urllc_schedule)]
                qbv_end_time = min(qbv_start_time + urllc_window_size, end_time)
                urllc_counter += 1
                schedule_type = "OFDMA"
            else:
                UE_names_temp = embb_schedule[embb_counter%len(embb_schedule)]
                qbv_end_time = min(qbv_start_time + embb_window_size, end_time)
                embb_counter += 1
                if "embb_schedule_type" in schedule_config:
                    schedule_type = schedule_config["embb_schedule_type"]
                else:
                    schedule_type = "contention"
            
            slots_temp[num_slot] = Slot(num_slot,\
                                        qbv_start_time,\
                                        qbv_end_time,
                                        schedule_type,
                                        UE_names_temp)
            num_slot += 1
            qbv_start_time = qbv_end_time

            if num_slot == 2*num_UEs:
                cycle_time = qbv_end_time


        schedule_contention = Schedule(start_time, end_time, num_slot, slots_temp)

        return (schedule_contention, cycle_time)
