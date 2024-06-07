Timer unit: 1e-09 s

Total time: 41.8554 s
File: /Users/milindkumarvaddiraju/projects/HVC_use/WTSN/simulation/network_classes.py
Function: serve_packets at line 442

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   442                                               def serve_packets(self, base_schedule: Schedule, service_mode_of_operation: str, 
   443                                                                 **kwargs) -> None:
   444                                                   '''
   445                                                   Function to serve the packets that the UEs have to transmit
   446                                           
   447                                                   Args:
   448                                                       base_schedule (Schedule): A base schedule specifying
   449                                                           Qbv windows for different UEs across time
   450                                                       service_mode_of_operation (str): Mode of operation of the UEs within 
   451                                                           a Qbv window
   452                                                   '''
   453         1       2000.0   2000.0      0.0          if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
   454                                                       for ue in self.UEs:
   455                                                           ue.serve_packets(base_schedule, **kwargs)
   456         1       1000.0   1000.0      0.0          elif service_mode_of_operation == "Mode 3":
   457                                                       # Mode 3 handles contention as well, the behaviour is the same as Mode 2 in the reserved
   458                                                       # slots but different in the contention slot
   459                                                       # The following are the assumptions in the reserved slot:
   460                                                           # Only one UE can transmit in the slot
   461                                                           # All UEs have the same characteristics: payload size, delivery latency, PER
   462                                                       # The following are the assumptions in the contetion slot:
   463                                                       # 
   464                                                       
   465                                                       assert 'payload_size' in kwargs, "Payload size not provided"
   466                                                       assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   467                                                           slots not provided"
   468                                                       assert "contention" in kwargs['payload_size'], "Payload size for \
   469                                                           contention slots not provided"
   470                                                       assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   471                                                       assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   472                                                           reserved slots not provided"
   473                                                       assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   474                                                           contention slots not provided"
   475                                                       assert 'PER' in kwargs, "PER not provided"
   476                                                       assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   477                                                       assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   478                                           
   479                                                       if "advance_time" in kwargs:
   480                                                           advance_time = kwargs["advance_time"]
   481                                                       else:
   482                                                           advance_time = 1
   483                                                       
   484                                                       if self.debug_mode:
   485                                                           print("advance time: ", advance_time)
   486                                           
   487                                                       # Need to map PER to MCS somehow
   488                                                       
   489                                                       # TODO: maybe refactor the code to serve the reserved slots and contention slots
   490                                                       # separately
   491                                           
   492                                           
   493                                                       payload_size_reserved = kwargs['payload_size']["reserved"]
   494                                                       payload_size_contention = kwargs['payload_size']["contention"]
   495                                                       delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   496                                                       delivery_latency_contention = kwargs['delivery_latency']["contention"]
   497                                                       PER_reserved = kwargs['PER']["reserved"]    
   498                                                       PER_contention = kwargs['PER']["contention"]
   499                                                       
   500                                           
   501                                                       for slot in base_schedule.schedule:
   502                                                           if base_schedule.schedule[slot].mode == "reserved":
   503                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   504                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   505                                                               # Get the packets that can be served in this slot
   506                                                               payload_used = 0
   507                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   508                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   509                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   510                                                                           or packet.status == PacketStatus.DROPPED):
   511                                                                           # TODO: Currently, this assumes that there will always be more packets
   512                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   513                                                                           # always the maximum possible. However, if there are fewer packets than
   514                                                                           # paylaod size, then the delivery latency will be lower
   515                                                                           if payload_used + packet.size <= payload_size_reserved:
   516                                                                               # TODO: Add a guard interval
   517                                                                               # TODO: Implement number of retries-currently there are no retries
   518                                                                               # within the slot
   519                                                                               payload_used += packet.size
   520                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   521                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   522                                                                                                       delivery_latency_reserved
   523                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   524                                                                                       "Packet delivery time exceeds slot end time" 
   525                                                                                   packet.status = PacketStatus.DELIVERED
   526                                                                               else:
   527                                                                                   packet.status = PacketStatus.DROPPED
   528                                                                           else:
   529                                                                               packet.status = PacketStatus.QUEUED
   530                                                           
   531                                                           
   532                                                           elif base_schedule.schedule[slot].mode == "contention":
   533                                                               start_time = base_schedule.schedule[slot].start_time
   534                                                               # Contend only with the spcified UEs
   535                                                               UEs_to_contend = base_schedule.schedule[slot].UEs
   536                                           
   537                                                               # Create queues of all packets to be trasmitted for each UE
   538                                                               # TODO: Check how this works when you have a mix of slots
   539                                                               packets_to_transmit = {}
   540                                                               for UE_name in UEs_to_contend:
   541                                                                   packets_per_UE = []
   542                                                                   for packet in self.UEs[UE_name].packets:
   543                                                                       if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   544                                                                           # TODO: dropped and queued packets are treated the same way
   545                                                                           if (packet.status == PacketStatus.ARRIVED 
   546                                                                               or packet.status == PacketStatus.QUEUED 
   547                                                                               or packet.status == PacketStatus.DROPPED):
   548                                                                               
   549                                                                               packets_per_UE.append(packet.sequence_number)
   550                                                                   
   551                                                                   packets_to_transmit[UE_name] = packets_per_UE
   552                                           
   553                                           
   554                                           
   555                                           
   556                                                               n_transmitted_array = []
   557                                                               while start_time < base_schedule.schedule[slot].end_time:
   558                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   559                                                                   # each UE and return the minimum backoff time, if there is more than
   560                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   561                                                                   # and then draw again
   562                                                                   
   563                                                                   
   564                                                                   UEs_with_packets = []
   565                                                                   for UE_name in UEs_to_contend:
   566                                                                       if len(packets_to_transmit[UE_name]) > 0:
   567                                                                           earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   568                                                                           if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   569                                                                               UEs_with_packets.append(UE_name)
   570                                                                       
   571                                           
   572                                                                   if len(UEs_with_packets) > 0:
   573                                                                       backoff_times = {}
   574                                                                       for UE_name in UEs_with_packets:
   575                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   576                                                                           backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   577                                                                       min_backoff = min(backoff_times.values())
   578                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   579                                                                       UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   580                                                                                       backoff_times[UE_name] == min_backoff]
   581                                                                   else:
   582                                                                       UEs_to_transmit = []
   583                                                                       min_backoff = None
   584                                           
   585                                           
   586                                                                   # backoff_times = {}
   587                                                                   # for UE_name in UEs_to_contend:
   588                                                                   #     # TODO: Maybe initialize RNG each time to get different backoff times
   589                                                                   #     backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   590                                                                   # min_backoff = min(backoff_times.values())
   591                                                                   # # TODO: Check if start_time + min_backoff is less than the end time of the slot
   592                                                                   # UEs_winning_backoff = [UE_name for UE_name in UEs_to_contend if \
   593                                                                   #                 backoff_times[UE_name] == min_backoff]
   594                                                                   
   595                                                                   # # CW_array = [self.UEs[UE_name].CW for UE_name in UEs_to_contend]
   596                                                                   # # backoff_times = np.random.randint(0, CW_array)
   597                                                                   # # min_backoff = np.min(backoff_times)
   598                                                                   # # UEs_winning_backoff = np.array(UEs_to_contend)[backoff_times == min_backoff]
   599                                           
   600                                                                   # assert len(UEs_winning_backoff) > 0, "No UEs to transmit"
   601                                                                   
   602                                                                   # # Check that at least one UE has a packet to transmit and if not,
   603                                                                   # # advance the start_time by 1 and redo the backoff
   604                                                                   # UEs_to_transmit = []
   605                                                                   # for UE_name in UEs_winning_backoff:
   606                                                                   #     if len(packets_to_transmit[UE_name]) > 0:
   607                                                                   #         earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   608                                                                   #         if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   609                                                                   #             UEs_to_transmit.append(UE_name)
   610                                                                           
   611                                           
   612                                           
   613                                                                   # UEs_to_transmit = [UE_name for UE_name in UEs_winning_backoff if \
   614                                                                   #                 any((packet.arrival_time <= start_time and  
   615                                                                   #                     (packet.status == PacketStatus.ARRIVED 
   616                                                                   #                     or packet.status == PacketStatus.QUEUED 
   617                                                                   #                     or packet.status == PacketStatus.DROPPED)) \
   618                                                                   #                     for packet in self.UEs[UE_name].packets)]
   619                                           
   620                                           
   621                                                                   # save some debug information
   622                                                                   self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   623                                                                                             start_time, min_backoff, UEs_to_transmit])
   624                                           
   625                                                                   n_packets_transmitted = 0
   626                                                                   
   627                                                                   if len(UEs_to_transmit) == 0:
   628                                                                       start_time = start_time + advance_time
   629                                                                       
   630                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   631                                                                       # the current start time 
   632                                           
   633                                                                       if self.debug_mode:
   634                                                                           print("start_time: ", start_time)
   635                                           
   636                                                                   elif len(UEs_to_transmit) == 1:
   637                                                                       # Transmit all packets that have arrived till this point (start_time)
   638                                                                       delivery_time = start_time + delivery_latency_contention + \
   639                                                                                       min_backoff*self.wifi_slot_time + self.DIFS
   640                                                                       if delivery_time <= base_schedule.schedule[slot].end_time:
   641                                                                           for UE_name in UEs_to_transmit:
   642                                                                               payload_used = 0
   643                                                                               # TODO: Check if the slice is being used correctly
   644                                                                               # TODO: Change the slice size once delivery time is calculated
   645                                                                               # dynamically
   646                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:]:
   647                                                                                   # TODO: Check if this packet is being used correctly
   648                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
   649                                                                                   if packet.arrival_time <= start_time:
   650                                                                                       if payload_used + packet.size <= payload_size_contention:
   651                                                                                           payload_used += packet.size 
   652                                                                                           n_packets_transmitted += 1
   653                                                                                           if self.UEs[UE_name].transmit_packet(PER_contention):
   654                                                                                               packet.delivery_time = delivery_time 
   655                                                                                               packet.status = PacketStatus.DELIVERED
   656                                                                                               packets_to_transmit[UE_name].remove(packet_sequence_number)
   657                                                                                           else:
   658                                                                                               packet.status = PacketStatus.DROPPED
   659                                                                                       else:
   660                                                                                           break
   661                                                                                   else:
   662                                                                                       break
   663                                           
   664                                           
   665                                           
   666                                                                               # for packet in self.UEs[UE_name].packets:
   667                                                                               #     if packet.arrival_time <= start_time:
   668                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   669                                                                               #             or packet.status == PacketStatus.QUEUED 
   670                                                                               #             or packet.status == PacketStatus.DROPPED):
   671                                                                               #             if payload_used + packet.size <= payload_size_contention:
   672                                                                               #                 payload_used += packet.size 
   673                                                                               #                 n_packets_transmitted += 1
   674                                                                               #                 if self.UEs[UE_name].transmit_packet(PER_contention):
   675                                                                               #                     packet.delivery_time = delivery_time 
   676                                                                               #                     packet.status = PacketStatus.DELIVERED
   677                                                                               #                     packets_to_transmit[UE_name].remove(packet.sequence_number)
   678                                                                               #                 else:
   679                                                                               #                     packet.status = PacketStatus.DROPPED
   680                                                                               #     else:
   681                                                                               #     # assume packets are in ascending order of arrival time
   682                                                                               #     # if you've already reached the packets that haven't arrived
   683                                                                               #     # then break and don't evaluate any further
   684                                                                               #         break
   685                                                                                       
   686                                                                               # reset the contention window
   687                                                                               # TODO: You're skipping cases towards the end where delivery time
   688                                                                               # exceeds the end time of the slot. Need to fix this in the 
   689                                                                               # variable delivery latency case
   690                                                                               self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
   691                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   692                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   693                                                                                   .append(n_packets_transmitted)
   694                                                                               
   695                                                                       if n_packets_transmitted > 0:
   696                                                                           if self.debug_mode:
   697                                                                               print("start_time: ", start_time)
   698                                           
   699                                                                           start_time = delivery_time 
   700                                           
   701                                                                           if self.debug_mode:
   702                                                                               print("delivery_time: ", delivery_time)
   703                                                                               print("UEs: ", UEs_to_transmit)
   704                                                                       elif n_packets_transmitted == 0:
   705                                                                           start_time = start_time + advance_time
   706                                                                           if self.debug_mode:
   707                                                                               # This gets triggered towards the end of the slot
   708                                                                               # as delivery time exceeds the end time of the slot 
   709                                                                               print("Should not happen! start_time (advanced): ", start_time)
   710                                                                               print("UEs: ", UEs_to_transmit)
   711                                                                               print("Line595 Delivery time: ", delivery_time)
   712                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
   713                                                                       n_transmitted_array.append(n_packets_transmitted)
   714                                           
   715                                           
   716                                                                   else:
   717                                                                       # TODO: Fix the case where UEs contend but there's some of them
   718                                                                       # have no data to transmit, then exclude them from the list of
   719                                                                       # UEs contending, prevent packets from being dropped and
   720                                                                       # prevent the contention window from being doubled
   721                                                                       delivery_time = start_time + delivery_latency_contention + \
   722                                                                                       min_backoff*self.wifi_slot_time + self.DIFS
   723                                                                       if delivery_time <= base_schedule.schedule[slot].end_time:
   724                                                                           n_transmitted_old = 0 # TODO: remove the need for this by cleaning up the logic of the code
   725                                                                           for UE_name in UEs_to_transmit: 
   726                                                                               payload_used = 0
   727                                                                               
   728                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:]:
   729                                                                                   # TODO: Check if this packet is being used correctly
   730                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
   731                                                                                   if packet.arrival_time <= start_time:
   732                                                                                       if payload_used + packet.size <= payload_size_contention:
   733                                                                                           payload_used += packet.size 
   734                                                                                           n_packets_transmitted += 1
   735                                                                                           packet.status = PacketStatus.DROPPED
   736                                                                                       else:
   737                                                                                           break
   738                                                                                   else:
   739                                                                                       break
   740                                           
   741                                                                               # for packet in self.UEs[UE_name].packets:
   742                                                                               #     if packet.arrival_time <= start_time:
   743                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   744                                                                               #             or packet.status == PacketStatus.QUEUED 
   745                                                                               #             or packet.status == PacketStatus.DROPPED):
   746                                                                               #             if payload_used + packet.size <= payload_size_contention:
   747                                                                               #                 n_packets_transmitted += 1
   748                                                                               #                 payload_used += packet.size 
   749                                                                               #                 packet.status = PacketStatus.DROPPED
   750                                                                               #     else:
   751                                                                               #         break
   752                                           
   753                                           
   754                                                                               # double contention window for each UE
   755                                                                               if n_packets_transmitted > 0: 
   756                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
   757                                                                               # across all UEs. Avoids the case that no UE transmits and 
   758                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
   759                                                                               # from UEs_winning_backoff?)
   760                                                                                   self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
   761                                                                                                           self.UEs[UE_name].CWmax)
   762                                                                                   
   763                                                                               self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
   764                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   765                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   766                                                                                   .append(n_packets_transmitted - n_transmitted_old)
   767                                                                               n_transmitted_old = n_packets_transmitted
   768                                                                                   
   769                                           
   770                                                                       # TODO: there is a corner case where a UE's backoff might finish just
   771                                                                       # after the end of delivery_time in which case it should transmit
   772                                                                       # right away instead of starting again
   773                                                                       if n_packets_transmitted > 0:
   774                                                                           if self.debug_mode:
   775                                                                               print("start_time: ", start_time)
   776                                           
   777                                                                           start_time = delivery_time
   778                                           
   779                                                                           if self.debug_mode:
   780                                                                               print("delivery_time: ", delivery_time)
   781                                                                               print("UEs: ", UEs_to_transmit)
   782                                                                       elif n_packets_transmitted == 0:
   783                                                                           start_time = start_time + 1
   784                                                                           if self.debug_mode:
   785                                                                               # This gets triggered towards the end of the slot
   786                                                                               # as delivery time exceeds the end time of the slot
   787                                                                               print("Should not happen! start_time: ", start_time)
   788                                                                               print("UEs: ", UEs_to_transmit)
   789                                                                               print("Line647 Delivery time: ", delivery_time)
   790                                           
   791                                                               print("Mean packets transmitted: ", np.mean(n_transmitted_array))
   792                                                               # print("array of transmission numbers: ", n_transmitted_array)
   793                                                   
   794                                                   
   795                                                   ############### Mode 4 service mode of operation ######################
   796                                                   
   797                                                   
   798         1          0.0      0.0      0.0          elif service_mode_of_operation == "Mode 4":
   799                                                       # Mode 4 is still contention as in Mode 3 but allows UEs to transmit dynamic 
   800                                                       # number of packets 
   801                                                       
   802         1       1000.0   1000.0      0.0              assert 'payload_size' in kwargs, "Payload size not provided"
   803         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   804                                                           slots not provided"
   805         1          0.0      0.0      0.0              assert "contention" in kwargs['payload_size'], "Payload size for \
   806                                                           contention slots not provided"
   807         1       1000.0   1000.0      0.0              assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   808         1          0.0      0.0      0.0              assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   809                                                           reserved slots not provided"
   810         1          0.0      0.0      0.0              assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   811                                                           contention slots not provided"
   812         1          0.0      0.0      0.0              assert 'PER' in kwargs, "PER not provided"
   813         1          0.0      0.0      0.0              assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   814         1          0.0      0.0      0.0              assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   815         1       1000.0   1000.0      0.0              assert "aggregation_limit" in kwargs, "aggregation_limit not provided"
   816                                                       
   817                                           
   818         1          0.0      0.0      0.0              if "advance_time" in kwargs:
   819         1       1000.0   1000.0      0.0                  advance_time = kwargs["advance_time"]
   820                                                       else:
   821                                                           advance_time = 1
   822                                                       
   823         1       1000.0   1000.0      0.0              if self.debug_mode:
   824                                                           print("advance time: ", advance_time)
   825                                           
   826                                                       # Need to map PER to MCS somehow
   827                                                       
   828                                                       # TODO: maybe refactor the code to serve the reserved slots and contention slots
   829                                                       # separately
   830                                           
   831                                                       # TODO: Fix this delivery latency contention and make it an array
   832                                                       # TODO: we will need a more complicate setup for when different UEs have different
   833                                                       # MCSes, packet sizes and PERs
   834         1       4000.0   4000.0      0.0              payload_size_reserved = kwargs['payload_size']["reserved"]
   835         1          0.0      0.0      0.0              payload_size_contention = kwargs['payload_size']["contention"]
   836         1          0.0      0.0      0.0              delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   837         1          0.0      0.0      0.0              delivery_latency_contention = kwargs['delivery_latency']["contention"]
   838         1          0.0      0.0      0.0              PER_reserved = kwargs['PER']["reserved"]    
   839         1       1000.0   1000.0      0.0              PER_contention = kwargs['PER']["contention"]
   840         1          0.0      0.0      0.0              aggregation_limit = kwargs['aggregation_limit']
   841                                           
   842         1       1000.0   1000.0      0.0              assert len(delivery_latency_contention) > 1, "Deliver latency is an array"
   843                                                       
   844                                           
   845         1       1000.0   1000.0      0.0              UEs_all = set()
   846       601     180000.0    299.5      0.0              for slot in base_schedule.schedule:
   847       600     692000.0   1153.3      0.0                  UEs_all.update(base_schedule.schedule[slot].UEs)
   848                                                       
   849         1       1000.0   1000.0      0.0              if self.debug_mode:
   850                                                           print("UEs for queue measurement: ", UEs_all)
   851                                           
   852                                                       # Create queues of all packets to be trasmitted for each UE
   853                                                       # TODO: Check how this works when you have a mix of slots
   854         1       1000.0   1000.0      0.0              packets_to_transmit = {}
   855         1          0.0      0.0      0.0              arrival_times = {}
   856                                                       # for UE_name in UEs_all:
   857        11      24000.0   2181.8      0.0              for UE_name in UEs_all:
   858        10      12000.0   1200.0      0.0                  packets_per_UE = []
   859        10       3000.0    300.0      0.0                  arrivals_per_UE = []
   860    799464  272181000.0    340.5      0.7                  for packet in self.UEs[UE_name].packets:
   861    799454  417333000.0    522.0      1.0                      if packet.arrival_time <= base_schedule.end_time:
   862                                                                   # TODO: dropped and queued packets are treated the same way
   863    799454  438829000.0    548.9      1.0                          if (packet.status == PacketStatus.ARRIVED 
   864                                                                       or packet.status == PacketStatus.QUEUED 
   865                                                                       or packet.status == PacketStatus.DROPPED):
   866                                                                       
   867    799454  409752000.0    512.5      1.0                              packets_per_UE.append(packet.sequence_number)
   868    799454  434054000.0    542.9      1.0                              arrivals_per_UE.append(packet.arrival_time)
   869                                                               else: 
   870                                                                   break
   871                                                           
   872        10      33000.0   3300.0      0.0                  packets_to_transmit[UE_name] = packets_per_UE
   873        10       7000.0    700.0      0.0                  arrival_times[UE_name] = arrivals_per_UE
   874                                           
   875                                           
   876                                           
   877                                           
   878       601     567000.0    943.4      0.0              for slot in base_schedule.schedule:
   879       600     832000.0   1386.7      0.0                  if base_schedule.schedule[slot].mode == "reserved":
   880                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   881                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   882                                                               # Get the packets that can be served in this slot
   883                                                               payload_used = 0
   884                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   885                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   886                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   887                                                                           or packet.status == PacketStatus.DROPPED):
   888                                                                           # TODO: Currently, this assumes that there will always be more packets
   889                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   890                                                                           # always the maximum possible. However, if there are fewer packets than
   891                                                                           # paylaod size, then the delivery latency will be lower
   892                                                                           if payload_used + packet.size <= payload_size_reserved:
   893                                                                               # TODO: Add a guard interval
   894                                                                               # TODO: Implement number of retries-currently there are no retries
   895                                                                               # within the slot
   896                                                                               payload_used += packet.size
   897                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   898                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   899                                                                                                       delivery_latency_reserved
   900                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   901                                                                                       "Packet delivery time exceeds slot end time" 
   902                                                                                   packet.status = PacketStatus.DELIVERED
   903                                                                               else:
   904                                                                                   packet.status = PacketStatus.DROPPED
   905                                                                           else:
   906                                                                               packet.status = PacketStatus.QUEUED
   907                                                           
   908                                                           
   909       600     344000.0    573.3      0.0                  elif base_schedule.schedule[slot].mode == "contention":
   910       600     399000.0    665.0      0.0                      start_time = base_schedule.schedule[slot].start_time
   911                                                               # Contend only with the spcified UEs
   912       600     335000.0    558.3      0.0                      UEs_to_contend = base_schedule.schedule[slot].UEs
   913                                           
   914       600     840000.0   1400.0      0.0                      n_transmitted_array = []
   915       600     178000.0    296.7      0.0                      queue_measurement_time = start_time
   916                                           
   917                                                               # Measure queues at the start of the slot
   918                                                               # for UE_name in UEs_all:
   919      6600    2628000.0    398.2      0.0                      for UE_name in UEs_all:
   920      6000   10826000.0   1804.3      0.0                          queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
   921      6000    7998000.0   1333.0      0.0                          self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
   922      6000    4433000.0    738.8      0.0                          self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
   923    319061  486090000.0   1523.5      1.2                      while start_time < base_schedule.schedule[slot].end_time:
   924                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   925                                                                   # each UE and return the minimum backoff time, if there is more than
   926                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   927                                                                   # and then draw again
   928                                                                   
   929                                           
   930    318461  165452000.0    519.5      0.4                          if start_time - queue_measurement_time >= 1000:
   931                                                                       # for UE_name in UEs_all:
   932    489753  193823000.0    395.8      0.5                              for UE_name in UEs_all:
   933    445230  779394000.0   1750.5      1.9                                  queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
   934    445230  376167000.0    844.9      0.9                                  self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
   935    445230  326880000.0    734.2      0.8                                  self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
   936     44523   12380000.0    278.1      0.0                              queue_measurement_time = start_time
   937                                           
   938                                                                   
   939    318461  126872000.0    398.4      0.3                          UEs_with_packets = []
   940    636922  311724000.0    489.4      0.7                          for UE_name in UEs_to_contend:
   941    318461  178221000.0    559.6      0.4                              if len(packets_to_transmit[UE_name]) > 0:
   942    318461  132566000.0    416.3      0.3                                  earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   943    318461  245283000.0    770.2      0.6                                  if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   944     85909   42979000.0    500.3      0.1                                      UEs_with_packets.append(UE_name)
   945                                                                       
   946                                           
   947    318461  150715000.0    473.3      0.4                          if len(UEs_with_packets) > 0:
   948     85909   37651000.0    438.3      0.1                              backoff_times = {}
   949    171818   74320000.0    432.6      0.2                              for UE_name in UEs_with_packets:
   950                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   951     85909  559408000.0   6511.6      1.3                                  backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   952     85909   81012000.0    943.0      0.2                              min_backoff = min(backoff_times.values())
   953                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   954     85909  156107000.0   1817.1      0.4                              UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   955                                                                                       backoff_times[UE_name] == min_backoff]
   956                                                                   else:
   957    232552   77645000.0    333.9      0.2                              UEs_to_transmit = []
   958    232552   72402000.0    311.3      0.2                              min_backoff = None
   959                                           
   960                                                                   # save some debug information
   961    318461  132237000.0    415.2      0.3                          if self.debug_mode:
   962                                                                       self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   963                                                                                               start_time, min_backoff, UEs_to_transmit])
   964                                                                   
   965                                                                   # TODO: remove this
   966    318461   84330000.0    264.8      0.2                          n_packets_transmitted = 0
   967                                           
   968                                                                   
   969    318461  144125000.0    452.6      0.3                          if len(UEs_to_transmit) == 0:
   970    232552   96035000.0    413.0      0.2                              start_time = start_time + advance_time
   971    232552  120617000.0    518.7      0.3                              if start_time > base_schedule.schedule[slot].end_time:
   972       226     132000.0    584.1      0.0                                  start_time = base_schedule.schedule[slot].end_time
   973                                                                       
   974                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   975                                                                       # the current start time 
   976                                           
   977    232552  157765000.0    678.4      0.4                              if self.debug_mode:
   978                                                                           print("start_time: ", start_time)
   979                                                                           print("UEs: ", UEs_to_transmit)
   980                                           
   981     85909   38010000.0    442.4      0.1                          elif len(UEs_to_transmit) == 1:
   982                                                                       # Transmit all packets that have arrived till this point (start_time)
   983     85909   33372000.0    388.5      0.1                              UE_name = UEs_to_transmit[0]
   984                                           
   985                                                                       # Determine delivery time
   986    257727  123829000.0    480.5      0.3                              time_remaining = base_schedule.schedule[slot].end_time - start_time - \
   987    171818   64637000.0    376.2      0.2                                              min_backoff*self.wifi_slot_time - self.DIFS
   988    171818   97671000.0    568.5      0.2                              max_packets_time_remaining = bisect.bisect_right(\
   989     85909   24849000.0    289.2      0.1                                  delivery_latency_contention, time_remaining)
   990     85909   57497000.0    669.3      0.1                              max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
   991     85909   28601000.0    332.9      0.1                              n_packets_transmitted = 0
   992                                           
   993     85909   33517000.0    390.1      0.1                              if self.debug_mode:
   994                                                                           print("\nUE_name: ", UE_name)
   995                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
   996                                                                           print("start_time: ", start_time)
   997                                                                           print("min_backoff: ", min_backoff)
   998                                                                           print("DIFS: ", self.DIFS)
   999                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
  1000                                                                           print("time_remaining: ", time_remaining)
  1001                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
  1002                                                                           print("max_packets_allowed: ", max_packets_allowed)
  1003                                           
  1004                                                                           
  1005                                           
  1006     85909   34140000.0    397.4      0.1                              if max_packets_allowed == 0:
  1007                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
  1008       374     168000.0    449.2      0.0                                  n_packets_transmitted = 0
  1009                                                                       else:
  1010    878966  345633000.0    393.2      0.8                                  while (n_packets_transmitted < max_packets_allowed and 
  1011    800751  427324000.0    533.7      1.0                                         n_packets_transmitted < len(packets_to_transmit[UE_name])):
  1012    800751  274038000.0    342.2      0.7                                      if self.debug_mode:
  1013                                                                                   print("n_packets_transmitted: ", n_packets_transmitted)
  1014                                                                                   print("packet_sequence_number: ", packets_to_transmit[UE_name][n_packets_transmitted])
  1015                                                                                   print(" packets_to_transmit[UE_name][:10]: ",  packets_to_transmit[UE_name][:10])
  1016                                           
  1017    800751  332489000.0    415.2      0.8                                      packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
  1018    800751  390443000.0    487.6      0.9                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
  1019    800751  531768000.0    664.1      1.3                                      if packet.arrival_time <= start_time:
  1020    793431  276644000.0    348.7      0.7                                          n_packets_transmitted += 1
  1021                                                                               else:
  1022      7320    2037000.0    278.3      0.0                                          break
  1023                                                                           
  1024                                                                           # TODO: check indexing of delivery_latency_contention
  1025    256605  135242000.0    527.0      0.3                                  delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
  1026    171070   65524000.0    383.0      0.2                                                  min_backoff*self.wifi_slot_time + self.DIFS
  1027                                                                           
  1028    878966  382763000.0    435.5      0.9                                  for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
  1029    793431  461767000.0    582.0      1.1                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
  1030    793431 2235841000.0   2817.9      5.3                                      if self.UEs[UE_name].transmit_packet(PER_contention):
  1031    793431  343132000.0    432.5      0.8                                          packet.delivery_time = delivery_time 
  1032    793431  444671000.0    560.4      1.1                                          packet.status = PacketStatus.DELIVERED
  1033    793431        1e+10  16298.8     30.9                                          packets_to_transmit[UE_name].remove(packet_sequence_number)
  1034    793431        1e+10  16671.1     31.6                                          arrival_times[UE_name].remove(packet.arrival_time)
  1035    793431  742887000.0    936.3      1.8                                          assert len(arrival_times[UE_name]) == len(packets_to_transmit[UE_name]), \
  1036                                                                                       "Arrival times and packets to transmit are not the same length"
  1037                                                                               else:
  1038                                                                                   packet.status = PacketStatus.DROPPED
  1039                                                                           
  1040     85535   61760000.0    722.0      0.1                                  self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
  1041     85535   74139000.0    866.8      0.2                                  self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
  1042     85535   44337000.0    518.3      0.1                                  self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
  1043     85535   66386000.0    776.1      0.2                                      .append(n_packets_transmitted)
  1044                                                                               
  1045     85909   40074000.0    466.5      0.1                              if n_packets_transmitted > 0:
  1046     85535   30316000.0    354.4      0.1                                  if self.debug_mode:
  1047                                                                               print("start_time: ", start_time)
  1048                                           
  1049     85535   23462000.0    274.3      0.1                                  start_time = delivery_time 
  1050                                           
  1051     85535   34317000.0    401.2      0.1                                  if self.debug_mode:
  1052                                                                               print("delivery_time: ", delivery_time)
  1053                                                                               print("UEs: ", UEs_to_transmit)
  1054                                                                               print("\n")
  1055       374     135000.0    361.0      0.0                              elif n_packets_transmitted == 0:
  1056       374     124000.0    331.6      0.0                                  if max_packets_time_remaining == 0:
  1057       374     193000.0    516.0      0.0                                      start_time = base_schedule.schedule[slot].end_time
  1058       374     159000.0    425.1      0.0                                      if self.debug_mode:
  1059                                                                                   print("Start time advanced to end")
  1060                                                                                   print("Single UE, no packets transmitted")
  1061                                                                                   print("start_time: ", start_time)
  1062                                                                           else:
  1063                                                                               start_time = start_time + advance_time
  1064                                                                               if self.debug_mode:
  1065                                                                                   # This gets triggered towards the end of the slot
  1066                                                                                   # as delivery time exceeds the end time of the slot 
  1067                                                                                   print("Should not happen! start_time (advanced): ", start_time)
  1068                                                                                   print("UEs: ", UEs_to_transmit)
  1069                                                                                   print("\n")
  1070                                           
  1071                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
  1072     85909   67318000.0    783.6      0.2                              n_transmitted_array.append(n_packets_transmitted)
  1073                                           
  1074                                           
  1075                                                                   else:
  1076                                                                       # TODO: Fix the case where UEs contend but there's some of them
  1077                                                                       # have no data to transmit, then exclude them from the list of
  1078                                                                       # UEs contending, prevent packets from being dropped and
  1079                                                                       # prevent the contention window from being doubled
  1080                                                                       delivery_times = []
  1081                                                                       n_packets_transmitted_per_UE = []
  1082                                                                       time_remaining = base_schedule.schedule[slot].end_time - start_time - \
  1083                                                                                       min_backoff*self.wifi_slot_time - self.DIFS
  1084                                                                       # TODO: Make delivery_latency_contention different for different UEs
  1085                                                                       # using different MCSes
  1086                                                                       max_packets_time_remaining = bisect.bisect_right(\
  1087                                                                           delivery_latency_contention, time_remaining)
  1088                                                                       # TODO: Make aggregation different for different UEs
  1089                                                                       max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
  1090                                           
  1091                                                                       if self.debug_mode:
  1092                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
  1093                                                                           print("start_time: ", start_time)
  1094                                                                           print("min_backoff: ", min_backoff)
  1095                                                                           print("DIFS: ", self.DIFS)
  1096                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
  1097                                                                           print("time_remaining: ", time_remaining)
  1098                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
  1099                                                                           print("max_packets_allowed: ", max_packets_allowed)
  1100                                                                       
  1101                                                                       for UE_name in UEs_to_transmit:
  1102                                                                           n_packets_transmitted = 0
  1103                                                                           if max_packets_allowed == 0:
  1104                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
  1105                                                                               n_packets_transmitted = 0
  1106                                                                           else:
  1107                                                                               while (n_packets_transmitted < max_packets_allowed and 
  1108                                                                                  n_packets_transmitted < len(packets_to_transmit[UE_name])):
  1109                                                                                   if self.debug_mode:
  1110                                                                                       print("n_packets_transmitted: ", n_packets_transmitted)
  1111                                                                                       print("UE_name: ", UE_name)
  1112                                           
  1113                                                                                   packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
  1114                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
  1115                                                                                   if packet.arrival_time <= start_time:
  1116                                                                                       n_packets_transmitted += 1
  1117                                                                                   else:
  1118                                                                                       break
  1119                                                                               
  1120                                                                               # TODO: check indexing of delivery_latency_contention
  1121                                                                               delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
  1122                                                                                               min_backoff*self.wifi_slot_time + self.DIFS
  1123                                                                               delivery_times.append(delivery_time)
  1124                                           
  1125                                           
  1126                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
  1127                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
  1128                                                                                   packet.status = PacketStatus.DROPPED
  1129                                           
  1130                                                                               if n_packets_transmitted > 0: 
  1131                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
  1132                                                                               # across all UEs. Avoids the case that no UE transmits and 
  1133                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
  1134                                                                               # from UEs_winning_backoff?)
  1135                                                                                   self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
  1136                                                                                                           self.UEs[UE_name].CWmax)
  1137                                                                               
  1138                                                                               self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
  1139                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
  1140                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
  1141                                                                                   .append(n_packets_transmitted)
  1142                                                                           
  1143                                           
  1144                                                                           
  1145                                                                           n_packets_transmitted_per_UE.append(n_packets_transmitted)
  1146                                           
  1147                                                                       total_packets_transmitted = sum(n_packets_transmitted_per_UE)
  1148                                                                       if total_packets_transmitted > 0:
  1149                                                                           if self.debug_mode:
  1150                                                                               print("start_time: ", start_time)
  1151                                           
  1152                                                                           start_time = max(delivery_times)
  1153                                           
  1154                                                                           if self.debug_mode:
  1155                                                                               print("delivery_time: ", delivery_times)
  1156                                                                               print("UEs: ", UEs_to_transmit)
  1157                                                                               print("\n")
  1158                                                                       elif total_packets_transmitted == 0:
  1159                                                                           if max_packets_time_remaining == 0:
  1160                                                                               start_time = base_schedule.schedule[slot].end_time
  1161                                                                               if self.debug_mode:
  1162                                                                                   print("Start time advanced to end")
  1163                                                                                   print("Single UE, no packets transmitted")
  1164                                                                                   print("start_time: ", start_time)
  1165                                                                           else:
  1166                                                                               start_time = start_time + advance_time
  1167                                                                               if self.debug_mode:
  1168                                                                                   # This gets triggered towards the end of the slot
  1169                                                                                   # as delivery time exceeds the end time of the slot
  1170                                                                                   print("Should not happen! start_time: ", start_time)
  1171                                                                                   print("UEs: ", UEs_to_transmit)
  1172                                                                                   print("Line collision Delivery time: ", delivery_times)
  1173                                                                                   print("\n")
  1174                                           
  1175                                                               # print("Mean packets transmitted: ", np.mean(n_transmitted_array))
  1176                                                               # print("array of transmission numbers: ", n_transmitted_array)