# Necessary imports

from enum import Enum
import matplotlib.pyplot as plt
import numpy as np
import typing
from typing import List, Tuple, Dict, Optional




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
            f"Arrival Time: {self.arrival_time} microseconds), "
            f"Delivery Time: {self.delivery_time} microseconds), "
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
                service_mode_of_operation: str, n_packets : Optional[int]) -> None:
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

    def __str__(self) -> str:
        '''
        Function to print the UE
        '''
        output = (f"UE(UE ID: {self.ue_id}, "
            f"UE(MCS: {self.mcs}, "
            f"Network mode of Operation: {self.network_mode_of_operation}, "
            f"Service mode of Operation: {self.service_mode_of_operation}, "
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
                rest are queued to be served in the next Qbv window
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
                    for packet in self.packets: # Relying on this being ordered by sequence number
                        if packet.arrival_time <= base_schedule.schedule[slot].start_time:
                            if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
                                or packet.status == PacketStatus.DROPPED):
                                if payload_used + packet.size <= payload_size:
                                    # TODO: Add a guard interval
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
