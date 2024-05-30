"""
Module to store functions that create different schedules 

Author: Milind Kumar Vaddiraju, ChatGPT, CoPilot
"""

import numpy as np
import random

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