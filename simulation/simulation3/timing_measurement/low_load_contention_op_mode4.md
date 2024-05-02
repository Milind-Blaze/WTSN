Timer unit: 1e-09 s

Total time: 3.31045 s
File: /Users/milindkumarvaddiraju/projects/HVC_use/WTSN/simulation/network_classes.py
Function: serve_packets at line 438

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   438                                               def serve_packets(self, base_schedule: Schedule, service_mode_of_operation: str, 
   439                                                                 **kwargs) -> None:
   440                                                   '''
   441                                                   Function to serve the packets that the UEs have to transmit
   442                                           
   443                                                   Args:
   444                                                       base_schedule (Schedule): A base schedule specifying
   445                                                           Qbv windows for different UEs across time
   446                                                       service_mode_of_operation (str): Mode of operation of the UEs within 
   447                                                           a Qbv window
   448                                                   '''
   449         1       3000.0   3000.0      0.0          if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
   450                                                       for ue in self.UEs:
   451                                                           ue.serve_packets(base_schedule, **kwargs)
   452         1       1000.0   1000.0      0.0          elif service_mode_of_operation == "Mode 3":
   453                                                       # Mode 3 handles contention as well, the behaviour is the same as Mode 2 in the reserved
   454                                                       # slots but different in the contention slot
   455                                                       # The following are the assumptions in the reserved slot:
   456                                                           # Only one UE can transmit in the slot
   457                                                           # All UEs have the same characteristics: payload size, delivery latency, PER
   458                                                       # The following are the assumptions in the contetion slot:
   459                                                       # 
   460                                                       
   461                                                       assert 'payload_size' in kwargs, "Payload size not provided"
   462                                                       assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   463                                                           slots not provided"
   464                                                       assert "contention" in kwargs['payload_size'], "Payload size for \
   465                                                           contention slots not provided"
   466                                                       assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   467                                                       assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   468                                                           reserved slots not provided"
   469                                                       assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   470                                                           contention slots not provided"
   471                                                       assert 'PER' in kwargs, "PER not provided"
   472                                                       assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   473                                                       assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   474                                           
   475                                                       if "advance_time" in kwargs:
   476                                                           advance_time = kwargs["advance_time"]
   477                                                       else:
   478                                                           advance_time = 1
   479                                                       
   480                                                       if self.debug_mode:
   481                                                           print("advance time: ", advance_time)
   482                                           
   483                                                       # Need to map PER to MCS somehow
   484                                                       
   485                                                       # TODO: maybe refactor the code to serve the reserved slots and contention slots
   486                                                       # separately
   487                                           
   488                                           
   489                                                       payload_size_reserved = kwargs['payload_size']["reserved"]
   490                                                       payload_size_contention = kwargs['payload_size']["contention"]
   491                                                       delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   492                                                       delivery_latency_contention = kwargs['delivery_latency']["contention"]
   493                                                       PER_reserved = kwargs['PER']["reserved"]    
   494                                                       PER_contention = kwargs['PER']["contention"]
   495                                                       
   496                                           
   497                                                       for slot in base_schedule.schedule:
   498                                                           if base_schedule.schedule[slot].mode == "reserved":
   499                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   500                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   501                                                               # Get the packets that can be served in this slot
   502                                                               payload_used = 0
   503                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   504                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   505                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   506                                                                           or packet.status == PacketStatus.DROPPED):
   507                                                                           # TODO: Currently, this assumes that there will always be more packets
   508                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   509                                                                           # always the maximum possible. However, if there are fewer packets than
   510                                                                           # paylaod size, then the delivery latency will be lower
   511                                                                           if payload_used + packet.size <= payload_size_reserved:
   512                                                                               # TODO: Add a guard interval
   513                                                                               # TODO: Implement number of retries-currently there are no retries
   514                                                                               # within the slot
   515                                                                               payload_used += packet.size
   516                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   517                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   518                                                                                                       delivery_latency_reserved
   519                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   520                                                                                       "Packet delivery time exceeds slot end time" 
   521                                                                                   packet.status = PacketStatus.DELIVERED
   522                                                                               else:
   523                                                                                   packet.status = PacketStatus.DROPPED
   524                                                                           else:
   525                                                                               packet.status = PacketStatus.QUEUED
   526                                                           
   527                                                           
   528                                                           elif base_schedule.schedule[slot].mode == "contention":
   529                                                               start_time = base_schedule.schedule[slot].start_time
   530                                                               # Contend only with the spcified UEs
   531                                                               UEs_to_contend = base_schedule.schedule[slot].UEs
   532                                           
   533                                                               # Create queues of all packets to be trasmitted for each UE
   534                                                               # TODO: Check how this works when you have a mix of slots
   535                                                               packets_to_transmit = {}
   536                                                               for UE_name in UEs_to_contend:
   537                                                                   packets_per_UE = []
   538                                                                   for packet in self.UEs[UE_name].packets:
   539                                                                       if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   540                                                                           # TODO: dropped and queued packets are treated the same way
   541                                                                           if (packet.status == PacketStatus.ARRIVED 
   542                                                                               or packet.status == PacketStatus.QUEUED 
   543                                                                               or packet.status == PacketStatus.DROPPED):
   544                                                                               
   545                                                                               packets_per_UE.append(packet.sequence_number)
   546                                                                   
   547                                                                   packets_to_transmit[UE_name] = packets_per_UE
   548                                           
   549                                           
   550                                           
   551                                           
   552                                                               n_transmitted_array = []
   553                                                               while start_time < base_schedule.schedule[slot].end_time:
   554                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   555                                                                   # each UE and return the minimum backoff time, if there is more than
   556                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   557                                                                   # and then draw again
   558                                                                   
   559                                                                   
   560                                                                   UEs_with_packets = []
   561                                                                   for UE_name in UEs_to_contend:
   562                                                                       if len(packets_to_transmit[UE_name]) > 0:
   563                                                                           earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   564                                                                           if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   565                                                                               UEs_with_packets.append(UE_name)
   566                                                                       
   567                                           
   568                                                                   if len(UEs_with_packets) > 0:
   569                                                                       backoff_times = {}
   570                                                                       for UE_name in UEs_with_packets:
   571                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   572                                                                           backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   573                                                                       min_backoff = min(backoff_times.values())
   574                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   575                                                                       UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   576                                                                                       backoff_times[UE_name] == min_backoff]
   577                                                                   else:
   578                                                                       UEs_to_transmit = []
   579                                                                       min_backoff = None
   580                                           
   581                                           
   582                                                                   # backoff_times = {}
   583                                                                   # for UE_name in UEs_to_contend:
   584                                                                   #     # TODO: Maybe initialize RNG each time to get different backoff times
   585                                                                   #     backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   586                                                                   # min_backoff = min(backoff_times.values())
   587                                                                   # # TODO: Check if start_time + min_backoff is less than the end time of the slot
   588                                                                   # UEs_winning_backoff = [UE_name for UE_name in UEs_to_contend if \
   589                                                                   #                 backoff_times[UE_name] == min_backoff]
   590                                                                   
   591                                                                   # # CW_array = [self.UEs[UE_name].CW for UE_name in UEs_to_contend]
   592                                                                   # # backoff_times = np.random.randint(0, CW_array)
   593                                                                   # # min_backoff = np.min(backoff_times)
   594                                                                   # # UEs_winning_backoff = np.array(UEs_to_contend)[backoff_times == min_backoff]
   595                                           
   596                                                                   # assert len(UEs_winning_backoff) > 0, "No UEs to transmit"
   597                                                                   
   598                                                                   # # Check that at least one UE has a packet to transmit and if not,
   599                                                                   # # advance the start_time by 1 and redo the backoff
   600                                                                   # UEs_to_transmit = []
   601                                                                   # for UE_name in UEs_winning_backoff:
   602                                                                   #     if len(packets_to_transmit[UE_name]) > 0:
   603                                                                   #         earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   604                                                                   #         if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   605                                                                   #             UEs_to_transmit.append(UE_name)
   606                                                                           
   607                                           
   608                                           
   609                                                                   # UEs_to_transmit = [UE_name for UE_name in UEs_winning_backoff if \
   610                                                                   #                 any((packet.arrival_time <= start_time and  
   611                                                                   #                     (packet.status == PacketStatus.ARRIVED 
   612                                                                   #                     or packet.status == PacketStatus.QUEUED 
   613                                                                   #                     or packet.status == PacketStatus.DROPPED)) \
   614                                                                   #                     for packet in self.UEs[UE_name].packets)]
   615                                           
   616                                           
   617                                                                   # save some debug information
   618                                                                   self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   619                                                                                             start_time, min_backoff, UEs_to_transmit])
   620                                           
   621                                                                   n_packets_transmitted = 0
   622                                                                   
   623                                                                   if len(UEs_to_transmit) == 0:
   624                                                                       start_time = start_time + advance_time
   625                                                                       
   626                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   627                                                                       # the current start time 
   628                                           
   629                                                                       if self.debug_mode:
   630                                                                           print("start_time: ", start_time)
   631                                           
   632                                                                   elif len(UEs_to_transmit) == 1:
   633                                                                       # Transmit all packets that have arrived till this point (start_time)
   634                                                                       delivery_time = start_time + delivery_latency_contention + \
   635                                                                                       min_backoff*self.wifi_slot_time + self.DIFS
   636                                                                       if delivery_time <= base_schedule.schedule[slot].end_time:
   637                                                                           for UE_name in UEs_to_transmit:
   638                                                                               payload_used = 0
   639                                                                               # TODO: Check if the slice is being used correctly
   640                                                                               # TODO: Change the slice size once delivery time is calculated
   641                                                                               # dynamically
   642                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:]:
   643                                                                                   # TODO: Check if this packet is being used correctly
   644                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
   645                                                                                   if packet.arrival_time <= start_time:
   646                                                                                       if payload_used + packet.size <= payload_size_contention:
   647                                                                                           payload_used += packet.size 
   648                                                                                           n_packets_transmitted += 1
   649                                                                                           if self.UEs[UE_name].transmit_packet(PER_contention):
   650                                                                                               packet.delivery_time = delivery_time 
   651                                                                                               packet.status = PacketStatus.DELIVERED
   652                                                                                               packets_to_transmit[UE_name].remove(packet_sequence_number)
   653                                                                                           else:
   654                                                                                               packet.status = PacketStatus.DROPPED
   655                                                                                       else:
   656                                                                                           break
   657                                                                                   else:
   658                                                                                       break
   659                                           
   660                                           
   661                                           
   662                                                                               # for packet in self.UEs[UE_name].packets:
   663                                                                               #     if packet.arrival_time <= start_time:
   664                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   665                                                                               #             or packet.status == PacketStatus.QUEUED 
   666                                                                               #             or packet.status == PacketStatus.DROPPED):
   667                                                                               #             if payload_used + packet.size <= payload_size_contention:
   668                                                                               #                 payload_used += packet.size 
   669                                                                               #                 n_packets_transmitted += 1
   670                                                                               #                 if self.UEs[UE_name].transmit_packet(PER_contention):
   671                                                                               #                     packet.delivery_time = delivery_time 
   672                                                                               #                     packet.status = PacketStatus.DELIVERED
   673                                                                               #                     packets_to_transmit[UE_name].remove(packet.sequence_number)
   674                                                                               #                 else:
   675                                                                               #                     packet.status = PacketStatus.DROPPED
   676                                                                               #     else:
   677                                                                               #     # assume packets are in ascending order of arrival time
   678                                                                               #     # if you've already reached the packets that haven't arrived
   679                                                                               #     # then break and don't evaluate any further
   680                                                                               #         break
   681                                                                                       
   682                                                                               # reset the contention window
   683                                                                               # TODO: You're skipping cases towards the end where delivery time
   684                                                                               # exceeds the end time of the slot. Need to fix this in the 
   685                                                                               # variable delivery latency case
   686                                                                               self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
   687                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   688                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   689                                                                                   .append(n_packets_transmitted)
   690                                                                               
   691                                                                       if n_packets_transmitted > 0:
   692                                                                           if self.debug_mode:
   693                                                                               print("start_time: ", start_time)
   694                                           
   695                                                                           start_time = delivery_time 
   696                                           
   697                                                                           if self.debug_mode:
   698                                                                               print("delivery_time: ", delivery_time)
   699                                                                               print("UEs: ", UEs_to_transmit)
   700                                                                       elif n_packets_transmitted == 0:
   701                                                                           start_time = start_time + advance_time
   702                                                                           if self.debug_mode:
   703                                                                               # This gets triggered towards the end of the slot
   704                                                                               # as delivery time exceeds the end time of the slot 
   705                                                                               print("Should not happen! start_time (advanced): ", start_time)
   706                                                                               print("UEs: ", UEs_to_transmit)
   707                                                                               print("Line595 Delivery time: ", delivery_time)
   708                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
   709                                                                       n_transmitted_array.append(n_packets_transmitted)
   710                                           
   711                                           
   712                                                                   else:
   713                                                                       # TODO: Fix the case where UEs contend but there's some of them
   714                                                                       # have no data to transmit, then exclude them from the list of
   715                                                                       # UEs contending, prevent packets from being dropped and
   716                                                                       # prevent the contention window from being doubled
   717                                                                       delivery_time = start_time + delivery_latency_contention + \
   718                                                                                       min_backoff*self.wifi_slot_time + self.DIFS
   719                                                                       if delivery_time <= base_schedule.schedule[slot].end_time:
   720                                                                           n_transmitted_old = 0 # TODO: remove the need for this by cleaning up the logic of the code
   721                                                                           for UE_name in UEs_to_transmit: 
   722                                                                               payload_used = 0
   723                                                                               
   724                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:]:
   725                                                                                   # TODO: Check if this packet is being used correctly
   726                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
   727                                                                                   if packet.arrival_time <= start_time:
   728                                                                                       if payload_used + packet.size <= payload_size_contention:
   729                                                                                           payload_used += packet.size 
   730                                                                                           n_packets_transmitted += 1
   731                                                                                           packet.status = PacketStatus.DROPPED
   732                                                                                       else:
   733                                                                                           break
   734                                                                                   else:
   735                                                                                       break
   736                                           
   737                                                                               # for packet in self.UEs[UE_name].packets:
   738                                                                               #     if packet.arrival_time <= start_time:
   739                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   740                                                                               #             or packet.status == PacketStatus.QUEUED 
   741                                                                               #             or packet.status == PacketStatus.DROPPED):
   742                                                                               #             if payload_used + packet.size <= payload_size_contention:
   743                                                                               #                 n_packets_transmitted += 1
   744                                                                               #                 payload_used += packet.size 
   745                                                                               #                 packet.status = PacketStatus.DROPPED
   746                                                                               #     else:
   747                                                                               #         break
   748                                           
   749                                           
   750                                                                               # double contention window for each UE
   751                                                                               if n_packets_transmitted > 0: 
   752                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
   753                                                                               # across all UEs. Avoids the case that no UE transmits and 
   754                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
   755                                                                               # from UEs_winning_backoff?)
   756                                                                                   self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
   757                                                                                                           self.UEs[UE_name].CWmax)
   758                                                                                   
   759                                                                               self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
   760                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   761                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   762                                                                                   .append(n_packets_transmitted - n_transmitted_old)
   763                                                                               n_transmitted_old = n_packets_transmitted
   764                                                                                   
   765                                           
   766                                                                       # TODO: there is a corner case where a UE's backoff might finish just
   767                                                                       # after the end of delivery_time in which case it should transmit
   768                                                                       # right away instead of starting again
   769                                                                       if n_packets_transmitted > 0:
   770                                                                           if self.debug_mode:
   771                                                                               print("start_time: ", start_time)
   772                                           
   773                                                                           start_time = delivery_time
   774                                           
   775                                                                           if self.debug_mode:
   776                                                                               print("delivery_time: ", delivery_time)
   777                                                                               print("UEs: ", UEs_to_transmit)
   778                                                                       elif n_packets_transmitted == 0:
   779                                                                           start_time = start_time + 1
   780                                                                           if self.debug_mode:
   781                                                                               # This gets triggered towards the end of the slot
   782                                                                               # as delivery time exceeds the end time of the slot
   783                                                                               print("Should not happen! start_time: ", start_time)
   784                                                                               print("UEs: ", UEs_to_transmit)
   785                                                                               print("Line647 Delivery time: ", delivery_time)
   786                                           
   787                                                               print("Mean packets transmitted: ", np.mean(n_transmitted_array))
   788                                                               # print("array of transmission numbers: ", n_transmitted_array)
   789                                                   
   790                                                   
   791                                                   ############### Mode 4 service mode of operation ######################
   792                                                   
   793                                                   
   794         1          0.0      0.0      0.0          elif service_mode_of_operation == "Mode 4":
   795                                                       # Mode 4 is still contention as in Mode 3 but allows UEs to transmit dynamic 
   796                                                       # number of packets 
   797                                                       
   798         1       1000.0   1000.0      0.0              assert 'payload_size' in kwargs, "Payload size not provided"
   799         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   800                                                           slots not provided"
   801         1          0.0      0.0      0.0              assert "contention" in kwargs['payload_size'], "Payload size for \
   802                                                           contention slots not provided"
   803         1          0.0      0.0      0.0              assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   804         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   805                                                           reserved slots not provided"
   806         1       1000.0   1000.0      0.0              assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   807                                                           contention slots not provided"
   808         1       1000.0   1000.0      0.0              assert 'PER' in kwargs, "PER not provided"
   809         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   810         1       1000.0   1000.0      0.0              assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   811         1          0.0      0.0      0.0              assert "aggregation_limit" in kwargs, "aggregation_limit not provided"
   812                                           
   813         1          0.0      0.0      0.0              if "advance_time" in kwargs:
   814         1          0.0      0.0      0.0                  advance_time = kwargs["advance_time"]
   815                                                       else:
   816                                                           advance_time = 1
   817                                                       
   818         1       1000.0   1000.0      0.0              if self.debug_mode:
   819                                                           print("advance time: ", advance_time)
   820                                           
   821                                                       # Need to map PER to MCS somehow
   822                                                       
   823                                                       # TODO: maybe refactor the code to serve the reserved slots and contention slots
   824                                                       # separately
   825                                           
   826                                                       # TODO: Fix this delivery latency contention and make it an array
   827                                                       # TODO: we will need a more complicate setup for when different UEs have different
   828                                                       # MCSes, packet sizes and PERs
   829         1       1000.0   1000.0      0.0              payload_size_reserved = kwargs['payload_size']["reserved"]
   830         1          0.0      0.0      0.0              payload_size_contention = kwargs['payload_size']["contention"]
   831         1          0.0      0.0      0.0              delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   832         1          0.0      0.0      0.0              delivery_latency_contention = kwargs['delivery_latency']["contention"]
   833         1          0.0      0.0      0.0              PER_reserved = kwargs['PER']["reserved"]    
   834         1       1000.0   1000.0      0.0              PER_contention = kwargs['PER']["contention"]
   835         1          0.0      0.0      0.0              aggregation_limit = kwargs['aggregation_limit']
   836                                                       
   837                                           
   838         2       4000.0   2000.0      0.0              for slot in base_schedule.schedule:
   839         1       1000.0   1000.0      0.0                  if base_schedule.schedule[slot].mode == "reserved":
   840                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   841                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   842                                                               # Get the packets that can be served in this slot
   843                                                               payload_used = 0
   844                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   845                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   846                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   847                                                                           or packet.status == PacketStatus.DROPPED):
   848                                                                           # TODO: Currently, this assumes that there will always be more packets
   849                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   850                                                                           # always the maximum possible. However, if there are fewer packets than
   851                                                                           # paylaod size, then the delivery latency will be lower
   852                                                                           if payload_used + packet.size <= payload_size_reserved:
   853                                                                               # TODO: Add a guard interval
   854                                                                               # TODO: Implement number of retries-currently there are no retries
   855                                                                               # within the slot
   856                                                                               payload_used += packet.size
   857                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   858                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   859                                                                                                       delivery_latency_reserved
   860                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   861                                                                                       "Packet delivery time exceeds slot end time" 
   862                                                                                   packet.status = PacketStatus.DELIVERED
   863                                                                               else:
   864                                                                                   packet.status = PacketStatus.DROPPED
   865                                                                           else:
   866                                                                               packet.status = PacketStatus.QUEUED
   867                                                           
   868                                                           
   869         1       1000.0   1000.0      0.0                  elif base_schedule.schedule[slot].mode == "contention":
   870         1          0.0      0.0      0.0                      start_time = base_schedule.schedule[slot].start_time
   871                                                               # Contend only with the spcified UEs
   872         1       1000.0   1000.0      0.0                      UEs_to_contend = base_schedule.schedule[slot].UEs
   873                                           
   874                                                               # Create queues of all packets to be trasmitted for each UE
   875                                                               # TODO: Check how this works when you have a mix of slots
   876         1       1000.0   1000.0      0.0                      packets_to_transmit = {}
   877        11       5000.0    454.5      0.0                      for UE_name in UEs_to_contend:
   878        10       1000.0    100.0      0.0                          packets_per_UE = []
   879       459     194000.0    422.7      0.0                          for packet in self.UEs[UE_name].packets:
   880       449     294000.0    654.8      0.0                              if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   881                                                                           # TODO: dropped and queued packets are treated the same way
   882       449     246000.0    547.9      0.0                                  if (packet.status == PacketStatus.ARRIVED 
   883                                                                               or packet.status == PacketStatus.QUEUED 
   884                                                                               or packet.status == PacketStatus.DROPPED):
   885                                                                               
   886       449     270000.0    601.3      0.0                                      packets_per_UE.append(packet.sequence_number)
   887                                                                   
   888        10       7000.0    700.0      0.0                          packets_to_transmit[UE_name] = packets_per_UE
   889                                           
   890                                           
   891         1          0.0      0.0      0.0                      n_transmitted_array = []
   892    124224  168343000.0   1355.2      5.1                      while start_time < base_schedule.schedule[slot].end_time:
   893                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   894                                                                   # each UE and return the minimum backoff time, if there is more than
   895                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   896                                                                   # and then draw again
   897                                                                   
   898                                                                   
   899    124223   49885000.0    401.6      1.5                          UEs_with_packets = []
   900   1366453  622128000.0    455.3     18.8                          for UE_name in UEs_to_contend:
   901   1242230  582726000.0    469.1     17.6                              if len(packets_to_transmit[UE_name]) > 0:
   902   1224452  466916000.0    381.3     14.1                                  earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   903   1224452  776286000.0    634.0     23.4                                  if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   904       510     501000.0    982.4      0.0                                      UEs_with_packets.append(UE_name)
   905                                                                       
   906                                           
   907    124223   58336000.0    469.6      1.8                          if len(UEs_with_packets) > 0:
   908       500     590000.0   1180.0      0.0                              backoff_times = {}
   909      1010     526000.0    520.8      0.0                              for UE_name in UEs_with_packets:
   910                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   911       510   12653000.0  24809.8      0.4                                  backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   912       500    1233000.0   2466.0      0.0                              min_backoff = min(backoff_times.values())
   913                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   914       500    2179000.0   4358.0      0.1                              UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   915                                                                                       backoff_times[UE_name] == min_backoff]
   916                                                                   else:
   917    123723   36467000.0    294.7      1.1                              UEs_to_transmit = []
   918    123723   34032000.0    275.1      1.0                              min_backoff = None
   919                                           
   920                                                                   # save some debug information
   921    248446  230539000.0    927.9      7.0                          self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   922    124223   40275000.0    324.2      1.2                                                    start_time, min_backoff, UEs_to_transmit])
   923                                                                   
   924                                                                   # TODO: remove this
   925    124223   38330000.0    308.6      1.2                          n_packets_transmitted = 0
   926                                           
   927                                                                   
   928    124223   56478000.0    454.7      1.7                          if len(UEs_to_transmit) == 0:
   929    123723   44212000.0    357.3      1.3                              start_time = start_time + advance_time
   930                                                                       
   931                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   932                                                                       # the current start time 
   933                                           
   934    123723   69232000.0    559.6      2.1                              if self.debug_mode:
   935                                                                           print("start_time: ", start_time)
   936                                           
   937       500     265000.0    530.0      0.0                          elif len(UEs_to_transmit) == 1:
   938                                                                       # Transmit all packets that have arrived till this point (start_time)
   939       499     205000.0    410.8      0.0                              UE_name = UEs_to_transmit[0]
   940                                           
   941                                                                       # Determine delivery time
   942      1497     990000.0    661.3      0.0                              time_remaining = base_schedule.schedule[slot].end_time - start_time - \
   943       998     541000.0    542.1      0.0                                              min_backoff*self.wifi_slot_time - self.DIFS
   944       998    1002000.0   1004.0      0.0                              max_packets_time_remaining = bisect.bisect_right(\
   945       499     144000.0    288.6      0.0                                  delivery_latency_contention, time_remaining)
   946       499     566000.0   1134.3      0.0                              max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
   947       499     164000.0    328.7      0.0                              n_packets_transmitted = 0
   948                                           
   949       499     241000.0    483.0      0.0                              if self.debug_mode:
   950                                                                           print("\nUE_name: ", UE_name)
   951                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
   952                                                                           print("start_time: ", start_time)
   953                                                                           print("min_backoff: ", min_backoff)
   954                                                                           print("DIFS: ", self.DIFS)
   955                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
   956                                                                           print("time_remaining: ", time_remaining)
   957                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
   958                                                                           print("max_packets_allowed: ", max_packets_allowed)
   959                                           
   960                                                                           
   961                                           
   962       499     187000.0    374.7      0.0                              if max_packets_allowed == 0:
   963                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
   964        52      27000.0    519.2      0.0                                  n_packets_transmitted = 0
   965                                                                       else:
   966       895     398000.0    444.7      0.0                                  while (n_packets_transmitted < max_packets_allowed and 
   967       895     525000.0    586.6      0.0                                         n_packets_transmitted < len(packets_to_transmit[UE_name])):
   968       886     292000.0    329.6      0.0                                      if self.debug_mode:
   969                                                                                   print("n_packets_transmitted: ", n_packets_transmitted)
   970                                                                                   print("packet_sequence_number: ", packets_to_transmit[UE_name][n_packets_transmitted])
   971                                                                                   print(" packets_to_transmit[UE_name]: ",  packets_to_transmit[UE_name])
   972                                           
   973       886     407000.0    459.4      0.0                                      packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
   974       886     505000.0    570.0      0.0                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
   975       886     657000.0    741.5      0.0                                      if packet.arrival_time <= start_time:
   976       448     284000.0    633.9      0.0                                          n_packets_transmitted += 1
   977                                                                               else:
   978       438     116000.0    264.8      0.0                                          break
   979                                                                           
   980                                                                           # TODO: check indexing of delivery_latency_contention
   981      1341     654000.0    487.7      0.0                                  delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
   982       894     286000.0    319.9      0.0                                                  min_backoff*self.wifi_slot_time + self.DIFS
   983                                                                           
   984       895     888000.0    992.2      0.0                                  for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
   985       448     192000.0    428.6      0.0                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
   986       448    3131000.0   6988.8      0.1                                      if self.UEs[UE_name].transmit_packet(PER_contention):
   987       448     396000.0    883.9      0.0                                          packet.delivery_time = delivery_time 
   988       448     868000.0   1937.5      0.0                                          packet.status = PacketStatus.DELIVERED
   989       448     636000.0   1419.6      0.0                                          packets_to_transmit[UE_name].remove(packet_sequence_number)
   990                                                                               else:
   991                                                                                   packet.status = PacketStatus.DROPPED
   992                                                                           
   993       447     328000.0    733.8      0.0                                  self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
   994       447     531000.0   1187.9      0.0                                  self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   995       447     256000.0    572.7      0.0                                  self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   996       447     277000.0    619.7      0.0                                      .append(n_packets_transmitted)
   997                                                                               
   998       499     190000.0    380.8      0.0                              if n_packets_transmitted > 0:
   999       447     162000.0    362.4      0.0                                  if self.debug_mode:
  1000                                                                               print("start_time: ", start_time)
  1001                                           
  1002       447     124000.0    277.4      0.0                                  start_time = delivery_time 
  1003                                           
  1004       447     162000.0    362.4      0.0                                  if self.debug_mode:
  1005                                                                               print("delivery_time: ", delivery_time)
  1006                                                                               print("UEs: ", UEs_to_transmit)
  1007                                                                               print("\n")
  1008        52      19000.0    365.4      0.0                              elif n_packets_transmitted == 0:
  1009        52      26000.0    500.0      0.0                                  start_time = start_time + advance_time
  1010        52      22000.0    423.1      0.0                                  if self.debug_mode:
  1011                                                                               # This gets triggered towards the end of the slot
  1012                                                                               # as delivery time exceeds the end time of the slot 
  1013                                                                               print("Should not happen! start_time (advanced): ", start_time)
  1014                                                                               print("UEs: ", UEs_to_transmit)
  1015                                                                               print("\n")
  1016                                           
  1017                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
  1018       499     413000.0    827.7      0.0                              n_transmitted_array.append(n_packets_transmitted)
  1019                                           
  1020                                           
  1021                                                                   else:
  1022                                                                       # TODO: Fix the case where UEs contend but there's some of them
  1023                                                                       # have no data to transmit, then exclude them from the list of
  1024                                                                       # UEs contending, prevent packets from being dropped and
  1025                                                                       # prevent the contention window from being doubled
  1026         1       1000.0   1000.0      0.0                              delivery_times = []
  1027         1          0.0      0.0      0.0                              n_packets_transmitted_per_UE = []
  1028         3       2000.0    666.7      0.0                              time_remaining = base_schedule.schedule[slot].end_time - start_time - \
  1029         2       2000.0   1000.0      0.0                                              min_backoff*self.wifi_slot_time - self.DIFS
  1030                                                                       # TODO: Make delivery_latency_contention different for different UEs
  1031                                                                       # using different MCSes
  1032         2       1000.0    500.0      0.0                              max_packets_time_remaining = bisect.bisect_right(\
  1033         1          0.0      0.0      0.0                                  delivery_latency_contention, time_remaining)
  1034                                                                       # TODO: Make aggregation different for different UEs
  1035         1       1000.0   1000.0      0.0                              max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
  1036                                           
  1037         1          0.0      0.0      0.0                              if self.debug_mode:
  1038                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
  1039                                                                           print("start_time: ", start_time)
  1040                                                                           print("min_backoff: ", min_backoff)
  1041                                                                           print("DIFS: ", self.DIFS)
  1042                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
  1043                                                                           print("time_remaining: ", time_remaining)
  1044                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
  1045                                                                           print("max_packets_allowed: ", max_packets_allowed)
  1046                                                                       
  1047         3          0.0      0.0      0.0                              for UE_name in UEs_to_transmit:
  1048         2          0.0      0.0      0.0                                  n_packets_transmitted = 0
  1049         2       1000.0    500.0      0.0                                  if max_packets_allowed == 0:
  1050                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
  1051                                                                               n_packets_transmitted = 0
  1052                                                                           else:
  1053         4       1000.0    250.0      0.0                                      while (n_packets_transmitted < max_packets_allowed and 
  1054         4       3000.0    750.0      0.0                                         n_packets_transmitted < len(packets_to_transmit[UE_name])):
  1055         4       3000.0    750.0      0.0                                          if self.debug_mode:
  1056                                                                                       print("n_packets_transmitted: ", n_packets_transmitted)
  1057                                                                                       print("UE_name: ", UE_name)
  1058                                           
  1059         4       1000.0    250.0      0.0                                          packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
  1060         4       1000.0    250.0      0.0                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
  1061         4       2000.0    500.0      0.0                                          if packet.arrival_time <= start_time:
  1062         2       1000.0    500.0      0.0                                              n_packets_transmitted += 1
  1063                                                                                   else:
  1064         2          0.0      0.0      0.0                                              break
  1065                                                                               
  1066                                                                               # TODO: check indexing of delivery_latency_contention
  1067         6       3000.0    500.0      0.0                                      delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
  1068         4       2000.0    500.0      0.0                                                      min_backoff*self.wifi_slot_time + self.DIFS
  1069         2       1000.0    500.0      0.0                                      delivery_times.append(delivery_time)
  1070                                           
  1071                                           
  1072         4       4000.0   1000.0      0.0                                      for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
  1073         2       2000.0   1000.0      0.0                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
  1074         2       3000.0   1500.0      0.0                                          packet.status = PacketStatus.DROPPED
  1075                                           
  1076         2          0.0      0.0      0.0                                      if n_packets_transmitted > 0: 
  1077                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
  1078                                                                               # across all UEs. Avoids the case that no UE transmits and 
  1079                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
  1080                                                                               # from UEs_winning_backoff?)
  1081         4       2000.0    500.0      0.0                                          self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
  1082         2       1000.0    500.0      0.0                                                                  self.UEs[UE_name].CWmax)
  1083                                                                               
  1084         2       2000.0   1000.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
  1085         2       1000.0    500.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
  1086         2       1000.0    500.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
  1087         2          0.0      0.0      0.0                                          .append(n_packets_transmitted)
  1088                                                                           
  1089                                           
  1090                                                                           
  1091         2          0.0      0.0      0.0                                  n_packets_transmitted_per_UE.append(n_packets_transmitted)
  1092                                           
  1093         1       1000.0   1000.0      0.0                              total_packets_transmitted = sum(n_packets_transmitted_per_UE)
  1094         1          0.0      0.0      0.0                              if total_packets_transmitted > 0:
  1095         1          0.0      0.0      0.0                                  if self.debug_mode:
  1096                                                                               print("start_time: ", start_time)
  1097                                           
  1098         1       1000.0   1000.0      0.0                                  start_time = max(delivery_times)
  1099                                           
  1100         1       1000.0   1000.0      0.0                                  if self.debug_mode:
  1101                                                                               print("delivery_time: ", delivery_times)
  1102                                                                               print("UEs: ", UEs_to_transmit)
  1103                                                                               print("\n")
  1104                                                                       elif total_packets_transmitted == 0:
  1105                                                                           start_time = start_time + advance_time
  1106                                                                           if self.debug_mode:
  1107                                                                               # This gets triggered towards the end of the slot
  1108                                                                               # as delivery time exceeds the end time of the slot
  1109                                                                               print("Should not happen! start_time: ", start_time)
  1110                                                                               print("UEs: ", UEs_to_transmit)
  1111                                                                               print("Line collision Delivery time: ", delivery_times)
  1112                                                                               print("\n")
  1113                                           
  1114         1     426000.0 426000.0      0.0                      print("Mean packets transmitted: ", np.mean(n_transmitted_array))
  1115                                                               # print("array of transmission numbers: ", n_transmitted_array)