"""
File to contain all the network related classes and functionalities for the simulation

Author: Milind Kumar Vaddiraju, ChatGPT, Copilot
"""

# Necessary imports

import bisect
import copy
from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import typing
from typing import List, Tuple, Dict, Optional
import inspect

np.random.seed(1234)


# Create the necessary classes and structures

# TODO: do you need a mapping between the parameters of the sheet and corresponding latency?
# TODO: Add functions to plot the base schedules and whatnot

class PacketStatus(Enum):
    '''
    Enum to represent the status of a packet
    '''
    ARRIVED = 1
    QUEUED = 2
    DELIVERED = 3
    DROPPED = 4

class Packet:
    '''
    Class to represent a packet in the Wi-Fi network
    '''

    def __init__(self, size: int, priority: int, sequence_number: int, arrival_time: float) -> None:
        '''
        Constructor for the packet class

        Args:
            size (int): Size of the packet in bytes
            priority (int): Priority of the packet, the higher the value, higher
                the priority
            arrival_time (float): Time at which the packet arrives at the UE's 
                link layer for transmission in microseconds
        ''' 
        self.size = size
        self.priority = priority
        self.sequence_number = sequence_number
        self.arrival_time = arrival_time
        self.delivery_time = None
        self.status = PacketStatus.ARRIVED

    # Implement a __str__ function to print the packet
    def __str__(self) -> str:
        '''
        Function to print the packet
        '''
        output = (f"Packet(Size: {self.size} bytes, "
            f"Priority: {self.priority}, "
            f"Sequence Number: {self.sequence_number}, "
            f"Arrival Time: {self.arrival_time} microseconds, "
            f"Delivery Time: {self.delivery_time} microseconds, "
            f"Status: {self.status.name}")

        return output
        



class Slot:
    '''
    Class to represent a slot in the Wi-Fi network. This corresponds to a Qbv window
    and can either be reserved for a UE or have contetion
    '''
    
    def __init__(self, slot_index: int, start_time: float, end_time: float, mode: str, 
                UEs: List[str]) -> None:
        '''
        Constructor for the Slot class

        Args:
            slot_index (int): Index of the slot in the schedule, starts from 0
            start_time (float): Start time of the slot in microseconds
            end_time (float): End time of the slot in microseconds
            mode (str): Mode of the slot, can be either contention or reserved (using Qbv)
            UEs (List[str]): List of UEs that are permitted to transmit in the slot
        '''
        self.slot_index = slot_index
        self.start_time = start_time
        self.end_time = end_time
        self.mode = mode
        self.UEs = UEs

    # Implement a __str__ function to print the slot
    def __str__(self) -> str:
        '''
        Function to print the slot
        '''
        return (f"Slot(Index: {self.slot_index}, "
            f"Start Time: {self.start_time} microseconds, "
            f"End Time: {self.end_time} microseconds, "
            f"Mode: {self.mode}, "
            f"UEs: {self.UEs})")

class Schedule:
    '''
    Class to represent the base schedule for the Wi-Fi network
    '''

    def __init__(self, start_time: float, end_time: float, num_slots: int, 
                 schedule: typing.Dict[int, Slot]) -> None:
        '''
        Constructor for the BaseSchedule class

        Args:
            start_time (float): Start time of the schedule in microseconds
            end_time (float): End time of the schedule in microseconds
            num_slots (int): Number of slots in the schedule
            schedule (typing.Dict[int, typing.Dict[int, int]]): A dictionary with 
                the priority as the key and another dictionary as the value. This
                inner dictionary has the sequence number as the key and the size
                of the packet as the value
        '''
        self.start_time = start_time
        self.end_time = end_time
        self.num_slots = num_slots
        self.schedule = schedule

    # Implement a __str__ function to print the schedule   
    def __str__(self) -> str:
        '''
        Function to print the schedule
        '''
        output = (f"Schedule(Start Time: {self.start_time} microseconds, "
            f"End Time: {self.end_time} microseconds, "
            f"Number of Slots: {self.num_slots})")
        output += "\nSlots: \n"
        for slot in self.schedule:
            output += "\t" + str(self.schedule[slot]) + "\n"
        return output

class UE:
    '''
    Class to represent a User Equipment (UE) or STA in the Wi-Fi network
    '''
    # TODO: evaluate use of MCS
    # TODO: make MCS a function of not just priority but also time or slot index
    # TODO: write setting functions for each parameter
    # TODO: consider making this a super class with AP and STA as subclasses
    # TODO: consider adding both uplink and downlink functionality- is it even different
    def __init__(self, ue_id: int, mcs: typing.Dict[int, int], network_mode_of_operation: str, 
                service_mode_of_operation: str, n_packets : Optional[int], CWmin: int = 15,
                CWmax: int = 63) -> None:
        '''
        Constructor for the UE class

        Args:
            mcs (typing.Dict[int, int]): Dictionary with the priority as the key
                and the MCS as the value i.e packets with the priority will 
                be transmitted at the corresponding MCS
            netowork_mode_of_operation (str): Mode of operation of the UE, can be either
                "central control" or "free" (TODO: add more modes)
            service_mode_of_operation (str): Mode of operation of the UE within a Qbv
                window, used to determine how TXOP is used, how packets are allocated etc.
            n_packets (int): Number of packets that the UE has to transmit-set to None if
                the mode is an arrival process
        '''
        self.ue_id = ue_id
        self.mcs = mcs
        # TODO: remove these modes of operation and feed them into functions instead
        self.network_mode_of_operation = network_mode_of_operation
        self.service_mode_of_operation = service_mode_of_operation
        self.n_packets = n_packets
        # List to store the packets that the UE has to transmit
        self.packets = []
        # TODO: make this an input to the class constructor
        self.poisson_lambda = None
        self.CWmin = CWmin
        self.CWmax = CWmax
        self.CW = CWmin # Initial value of the contention window
        self.transmission_record = {}

    def __str__(self) -> str:
        # TODO: make sure this function is up to date
        '''
        Function to print the UE
        '''
        output = (f"UE(UE ID: {self.ue_id}, "
            f"UE(MCS: {self.mcs}, "
            f"Network mode of Operation: {self.network_mode_of_operation}, "
            f"Service mode of Operation: {self.service_mode_of_operation}, "
            f"CWmin: {self.CWmin}, "
            f"CWmax: {self.CWmax}, "
            f"CW: {self.CW}, "
            f"Number of Packets: {self.n_packets})")
        if self.poisson_lambda is not None:
            output += f"\nPoisson Lambda: {self.poisson_lambda}"
        output += "\nPackets: \n"
        for packet in self.packets:
            output += "\t" + str(packet) + "\n"
        return output
    
    def set_poisson_lambda(self, poisson_lambda: float) -> None:
        '''
        Function to set the rate/lambda value for the Poisson arrival process
        that governs its packet generation. Used only if the mode of operation
        is "Poisson"

        Args:
            poisson_lambda (float): Poisson lambda for the UE
        '''
        self.poisson_lambda = poisson_lambda


    def initialize_transmission_record(self, base_schedule: Schedule) -> None:
        '''
        Function to initialize the transmission record for the UE

        Args:
            base_schedule (Schedule): A base schedule specifying
                Qbv windows for different UEs across time
        '''
        for slot in base_schedule.schedule:
            self.transmission_record[slot] = {"num_wins": 0, 
                                            "num_transmissions": [],
                                            "num_contentions": 0,
                                            "queue_information": {
                                                "queue_times": [],
                                                "queue_lengths": []
                                            }}




    def  generate_packets(self, base_schedule : Schedule, packet_size: List[int], 
                          packet_priorities: List[int]) ->  None:
        '''
        TODO: Fix this to take a custom generator function from outside and run that,
            this function can potentially enforce some constraints on the custom funciton that 
            is passed in 
        Function to generate the packets that the UE has to transmit

        Args:
            base_schedule (Schedule): A base schedule specifying
                Qbv windows for different UEs across time
            packet_size (List[int]): size of each packet
        '''

        if self.network_mode_of_operation == "central control":

            assert len(packet_size) == self.n_packets, "Number of packet sizes and number \
                                                        of packets don't match"
            assert len(packet_priorities) == self.n_packets, "Number of priorities and number of \
                                                    packets don't match"

            ue_name = "UE" + str(self.ue_id)
            num_slots_ue = 0
            slots_ue = []
            # Determine which slots the UE can trasnmit in
            for slot in base_schedule.schedule:
                if ue_name in base_schedule.schedule[slot].UEs:
                    num_slots_ue += 1
                    slots_ue.append(base_schedule.schedule[slot].slot_index)
            
            # Generate packets based on the schedule
            # TODO: Fix the case where n_packets is lesser than number of slots allocated
            assert self.n_packets >= num_slots_ue, "Number of packets is lesser than the number of slots allocated"
            num_packets_per_slot = [int(np.floor(self.n_packets/num_slots_ue))]*num_slots_ue
            # If the number of packets isn't divisible by the number of slots
            # then put the remaining packets in the last slot
            num_packets_per_slot[-1] += self.n_packets - sum(num_packets_per_slot)

            assert len(slots_ue) == len(num_packets_per_slot), "Number of slots and number of \
                                                                packets per slot don't match"

            packet_counter = 0
            for slot_index, num_packets in zip(slots_ue, num_packets_per_slot):
                for _ in range(num_packets):
                    self.packets.append(Packet(size = packet_size[packet_counter], 
                                                priority = packet_priorities[packet_counter], 
                                                sequence_number = packet_counter,
                                                arrival_time = base_schedule.schedule[slot_index].start_time - 1))
                    packet_counter += 1
        
        elif self.network_mode_of_operation == "Poisson":
            assert self.poisson_lambda is not None, "Poisson lambda not set"
            # TODO: make packet_sizes and packet_priorities a function of packet_counter
            assert len(packet_size) == 1, "Packet size list should have only one element"
            assert len(packet_priorities) == 1, "Packet priority list should have only one element"

            # Number of packets is distributed as a poisson random variable
            interval = base_schedule.end_time - base_schedule.start_time
            self.n_packets = np.random.poisson(self.poisson_lambda*interval)
            
            # Arrival times are uniformly distributed over the interval
            # TODO: set random seed?
            
            arrival_times = np.random.uniform(base_schedule.start_time, base_schedule.end_time, 
                                              self.n_packets)
            arrival_times.sort()
            
            for packet_counter in range(self.n_packets):
                self.packets.append(Packet(size = packet_size[0], 
                                          priority = packet_priorities[0], 
                                          sequence_number = packet_counter,
                                          arrival_time = arrival_times[packet_counter]))

            

    def obtain_packet_latency(self) -> List[float]:
        '''
        Function to obtain the latency of each packet

        Returns:
            List[float]: List of latencies of each packet
        '''
        latencies = []
        for packet in self.packets:
            if packet.status == PacketStatus.DELIVERED:
                latencies.append(packet.delivery_time - packet.arrival_time)
            else:
                latencies.append(None)
        return latencies
    
    def transmit_packet(self, PER: float) -> bool:
        '''
        Function to simulate the transmission of a packet. A coin is tossed with the 
        probability of success being 1-PER and True (successful transmission) is returned
        if the result is 1

        Args:
            PER (float): Packet Error Rate, probability that the packet will be dropped

        Returns:
            bool: True if the packet was transmitted successfully, False otherwise
        '''
        # simulate a Bernoulli trial with PER as the probability of failure
        return np.random.binomial(1, 1-PER) == 1
            
    def serve_packets(self, base_schedule: Schedule, **kwargs) -> None:
        # TODO: Move this function to the network class
        '''
        Function to serve the packets that the UE has to transmit

        Args:
            base_schedule (Schedule): A base schedule specifying
                Qbv windows for different UEs across time
        '''
        if self.service_mode_of_operation == "Mode 1":
            '''
            Mode 1: Dummy mode for testing 

            Simply marks all packets as served after a 3000 microsecond delay
            '''

            for packet in self.packets:
                packet.delivery_time = packet.arrival_time + 3000
                packet.status = PacketStatus.DELIVERED
        
        elif self.service_mode_of_operation == "Mode 2":
            '''
            Mode 2: Mode for testing with a single Qbv window based on packet limits
                i.e only so many bytes can be served in a single Qbv window. The 
                number of packets that fit this number of bytes are served and the 
                rest are queued to be served in the next Qbv window. This mode assumes
                that in all cases the slot operates in reserved mode
            '''
            # Need allowed payload size
            # Need latency with allowed payload size
            # how does it handle MCS?
            assert 'payload_size' in kwargs, "Payload size not provided"
            assert 'delivery_latency' in kwargs, "Delivery latency not provided"
            
            UE_name = "UE" + str(self.ue_id)


            payload_size = kwargs['payload_size']
            delivery_latency = kwargs['delivery_latency']
            PER = kwargs['PER']
            for slot in base_schedule.schedule:
                if UE_name in base_schedule.schedule[slot].UEs:
                    # Get the packets that can be served in this slot
                    payload_used = 0
                    for packet in self.packets: # Relying on this being ordered by packet sequence number
                        if packet.arrival_time <= base_schedule.schedule[slot].start_time:
                            if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
                                or packet.status == PacketStatus.DROPPED):
                                # TODO: Currently, this assumes that there will always be more packets
                                # ready to be transmitted than payload_size. So, the delivery latency is
                                # always the maximum possible. However, if there are fewer packets than
                                # paylaod size, then the delivery latency will be lower
                                if payload_used + packet.size <= payload_size:
                                    # TODO: Add a guard interval
                                    # TODO: Implement number of retries-currently there are no retries
                                    # within the slot
                                    payload_used += packet.size
                                    if self.transmit_packet(PER):
                                        packet.delivery_time = base_schedule.schedule[slot].start_time + delivery_latency
                                        assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
                                            "Packet delivery time exceeds slot end time" 
                                        packet.status = PacketStatus.DELIVERED
                                    else:
                                        packet.status = PacketStatus.DROPPED
                                else:
                                    packet.status = PacketStatus.QUEUED
            

                        

# TODO: Write a network class
class Network:
    '''
    Class to represent the Wi-Fi network. This stores things like the slot parameters, handles
    DIFS and whatnot and serves the packets, especially useful when you have to deal with contention
    '''
    # TODO: change UEs to num_UEs and then have a function to generate UEs
    # TODO: add a function to generate the base 
    # TODO: Move the packet transmission function here

    def __init__(self, wifi_slot_time : float, DIFS: float, UEs: Dict[str, UE], debug_mode : bool) \
        -> None:
        '''
        Constructor for the Network class

        Args:
            wifi_slot_time (float): Duration of a slot in microseconds
            DIFS (float): Duration of the DIFS in microseconds
            UEs (Dict[UE]): Dictionary of UEs in the network indexed by "UE" + str(ue_id)
        '''
        self.wifi_slot_time = wifi_slot_time
        self.DIFS = DIFS
        self.UEs = UEs
        self.selected_UEs = []
        self.debug_mode = debug_mode

    
    
    
    def generate_max_weight_schedule(self, queue_lengths_this_slot, UEs_all, mode, \
                                    arrival_times, start_time):
        """
        Function that generates a max weight schedule for some of the next slots based on 
        the queue lengths, arrival times etc. of the packets the UEs possess
        """
        
        if mode == "max weight":
            # Sort the UEs in descending order of their queue lengths and return this array
            sorted_ue_names = [[key] for key in\
                            sorted(queue_lengths_this_slot, key=queue_lengths_this_slot.get, \
                                   reverse=True)]
            return sorted_ue_names
        
        elif mode == "oldest first":
            # Sort the UEs in ascending order of their arrival times and return this array
            # TODO: This creates an array that might consist of UEs whose packets haven't arrived yet
            # This will be handled by the UEs_with_packets array but it's use across multiple slots
            # when measurement is done only once per a few slots needs to be evaluated
            sorted_ue_names = [[key] for key in\
                            sorted(arrival_times, key=lambda k: arrival_times[k][0] \
                                    if arrival_times[k] else float('inf'))]
            return sorted_ue_names
        
        elif mode == "minimum latency":
            net_latency = {}
            for ue_name in UEs_all:
                net_latency[ue_name] = np.sum(np.array(arrival_times[ue_name][:queue_lengths_this_slot[ue_name]]) \
                                        - start_time)
            sorted_ue_names = [[key] for key in\
                            sorted(net_latency, key=net_latency.get)]
            return sorted_ue_names
                
                






    def serve_packets(self, base_schedule: Schedule, service_mode_of_operation: str, 
                      **kwargs) -> None:
        '''
        Function to serve the packets that the UEs have to transmit

        Args:
            base_schedule (Schedule): A base schedule specifying
                Qbv windows for different UEs across time
            service_mode_of_operation (str): Mode of operation of the UEs within 
                a Qbv window
        '''
        if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
            for ue in self.UEs:
                ue.serve_packets(base_schedule, **kwargs)

        ############### Mode 3 service mode of operation ######################
        elif service_mode_of_operation == "Mode 3":
            # Mode 3 handles contention as well, the behaviour is the same as Mode 2 in the reserved
            # slots but different in the contention slot
            # The following are the assumptions in the reserved slot:
                # Only one UE can transmit in the slot
                # All UEs have the same characteristics: payload size, delivery latency, PER
            # The following are the assumptions in the contetion slot:
            # 
            
            assert 'payload_size' in kwargs, "Payload size not provided"
            assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
                slots not provided"
            assert "contention" in kwargs['payload_size'], "Payload size for \
                contention slots not provided"
            assert 'delivery_latency' in kwargs, "Delivery latency not provided"
            assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
                reserved slots not provided"
            assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
                contention slots not provided"
            assert 'PER' in kwargs, "PER not provided"
            assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
            assert "contention" in kwargs['PER'], "PER for contention slots not provided"

            if "advance_time" in kwargs:
                advance_time = kwargs["advance_time"]
            else:
                advance_time = 1
            
            if self.debug_mode:
                print("advance time: ", advance_time)

            # Need to map PER to MCS somehow
            
            # TODO: maybe refactor the code to serve the reserved slots and contention slots
            # separately


            payload_size_reserved = kwargs['payload_size']["reserved"]
            payload_size_contention = kwargs['payload_size']["contention"]
            delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
            delivery_latency_contention = kwargs['delivery_latency']["contention"]
            PER_reserved = kwargs['PER']["reserved"]    
            PER_contention = kwargs['PER']["contention"]
            

            for slot in base_schedule.schedule:
                if base_schedule.schedule[slot].mode == "reserved":
                    assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
                    UE_name = base_schedule.schedule[slot].UEs[0]
                    # Get the packets that can be served in this slot
                    payload_used = 0
                    for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
                        if packet.arrival_time <= base_schedule.schedule[slot].start_time:
                            if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
                                or packet.status == PacketStatus.DROPPED):
                                # TODO: Currently, this assumes that there will always be more packets
                                # ready to be transmitted than payload_size. So, the delivery latency is
                                # always the maximum possible. However, if there are fewer packets than
                                # paylaod size, then the delivery latency will be lower
                                if payload_used + packet.size <= payload_size_reserved:
                                    # TODO: Add a guard interval
                                    # TODO: Implement number of retries-currently there are no retries
                                    # within the slot
                                    payload_used += packet.size
                                    if self.UEs[UE_name].transmit_packet(PER_reserved):
                                        packet.delivery_time = base_schedule.schedule[slot].start_time + \
                                                            delivery_latency_reserved
                                        assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
                                            "Packet delivery time exceeds slot end time" 
                                        packet.status = PacketStatus.DELIVERED
                                    else:
                                        packet.status = PacketStatus.DROPPED
                                else:
                                    packet.status = PacketStatus.QUEUED
                
                
                elif base_schedule.schedule[slot].mode == "contention":
                    start_time = base_schedule.schedule[slot].start_time
                    # Contend only with the spcified UEs
                    UEs_to_contend = base_schedule.schedule[slot].UEs

                    # Create queues of all packets to be trasmitted for each UE
                    # TODO: Check how this works when you have a mix of slots
                    packets_to_transmit = {}
                    for UE_name in UEs_to_contend:
                        packets_per_UE = []
                        for packet in self.UEs[UE_name].packets:
                            if packet.arrival_time <= base_schedule.schedule[slot].end_time:
                                # TODO: dropped and queued packets are treated the same way
                                if (packet.status == PacketStatus.ARRIVED 
                                    or packet.status == PacketStatus.QUEUED 
                                    or packet.status == PacketStatus.DROPPED):
                                    
                                    packets_per_UE.append(packet.sequence_number)
                        
                        packets_to_transmit[UE_name] = packets_per_UE




                    n_transmitted_array = []
                    while start_time < base_schedule.schedule[slot].end_time:
                        # Draw a random backoff time uniformly between 0 and CW for 
                        # each UE and return the minimum backoff time, if there is more than
                        # one UE with the same minimum backoff time, return that list of UEs1
                        # and then draw again
                        
                        
                        UEs_with_packets = []
                        for UE_name in UEs_to_contend:
                            if len(packets_to_transmit[UE_name]) > 0:
                                earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
                                if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
                                    UEs_with_packets.append(UE_name)
                            

                        if len(UEs_with_packets) > 0:
                            backoff_times = {}
                            for UE_name in UEs_with_packets:
                                # TODO: Maybe initialize RNG each time to get different backoff times
                                backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
                            min_backoff = min(backoff_times.values())
                            # TODO: Check if start_time + min_backoff is less than the end time of the slot
                            UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
                                            backoff_times[UE_name] == min_backoff]
                        else:
                            UEs_to_transmit = []
                            min_backoff = None


                        # backoff_times = {}
                        # for UE_name in UEs_to_contend:
                        #     # TODO: Maybe initialize RNG each time to get different backoff times
                        #     backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
                        # min_backoff = min(backoff_times.values())
                        # # TODO: Check if start_time + min_backoff is less than the end time of the slot
                        # UEs_winning_backoff = [UE_name for UE_name in UEs_to_contend if \
                        #                 backoff_times[UE_name] == min_backoff]
                        
                        # # CW_array = [self.UEs[UE_name].CW for UE_name in UEs_to_contend]
                        # # backoff_times = np.random.randint(0, CW_array)
                        # # min_backoff = np.min(backoff_times)
                        # # UEs_winning_backoff = np.array(UEs_to_contend)[backoff_times == min_backoff]

                        # assert len(UEs_winning_backoff) > 0, "No UEs to transmit"
                        
                        # # Check that at least one UE has a packet to transmit and if not,
                        # # advance the start_time by 1 and redo the backoff
                        # UEs_to_transmit = []
                        # for UE_name in UEs_winning_backoff:
                        #     if len(packets_to_transmit[UE_name]) > 0:
                        #         earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
                        #         if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
                        #             UEs_to_transmit.append(UE_name)
                                


                        # UEs_to_transmit = [UE_name for UE_name in UEs_winning_backoff if \
                        #                 any((packet.arrival_time <= start_time and  
                        #                     (packet.status == PacketStatus.ARRIVED 
                        #                     or packet.status == PacketStatus.QUEUED 
                        #                     or packet.status == PacketStatus.DROPPED)) \
                        #                     for packet in self.UEs[UE_name].packets)]


                        # save some debug information
                        self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
                                                  start_time, min_backoff, UEs_to_transmit])

                        n_packets_transmitted = 0
                        
                        if len(UEs_to_transmit) == 0:
                            start_time = start_time + advance_time
                            
                            # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
                            # the current start time 

                            if self.debug_mode:
                                print("start_time: ", start_time)

                        elif len(UEs_to_transmit) == 1:
                            # Transmit all packets that have arrived till this point (start_time)
                            delivery_time = start_time + delivery_latency_contention + \
                                            min_backoff*self.wifi_slot_time + self.DIFS
                            if delivery_time <= base_schedule.schedule[slot].end_time:
                                for UE_name in UEs_to_transmit:
                                    payload_used = 0
                                    # TODO: Check if the slice is being used correctly
                                    # TODO: Change the slice size once delivery time is calculated
                                    # dynamically
                                    for packet_sequence_number in packets_to_transmit[UE_name][:]:
                                        # TODO: Check if this packet is being used correctly
                                        packet = self.UEs[UE_name].packets[packet_sequence_number]
                                        if packet.arrival_time <= start_time:
                                            if payload_used + packet.size <= payload_size_contention:
                                                payload_used += packet.size 
                                                n_packets_transmitted += 1
                                                if self.UEs[UE_name].transmit_packet(PER_contention):
                                                    packet.delivery_time = delivery_time 
                                                    packet.status = PacketStatus.DELIVERED
                                                    packets_to_transmit[UE_name].remove(packet_sequence_number)
                                                else:
                                                    packet.status = PacketStatus.DROPPED
                                            else:
                                                break
                                        else:
                                            break



                                    # for packet in self.UEs[UE_name].packets:
                                    #     if packet.arrival_time <= start_time:
                                    #         if (packet.status == PacketStatus.ARRIVED 
                                    #             or packet.status == PacketStatus.QUEUED 
                                    #             or packet.status == PacketStatus.DROPPED):
                                    #             if payload_used + packet.size <= payload_size_contention:
                                    #                 payload_used += packet.size 
                                    #                 n_packets_transmitted += 1
                                    #                 if self.UEs[UE_name].transmit_packet(PER_contention):
                                    #                     packet.delivery_time = delivery_time 
                                    #                     packet.status = PacketStatus.DELIVERED
                                    #                     packets_to_transmit[UE_name].remove(packet.sequence_number)
                                    #                 else:
                                    #                     packet.status = PacketStatus.DROPPED
                                    #     else:
                                    #     # assume packets are in ascending order of arrival time
                                    #     # if you've already reached the packets that haven't arrived
                                    #     # then break and don't evaluate any further
                                    #         break
                                            
                                    # reset the contention window
                                    # TODO: You're skipping cases towards the end where delivery time
                                    # exceeds the end time of the slot. Need to fix this in the 
                                    # variable delivery latency case
                                    self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
                                    self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                                    self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                        .append(n_packets_transmitted)
                                    
                            if n_packets_transmitted > 0:
                                if self.debug_mode:
                                    print("start_time: ", start_time)

                                start_time = delivery_time 

                                if self.debug_mode:
                                    print("delivery_time: ", delivery_time)
                                    print("UEs: ", UEs_to_transmit)
                            elif n_packets_transmitted == 0:
                                start_time = start_time + advance_time
                                if self.debug_mode:
                                    # This gets triggered towards the end of the slot
                                    # as delivery time exceeds the end time of the slot 
                                    print("Should not happen! start_time (advanced): ", start_time)
                                    print("UEs: ", UEs_to_transmit)
                                    print("Line595 Delivery time: ", delivery_time)
                            # print("n_packets_transmitted : ", n_packets_transmitted)
                            n_transmitted_array.append(n_packets_transmitted)


                        else:
                            # TODO: Fix the case where UEs contend but there's some of them
                            # have no data to transmit, then exclude them from the list of
                            # UEs contending, prevent packets from being dropped and
                            # prevent the contention window from being doubled
                            delivery_time = start_time + delivery_latency_contention + \
                                            min_backoff*self.wifi_slot_time + self.DIFS
                            if delivery_time <= base_schedule.schedule[slot].end_time:
                                n_transmitted_old = 0 # TODO: remove the need for this by cleaning up the logic of the code
                                for UE_name in UEs_to_transmit: 
                                    payload_used = 0
                                    
                                    for packet_sequence_number in packets_to_transmit[UE_name][:]:
                                        # TODO: Check if this packet is being used correctly
                                        packet = self.UEs[UE_name].packets[packet_sequence_number]
                                        if packet.arrival_time <= start_time:
                                            if payload_used + packet.size <= payload_size_contention:
                                                payload_used += packet.size 
                                                n_packets_transmitted += 1
                                                packet.status = PacketStatus.DROPPED
                                            else:
                                                break
                                        else:
                                            break

                                    # for packet in self.UEs[UE_name].packets:
                                    #     if packet.arrival_time <= start_time:
                                    #         if (packet.status == PacketStatus.ARRIVED 
                                    #             or packet.status == PacketStatus.QUEUED 
                                    #             or packet.status == PacketStatus.DROPPED):
                                    #             if payload_used + packet.size <= payload_size_contention:
                                    #                 n_packets_transmitted += 1
                                    #                 payload_used += packet.size 
                                    #                 packet.status = PacketStatus.DROPPED
                                    #     else:
                                    #         break


                                    # double contention window for each UE
                                    if n_packets_transmitted > 0: 
                                    # TODO: enforce behaviour only if at least one packet is transmitted 
                                    # across all UEs. Avoids the case that no UE transmits and 
                                    # contention window is still doubled (Done by redefining UEs_to_transmit
                                    # from UEs_winning_backoff?)
                                        self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
                                                                self.UEs[UE_name].CWmax)
                                        
                                    self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
                                    self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                                    self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                        .append(n_packets_transmitted - n_transmitted_old)
                                    n_transmitted_old = n_packets_transmitted
                                        

                            # TODO: there is a corner case where a UE's backoff might finish just
                            # after the end of delivery_time in which case it should transmit
                            # right away instead of starting again
                            if n_packets_transmitted > 0:
                                if self.debug_mode:
                                    print("start_time: ", start_time)

                                start_time = delivery_time

                                if self.debug_mode:
                                    print("delivery_time: ", delivery_time)
                                    print("UEs: ", UEs_to_transmit)
                            elif n_packets_transmitted == 0:
                                start_time = start_time + 1
                                if self.debug_mode:
                                    # This gets triggered towards the end of the slot
                                    # as delivery time exceeds the end time of the slot
                                    print("Should not happen! start_time: ", start_time)
                                    print("UEs: ", UEs_to_transmit)
                                    print("Line647 Delivery time: ", delivery_time)

                    print("Mean packets transmitted: ", np.mean(n_transmitted_array))
                    # print("array of transmission numbers: ", n_transmitted_array)
        
        
        ############### Mode 4 service mode of operation ######################
        
        
        elif service_mode_of_operation == "Mode 4":
            # Mode 4 is still contention as in Mode 3 but allows UEs to transmit dynamic 
            # number of packets 
            
            assert 'payload_size' in kwargs, "Payload size not provided"
            assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
                slots not provided"
            assert "contention" in kwargs['payload_size'], "Payload size for \
                contention slots not provided"
            assert 'delivery_latency' in kwargs, "Delivery latency not provided"
            assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
                reserved slots not provided"
            assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
                contention slots not provided"
            assert 'PER' in kwargs, "PER not provided"
            assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
            assert "contention" in kwargs['PER'], "PER for contention slots not provided"
            assert "aggregation_limit" in kwargs, "aggregation_limit not provided"
            

            if "advance_time" in kwargs:
                advance_time = kwargs["advance_time"]
            else:
                advance_time = 1
            
            if self.debug_mode:
                print("advance time: ", advance_time)

            # Need to map PER to MCS somehow
            
            # TODO: maybe refactor the code to serve the reserved slots and contention slots
            # separately

            # TODO: Fix this delivery latency contention and make it an array
            # TODO: we will need a more complicate setup for when different UEs have different
            # MCSes, packet sizes and PERs
            payload_size_reserved = kwargs['payload_size']["reserved"]
            payload_size_contention = kwargs['payload_size']["contention"]
            delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
            delivery_latency_contention = kwargs['delivery_latency']["contention"]
            PER_reserved = kwargs['PER']["reserved"]    
            PER_contention = kwargs['PER']["contention"]
            aggregation_limit = kwargs['aggregation_limit']

            assert len(delivery_latency_contention) > 1, "Deliver latency is an array"
            

            UEs_all = set()
            for slot in base_schedule.schedule:
                UEs_all.update(base_schedule.schedule[slot].UEs)
            
            if self.debug_mode:
                print("UEs for queue measurement: ", UEs_all)

            # Create queues of all packets to be trasmitted for each UE
            # TODO: Check how this works when you have a mix of slots
            packets_to_transmit = {}
            arrival_times = {}
            # for UE_name in UEs_all:
            for UE_name in UEs_all:
                packets_per_UE = []
                arrivals_per_UE = []
                for packet in self.UEs[UE_name].packets:
                    if packet.arrival_time <= base_schedule.end_time:
                        # TODO: dropped and queued packets are treated the same way
                        if (packet.status == PacketStatus.ARRIVED 
                            or packet.status == PacketStatus.QUEUED 
                            or packet.status == PacketStatus.DROPPED):
                            
                            packets_per_UE.append(packet.sequence_number)
                            arrivals_per_UE.append(packet.arrival_time)
                    else: 
                        break
                
                packets_to_transmit[UE_name] = packets_per_UE
                arrival_times[UE_name] = arrivals_per_UE




            for slot in base_schedule.schedule:
                if base_schedule.schedule[slot].mode == "reserved":
                    assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
                    UE_name = base_schedule.schedule[slot].UEs[0]
                    # Get the packets that can be served in this slot
                    payload_used = 0
                    for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
                        if packet.arrival_time <= base_schedule.schedule[slot].start_time:
                            if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
                                or packet.status == PacketStatus.DROPPED):
                                # TODO: Currently, this assumes that there will always be more packets
                                # ready to be transmitted than payload_size. So, the delivery latency is
                                # always the maximum possible. However, if there are fewer packets than
                                # paylaod size, then the delivery latency will be lower
                                if payload_used + packet.size <= payload_size_reserved:
                                    # TODO: Add a guard interval
                                    # TODO: Implement number of retries-currently there are no retries
                                    # within the slot
                                    payload_used += packet.size
                                    if self.UEs[UE_name].transmit_packet(PER_reserved):
                                        packet.delivery_time = base_schedule.schedule[slot].start_time + \
                                                            delivery_latency_reserved
                                        assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
                                            "Packet delivery time exceeds slot end time" 
                                        packet.status = PacketStatus.DELIVERED
                                    else:
                                        packet.status = PacketStatus.DROPPED
                                else:
                                    packet.status = PacketStatus.QUEUED
                
                
                elif base_schedule.schedule[slot].mode == "contention":
                    start_time = base_schedule.schedule[slot].start_time
                    # Contend only with the spcified UEs
                    UEs_to_contend = copy.deepcopy(base_schedule.schedule[slot].UEs)

                    n_transmitted_array = []
                    queue_measurement_time = start_time

                    # Measure queues at the start of the slot
                    # for UE_name in UEs_all:
                    max_queue_length = 0
                    queue_lengths_this_slot = []
                    for UE_name in UEs_all:
                        queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
                        queue_lengths_this_slot.append(queue_length)
                        self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
                        self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
                        if queue_length > max_queue_length:
                            max_queue_length = queue_length
                    
                    if len(UEs_to_contend) == 0:
                        if max_queue_length == 0:
                            UEs_to_contend = copy.deepcopy(UEs_all)
                        else:
                            for UE_name in UEs_all:
                                if self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"][-1] == max_queue_length:
                                    UEs_to_contend.append(UE_name)
                                    break
                        if self.debug_mode:
                            print("\n\nstart time: ", start_time)
                            print("UEs to contend after max weight: ", UEs_to_contend)
                            print("queue lengths:",queue_lengths_this_slot)
                    else:
                        if self.debug_mode:
                            print("\n\nstart time: ", start_time)
                            print("UEs to contend, NO max weight: ", UEs_to_contend)
                            print("queue lengths:", queue_lengths_this_slot)



                    while start_time < base_schedule.schedule[slot].end_time:
                        # Draw a random backoff time uniformly between 0 and CW for 
                        # each UE and return the minimum backoff time, if there is more than
                        # one UE with the same minimum backoff time, return that list of UEs1
                        # and then draw again
                        

                        if start_time - queue_measurement_time >= 1000:
                            # for UE_name in UEs_all:
                            for UE_name in UEs_all:
                                queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
                                self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
                                self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
                            queue_measurement_time = start_time

                        
                        UEs_with_packets = []
                        for UE_name in UEs_to_contend:
                            if len(packets_to_transmit[UE_name]) > 0:
                                earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
                                if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
                                    UEs_with_packets.append(UE_name)
                            

                        if len(UEs_with_packets) > 0:
                            backoff_times = {}
                            for UE_name in UEs_with_packets:
                                # TODO: Maybe initialize RNG each time to get different backoff times
                                backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
                            min_backoff = min(backoff_times.values())
                            # TODO: Check if start_time + min_backoff is less than the end time of the slot
                            UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
                                            backoff_times[UE_name] == min_backoff]
                        else:
                            UEs_to_transmit = []
                            min_backoff = None

                        # save some debug information
                        if self.debug_mode:
                            self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
                                                    start_time, min_backoff, UEs_to_transmit])
                        
                        # TODO: remove this
                        n_packets_transmitted = 0

                        
                        if len(UEs_to_transmit) == 0:
                            start_time = start_time + advance_time
                            if start_time > base_schedule.schedule[slot].end_time:
                                start_time = base_schedule.schedule[slot].end_time
                            
                            # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
                            # the current start time 

                            if self.debug_mode:
                                print("start_time: ", start_time)
                                print("UEs: ", UEs_to_transmit)

                        elif len(UEs_to_transmit) == 1:
                            # Transmit all packets that have arrived till this point (start_time)
                            UE_name = UEs_to_transmit[0]

                            # Determine delivery time
                            time_remaining = base_schedule.schedule[slot].end_time - start_time - \
                                            min_backoff*self.wifi_slot_time - self.DIFS
                            max_packets_time_remaining = bisect.bisect_right(\
                                delivery_latency_contention, time_remaining)
                            max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
                            n_packets_transmitted = 0

                            if self.debug_mode:
                                print("\nUE_name: ", UE_name)
                                print("end_time: ", base_schedule.schedule[slot].end_time)
                                print("start_time: ", start_time)
                                print("min_backoff: ", min_backoff)
                                print("DIFS: ", self.DIFS)
                                print("wifi_slot_time: ", self.wifi_slot_time)
                                print("time_remaining: ", time_remaining)
                                print("max_packets_time_remaining: ", max_packets_time_remaining)
                                print("max_packets_allowed: ", max_packets_allowed)

                                

                            if max_packets_allowed == 0:
                                # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
                                n_packets_transmitted = 0
                            else:
                                while (n_packets_transmitted < max_packets_allowed and 
                                       n_packets_transmitted < len(packets_to_transmit[UE_name])):
                                    if self.debug_mode:
                                        print("n_packets_transmitted: ", n_packets_transmitted)
                                        print("packet_sequence_number: ", packets_to_transmit[UE_name][n_packets_transmitted])
                                        print(" packets_to_transmit[UE_name][:10]: ",  packets_to_transmit[UE_name][:10])
                                        print("arrival_times[UE_name][:10]: ", arrival_times[UE_name][:10])

                                    packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
                                    packet = self.UEs[UE_name].packets[packet_sequence_number]
                                    if packet.arrival_time <= start_time:
                                        n_packets_transmitted += 1
                                    else:
                                        break
                                
                                # TODO: check indexing of delivery_latency_contention
                                delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
                                                min_backoff*self.wifi_slot_time + self.DIFS
                                
                                for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
                                    packet = self.UEs[UE_name].packets[packet_sequence_number]
                                    if self.UEs[UE_name].transmit_packet(PER_contention):
                                        packet.delivery_time = delivery_time 
                                        packet.status = PacketStatus.DELIVERED
                                        packets_to_transmit[UE_name].remove(packet_sequence_number)
                                        arrival_times[UE_name].remove(packet.arrival_time)
                                        assert len(arrival_times[UE_name]) == len(packets_to_transmit[UE_name]), \
                                            "Arrival times and packets to transmit are not the same length"
                                    else:
                                        packet.status = PacketStatus.DROPPED
                                
                                self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
                                self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                                self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                    .append(n_packets_transmitted)
                                    
                            if n_packets_transmitted > 0:
                                if self.debug_mode:
                                    print("start_time: ", start_time)

                                start_time = delivery_time 

                                if self.debug_mode:
                                    print("delivery_time: ", delivery_time)
                                    print("UEs: ", UEs_to_transmit)
                                    print("\n")
                            elif n_packets_transmitted == 0:
                                if max_packets_time_remaining == 0:
                                    start_time = base_schedule.schedule[slot].end_time
                                    if self.debug_mode:
                                        print("Start time advanced to end")
                                        print("Single UE, no packets transmitted")
                                        print("start_time: ", start_time)
                                else:
                                    start_time = start_time + advance_time
                                    if self.debug_mode:
                                        # This gets triggered towards the end of the slot
                                        # as delivery time exceeds the end time of the slot 
                                        print("Should not happen! start_time (advanced): ", start_time)
                                        print("UEs: ", UEs_to_transmit)
                                        print("\n")

                            # print("n_packets_transmitted : ", n_packets_transmitted)
                            n_transmitted_array.append(n_packets_transmitted)


                        else:
                            # TODO: Fix the case where UEs contend but there's some of them
                            # have no data to transmit, then exclude them from the list of
                            # UEs contending, prevent packets from being dropped and
                            # prevent the contention window from being doubled
                            delivery_times = []
                            n_packets_transmitted_per_UE = []
                            time_remaining = base_schedule.schedule[slot].end_time - start_time - \
                                            min_backoff*self.wifi_slot_time - self.DIFS
                            # TODO: Make delivery_latency_contention different for different UEs
                            # using different MCSes
                            max_packets_time_remaining = bisect.bisect_right(\
                                delivery_latency_contention, time_remaining)
                            # TODO: Make aggregation different for different UEs
                            max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)

                            if self.debug_mode:
                                print("end_time: ", base_schedule.schedule[slot].end_time)
                                print("start_time: ", start_time)
                                print("min_backoff: ", min_backoff)
                                print("DIFS: ", self.DIFS)
                                print("wifi_slot_time: ", self.wifi_slot_time)
                                print("time_remaining: ", time_remaining)
                                print("max_packets_time_remaining: ", max_packets_time_remaining)
                                print("max_packets_allowed: ", max_packets_allowed)
                            
                            for UE_name in UEs_to_transmit:
                                n_packets_transmitted = 0
                                if max_packets_allowed == 0:
                                # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
                                    n_packets_transmitted = 0
                                else:
                                    while (n_packets_transmitted < max_packets_allowed and 
                                       n_packets_transmitted < len(packets_to_transmit[UE_name])):
                                        if self.debug_mode:
                                            print("n_packets_transmitted: ", n_packets_transmitted)
                                            print("UE_name: ", UE_name)

                                        packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
                                        packet = self.UEs[UE_name].packets[packet_sequence_number]
                                        if packet.arrival_time <= start_time:
                                            n_packets_transmitted += 1
                                        else:
                                            break
                                    
                                    # TODO: check indexing of delivery_latency_contention
                                    delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
                                                    min_backoff*self.wifi_slot_time + self.DIFS
                                    delivery_times.append(delivery_time)


                                    for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
                                        packet = self.UEs[UE_name].packets[packet_sequence_number]
                                        packet.status = PacketStatus.DROPPED

                                    if n_packets_transmitted > 0: 
                                    # TODO: enforce behaviour only if at least one packet is transmitted 
                                    # across all UEs. Avoids the case that no UE transmits and 
                                    # contention window is still doubled (Done by redefining UEs_to_transmit
                                    # from UEs_winning_backoff?)
                                        self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
                                                                self.UEs[UE_name].CWmax)
                                    
                                    self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
                                    self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                                    self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                        .append(n_packets_transmitted)
                                

                                
                                n_packets_transmitted_per_UE.append(n_packets_transmitted)

                            total_packets_transmitted = sum(n_packets_transmitted_per_UE)
                            if total_packets_transmitted > 0:
                                if self.debug_mode:
                                    print("start_time: ", start_time)

                                start_time = max(delivery_times)

                                if self.debug_mode:
                                    print("delivery_time: ", delivery_times)
                                    print("UEs: ", UEs_to_transmit)
                                    print("\n")
                            elif total_packets_transmitted == 0:
                                if max_packets_time_remaining == 0:
                                    start_time = base_schedule.schedule[slot].end_time
                                    if self.debug_mode:
                                        print("Start time advanced to end")
                                        print("Single UE, no packets transmitted")
                                        print("start_time: ", start_time)
                                else:
                                    start_time = start_time + advance_time
                                    if self.debug_mode:
                                        # This gets triggered towards the end of the slot
                                        # as delivery time exceeds the end time of the slot
                                        print("Should not happen! start_time: ", start_time)
                                        print("UEs: ", UEs_to_transmit)
                                        print("Line collision Delivery time: ", delivery_times)
                                        print("\n")

                    # print("Mean packets transmitted: ", np.mean(n_transmitted_array))
                    # print("array of transmission numbers: ", n_transmitted_array)

        ############### Max weight mode of service mode of operation ######################
        
        
        # This is various versions of max weight scheduling with different parameters instead of
        # weight being used. The effect of overheads is also evaluated. 
        
        elif service_mode_of_operation == "Max weight":
            # Mode 4 is still contention as in Mode 3 but allows UEs to transmit dynamic 
            # number of packets 
            
            assert 'payload_size' in kwargs, "Payload size not provided"
            assert "contention" in kwargs['payload_size'], "Payload size for \
                contention slots not provided"
            assert 'delivery_latency' in kwargs, "Delivery latency not provided"
            assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
                contention slots not provided"
            assert 'PER' in kwargs, "PER not provided"
            assert "contention" in kwargs['PER'], "PER for contention slots not provided"
            assert "aggregation_limit" in kwargs, "aggregation_limit not provided"
            

            if "advance_time" in kwargs:
                advance_time = kwargs["advance_time"]
            else:
                advance_time = 1
            
            if self.debug_mode:
                print("advance time: ", advance_time)

            # Need to map PER to MCS somehow
            
            # TODO: maybe refactor the code to serve the reserved slots and contention slots
            # separately

            # TODO: Fix this delivery latency contention and make it an array
            # TODO: we will need a more complicate setup for when different UEs have different
            # MCSes, packet sizes and PERs
            payload_size_contention = kwargs['payload_size']["contention"]
            delivery_latency_contention = kwargs['delivery_latency']["contention"]
            PER_contention = kwargs['PER']["contention"]
            aggregation_limit = kwargs['aggregation_limit']

            assert len(delivery_latency_contention) > 1, "Deliver latency is an array"
            

            UEs_all = set()
            for slot in base_schedule.schedule:
                UEs_all.update(base_schedule.schedule[slot].UEs)
            
            if self.debug_mode:
                print("UEs for queue measurement: ", UEs_all)

            # Create queues of all packets to be trasmitted for each UE
            # TODO: Check how this works when you have a mix of slots
            packets_to_transmit = {}
            arrival_times = {}
            # for UE_name in UEs_all:
            for UE_name in UEs_all:
                packets_per_UE = []
                arrivals_per_UE = []
                for packet in self.UEs[UE_name].packets:
                    if packet.arrival_time <= base_schedule.end_time:
                        # TODO: dropped and queued packets are treated the same way
                        if (packet.status == PacketStatus.ARRIVED 
                            or packet.status == PacketStatus.QUEUED 
                            or packet.status == PacketStatus.DROPPED):
                            
                            packets_per_UE.append(packet.sequence_number)
                            arrivals_per_UE.append(packet.arrival_time)
                    else: 
                        break
                
                packets_to_transmit[UE_name] = packets_per_UE
                arrival_times[UE_name] = arrivals_per_UE


            UEs_schedule_to_use = 0
            UEs_schedule = []

            for slot in base_schedule.schedule:                
                start_time = base_schedule.schedule[slot].start_time
                    # Contend only with the spcified UEs

                n_transmitted_array = []
                queue_measurement_time = start_time

                # Measure queues at the start of the slot

                queue_lengths_this_slot = {}
                for UE_name in UEs_all:
                    queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
                    queue_lengths_this_slot[UE_name] = queue_length
                    self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
                    self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
                    

                if base_schedule.schedule[slot].mode != "contention":
                    UEs_schedule = self.generate_max_weight_schedule(queue_lengths_this_slot,\
                                                                UEs_all, \
                                                                base_schedule.schedule[slot].mode, \
                                                                arrival_times,\
                                                                start_time)
                    start_time = base_schedule.schedule[slot].end_time
                    UEs_schedule_to_use = 0
                    
                elif base_schedule.schedule[slot].mode == "contention":
                    if len(UEs_schedule) == 0:
                        UEs_to_contend = copy.deepcopy(UEs_all)
                    else: 
                        UEs_to_contend = UEs_schedule[UEs_schedule_to_use%len(UEs_schedule)]
                        UEs_schedule_to_use += 1
                        # if len(UEs_to_contend) == 0:
                        #     if max_queue_length == 0:
                        #         UEs_to_contend = copy.deepcopy(UEs_all)
                        #     else:
                        #         for UE_name in UEs_all:
                        #             if self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"][-1] == max_queue_length:
                        #                 UEs_to_contend.append(UE_name)
                        #                 break
                        if self.debug_mode:
                            print("\n\nstart time: ", start_time)
                            print("UEs to contend after max weight: ", UEs_to_contend)
                            print("queue lengths:",queue_lengths_this_slot)
                        



                while start_time < base_schedule.schedule[slot].end_time:
                    # Draw a random backoff time uniformly between 0 and CW for 
                    # each UE and return the minimum backoff time, if there is more than
                    # one UE with the same minimum backoff time, return that list of UEs1
                    # and then draw again
                    
                    # TODO: Fix this repeated queue measurement, the queue is already measured
                    # at the start of the slot for both contention and measurement case
                    if start_time - queue_measurement_time >= 1000:
                        # for UE_name in UEs_all:
                        for UE_name in UEs_all:
                            queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
                            self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
                            self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
                        queue_measurement_time = start_time

                    
                    UEs_with_packets = []
                    for UE_name in UEs_to_contend:
                        if len(packets_to_transmit[UE_name]) > 0:
                            earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
                            if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
                                UEs_with_packets.append(UE_name)
                        

                    if len(UEs_with_packets) > 0:
                        backoff_times = {}
                        for UE_name in UEs_with_packets:
                            # TODO: Maybe initialize RNG each time to get different backoff times
                            backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
                        min_backoff = min(backoff_times.values())
                        # TODO: Check if start_time + min_backoff is less than the end time of the slot
                        UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
                                        backoff_times[UE_name] == min_backoff]
                    else:
                        UEs_to_transmit = []
                        min_backoff = None

                    # save some debug information
                    if self.debug_mode:
                        self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
                                                start_time, min_backoff, UEs_to_transmit])
                    
                    # TODO: remove this
                    n_packets_transmitted = 0

                    
                    if len(UEs_to_transmit) == 0:
                        start_time = start_time + advance_time
                        if start_time > base_schedule.schedule[slot].end_time:
                            start_time = base_schedule.schedule[slot].end_time
                        
                        # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
                        # the current start time 

                        if self.debug_mode:
                            print("start_time: ", start_time)
                            print("UEs: ", UEs_to_transmit)

                    elif len(UEs_to_transmit) == 1:
                        # Transmit all packets that have arrived till this point (start_time)
                        UE_name = UEs_to_transmit[0]

                        # Determine delivery time
                        time_remaining = base_schedule.schedule[slot].end_time - start_time - \
                                        min_backoff*self.wifi_slot_time - self.DIFS
                        max_packets_time_remaining = bisect.bisect_right(\
                            delivery_latency_contention, time_remaining)
                        max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
                        n_packets_transmitted = 0

                        if self.debug_mode:
                            print("\nUE_name: ", UE_name)
                            print("end_time: ", base_schedule.schedule[slot].end_time)
                            print("start_time: ", start_time)
                            print("min_backoff: ", min_backoff)
                            print("DIFS: ", self.DIFS)
                            print("wifi_slot_time: ", self.wifi_slot_time)
                            print("time_remaining: ", time_remaining)
                            print("max_packets_time_remaining: ", max_packets_time_remaining)
                            print("max_packets_allowed: ", max_packets_allowed)

                            

                        if max_packets_allowed == 0:
                            # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
                            n_packets_transmitted = 0
                        else:
                            while (n_packets_transmitted < max_packets_allowed and 
                                    n_packets_transmitted < len(packets_to_transmit[UE_name])):
                                if self.debug_mode:
                                    print("n_packets_transmitted: ", n_packets_transmitted)
                                    print("packet_sequence_number: ", packets_to_transmit[UE_name][n_packets_transmitted])
                                    print(" packets_to_transmit[UE_name][:10]: ",  packets_to_transmit[UE_name][:10])
                                    print("arrival_times[UE_name][:10]: ", arrival_times[UE_name][:10])

                                packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
                                packet = self.UEs[UE_name].packets[packet_sequence_number]
                                if packet.arrival_time <= start_time:
                                    n_packets_transmitted += 1
                                else:
                                    break
                            
                            # TODO: check indexing of delivery_latency_contention
                            delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
                                            min_backoff*self.wifi_slot_time + self.DIFS
                            
                            for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
                                packet = self.UEs[UE_name].packets[packet_sequence_number]
                                if self.UEs[UE_name].transmit_packet(PER_contention):
                                    packet.delivery_time = delivery_time 
                                    packet.status = PacketStatus.DELIVERED
                                    packets_to_transmit[UE_name].remove(packet_sequence_number)
                                    arrival_times[UE_name].remove(packet.arrival_time)
                                    assert len(arrival_times[UE_name]) == len(packets_to_transmit[UE_name]), \
                                        "Arrival times and packets to transmit are not the same length"
                                else:
                                    packet.status = PacketStatus.DROPPED
                            
                            self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
                            self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                            self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                .append(n_packets_transmitted)
                                
                        if n_packets_transmitted > 0:
                            if self.debug_mode:
                                print("start_time: ", start_time)

                            start_time = delivery_time 

                            if self.debug_mode:
                                print("delivery_time: ", delivery_time)
                                print("UEs: ", UEs_to_transmit)
                                print("\n")
                        elif n_packets_transmitted == 0:
                            if max_packets_time_remaining == 0:
                                start_time = base_schedule.schedule[slot].end_time
                                if self.debug_mode:
                                    print("Start time advanced to end")
                                    print("Single UE, no packets transmitted")
                                    print("start_time: ", start_time)
                            else:
                                start_time = start_time + advance_time
                                if self.debug_mode:
                                    # This gets triggered towards the end of the slot
                                    # as delivery time exceeds the end time of the slot 
                                    print("Should not happen! start_time (advanced): ", start_time)
                                    print("UEs: ", UEs_to_transmit)
                                    print("\n")

                        # print("n_packets_transmitted : ", n_packets_transmitted)
                        n_transmitted_array.append(n_packets_transmitted)


                    else:
                        # TODO: Fix the case where UEs contend but there's some of them
                        # have no data to transmit, then exclude them from the list of
                        # UEs contending, prevent packets from being dropped and
                        # prevent the contention window from being doubled
                        delivery_times = []
                        n_packets_transmitted_per_UE = []
                        time_remaining = base_schedule.schedule[slot].end_time - start_time - \
                                        min_backoff*self.wifi_slot_time - self.DIFS
                        # TODO: Make delivery_latency_contention different for different UEs
                        # using different MCSes
                        max_packets_time_remaining = bisect.bisect_right(\
                            delivery_latency_contention, time_remaining)
                        # TODO: Make aggregation different for different UEs
                        max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)

                        if self.debug_mode:
                            print("end_time: ", base_schedule.schedule[slot].end_time)
                            print("start_time: ", start_time)
                            print("min_backoff: ", min_backoff)
                            print("DIFS: ", self.DIFS)
                            print("wifi_slot_time: ", self.wifi_slot_time)
                            print("time_remaining: ", time_remaining)
                            print("max_packets_time_remaining: ", max_packets_time_remaining)
                            print("max_packets_allowed: ", max_packets_allowed)
                        
                        for UE_name in UEs_to_transmit:
                            n_packets_transmitted = 0
                            if max_packets_allowed == 0:
                            # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
                                n_packets_transmitted = 0
                            else:
                                while (n_packets_transmitted < max_packets_allowed and 
                                    n_packets_transmitted < len(packets_to_transmit[UE_name])):
                                    if self.debug_mode:
                                        print("n_packets_transmitted: ", n_packets_transmitted)
                                        print("UE_name: ", UE_name)

                                    packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
                                    packet = self.UEs[UE_name].packets[packet_sequence_number]
                                    if packet.arrival_time <= start_time:
                                        n_packets_transmitted += 1
                                    else:
                                        break
                                
                                # TODO: check indexing of delivery_latency_contention
                                delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
                                                min_backoff*self.wifi_slot_time + self.DIFS
                                delivery_times.append(delivery_time)


                                for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
                                    packet = self.UEs[UE_name].packets[packet_sequence_number]
                                    packet.status = PacketStatus.DROPPED

                                if n_packets_transmitted > 0: 
                                # TODO: enforce behaviour only if at least one packet is transmitted 
                                # across all UEs. Avoids the case that no UE transmits and 
                                # contention window is still doubled (Done by redefining UEs_to_transmit
                                # from UEs_winning_backoff?)
                                    self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
                                                            self.UEs[UE_name].CWmax)
                                
                                self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
                                self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
                                self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
                                    .append(n_packets_transmitted)
                            

                            
                            n_packets_transmitted_per_UE.append(n_packets_transmitted)

                        total_packets_transmitted = sum(n_packets_transmitted_per_UE)
                        if total_packets_transmitted > 0:
                            if self.debug_mode:
                                print("start_time: ", start_time)

                            start_time = max(delivery_times)

                            if self.debug_mode:
                                print("delivery_time: ", delivery_times)
                                print("UEs: ", UEs_to_transmit)
                                print("\n")
                        elif total_packets_transmitted == 0:
                            if max_packets_time_remaining == 0:
                                start_time = base_schedule.schedule[slot].end_time
                                if self.debug_mode:
                                    print("Start time advanced to end")
                                    print("Single UE, no packets transmitted")
                                    print("start_time: ", start_time)
                            else:
                                start_time = start_time + advance_time
                                if self.debug_mode:
                                    # This gets triggered towards the end of the slot
                                    # as delivery time exceeds the end time of the slot
                                    print("Should not happen! start_time: ", start_time)
                                    print("UEs: ", UEs_to_transmit)
                                    print("Line collision Delivery time: ", delivery_times)
                                    print("\n")

                # print("Mean packets transmitted: ", np.mean(n_transmitted_array))
                # print("array of transmission numbers: ", n_transmitted_array)
                


## Miscellanous functions
                                    
# Write a function to compute the 99th percentile of the latencies given an array of latencies

def compute_percentile(latencies: List[float], percentile: int) -> float:
    '''
    Function to compute the percentile of the latencies

    Args:
        latencies (List[float]): List of latencies
        percentile (int): Percentile to compute

    Returns:
        float: The percentile of the latencies
    '''
    return np.percentile(latencies, percentile)                                    
