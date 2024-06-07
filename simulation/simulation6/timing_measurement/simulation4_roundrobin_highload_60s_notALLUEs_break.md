Timer unit: 1e-09 s

Total time: 70.6513 s
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
   453         1       9000.0   9000.0      0.0          if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
   454                                                       for ue in self.UEs:
   455                                                           ue.serve_packets(base_schedule, **kwargs)
   456         1       2000.0   2000.0      0.0          elif service_mode_of_operation == "Mode 3":
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
   798         1       1000.0   1000.0      0.0          elif service_mode_of_operation == "Mode 4":
   799                                                       # Mode 4 is still contention as in Mode 3 but allows UEs to transmit dynamic 
   800                                                       # number of packets 
   801                                                       
   802         1       2000.0   2000.0      0.0              assert 'payload_size' in kwargs, "Payload size not provided"
   803         1       2000.0   2000.0      0.0              assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   804                                                           slots not provided"
   805         1       1000.0   1000.0      0.0              assert "contention" in kwargs['payload_size'], "Payload size for \
   806                                                           contention slots not provided"
   807         1          0.0      0.0      0.0              assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   808         1       7000.0   7000.0      0.0              assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   809                                                           reserved slots not provided"
   810         1          0.0      0.0      0.0              assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   811                                                           contention slots not provided"
   812         1          0.0      0.0      0.0              assert 'PER' in kwargs, "PER not provided"
   813         1       5000.0   5000.0      0.0              assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   814         1       1000.0   1000.0      0.0              assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   815         1          0.0      0.0      0.0              assert "aggregation_limit" in kwargs, "aggregation_limit not provided"
   816                                                       
   817                                           
   818         1          0.0      0.0      0.0              if "advance_time" in kwargs:
   819         1       2000.0   2000.0      0.0                  advance_time = kwargs["advance_time"]
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
   834         1       1000.0   1000.0      0.0              payload_size_reserved = kwargs['payload_size']["reserved"]
   835         1       1000.0   1000.0      0.0              payload_size_contention = kwargs['payload_size']["contention"]
   836         1       5000.0   5000.0      0.0              delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   837         1       1000.0   1000.0      0.0              delivery_latency_contention = kwargs['delivery_latency']["contention"]
   838         1          0.0      0.0      0.0              PER_reserved = kwargs['PER']["reserved"]    
   839         1       1000.0   1000.0      0.0              PER_contention = kwargs['PER']["contention"]
   840         1          0.0      0.0      0.0              aggregation_limit = kwargs['aggregation_limit']
   841                                           
   842         1      10000.0  10000.0      0.0              assert len(delivery_latency_contention) > 1, "Deliver latency is an array"
   843                                                       
   844                                           
   845         1       6000.0   6000.0      0.0              UEs_all = set()
   846       601     354000.0    589.0      0.0              for slot in base_schedule.schedule:
   847       600     841000.0   1401.7      0.0                  UEs_all.update(base_schedule.schedule[slot].UEs)
   848                                                       
   849         1       1000.0   1000.0      0.0              if self.debug_mode:
   850                                                           print("UEs for queue measurement: ", UEs_all)
   851                                           
   852       601     627000.0   1043.3      0.0              for slot in base_schedule.schedule:
   853       600     930000.0   1550.0      0.0                  if base_schedule.schedule[slot].mode == "reserved":
   854                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   855                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   856                                                               # Get the packets that can be served in this slot
   857                                                               payload_used = 0
   858                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   859                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   860                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   861                                                                           or packet.status == PacketStatus.DROPPED):
   862                                                                           # TODO: Currently, this assumes that there will always be more packets
   863                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   864                                                                           # always the maximum possible. However, if there are fewer packets than
   865                                                                           # paylaod size, then the delivery latency will be lower
   866                                                                           if payload_used + packet.size <= payload_size_reserved:
   867                                                                               # TODO: Add a guard interval
   868                                                                               # TODO: Implement number of retries-currently there are no retries
   869                                                                               # within the slot
   870                                                                               payload_used += packet.size
   871                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   872                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   873                                                                                                       delivery_latency_reserved
   874                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   875                                                                                       "Packet delivery time exceeds slot end time" 
   876                                                                                   packet.status = PacketStatus.DELIVERED
   877                                                                               else:
   878                                                                                   packet.status = PacketStatus.DROPPED
   879                                                                           else:
   880                                                                               packet.status = PacketStatus.QUEUED
   881                                                           
   882                                                           
   883       600     358000.0    596.7      0.0                  elif base_schedule.schedule[slot].mode == "contention":
   884       600     393000.0    655.0      0.0                      start_time = base_schedule.schedule[slot].start_time
   885                                                               # Contend only with the spcified UEs
   886       600     283000.0    471.7      0.0                      UEs_to_contend = base_schedule.schedule[slot].UEs
   887                                           
   888                                                               # Create queues of all packets to be trasmitted for each UE
   889                                                               # TODO: Check how this works when you have a mix of slots
   890       600     285000.0    475.0      0.0                      packets_to_transmit = {}
   891       600     186000.0    310.0      0.0                      arrival_times = {}
   892                                                               # for UE_name in UEs_all:
   893      1200     995000.0    829.2      0.0                      for UE_name in UEs_to_contend:
   894       600     317000.0    528.3      0.0                          packets_per_UE = []
   895       600     221000.0    368.3      0.0                          arrivals_per_UE = []
   896  24035985 9032972000.0    375.8     12.8                          for packet in self.UEs[UE_name].packets:
   897  24035984        2e+10    640.0     21.8                              if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   898                                                                           # TODO: dropped and queued packets are treated the same way
   899  24035385        1e+10    458.0     15.6                                  if (packet.status == PacketStatus.ARRIVED 
   900  23241351        1e+10    441.7     14.5                                      or packet.status == PacketStatus.QUEUED 
   901  23241351        1e+10    508.0     16.7                                      or packet.status == PacketStatus.DROPPED):
   902                                                                               
   903    794034  413085000.0    520.2      0.6                                      packets_per_UE.append(packet.sequence_number)
   904    794034  378654000.0    476.9      0.5                                      arrivals_per_UE.append(packet.arrival_time)
   905                                                                       else: 
   906       599     683000.0   1140.2      0.0                                  break
   907                                                                   
   908       600    1010000.0   1683.3      0.0                          packets_to_transmit[UE_name] = packets_per_UE
   909       600     412000.0    686.7      0.0                          arrival_times[UE_name] = arrivals_per_UE
   910                                           
   911                                           
   912       600    2058000.0   3430.0      0.0                      n_transmitted_array = []
   913       600     187000.0    311.7      0.0                      queue_measurement_time = start_time
   914                                           
   915                                                               # Measure queues at the start of the slot
   916                                                               # for UE_name in UEs_all:
   917      1200    1242000.0   1035.0      0.0                      for UE_name in UEs_to_contend:
   918       600    9461000.0  15768.3      0.0                          queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
   919       600    7618000.0  12696.7      0.0                          self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
   920       600     639000.0   1065.0      0.0                          self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
   921    319061  457272000.0   1433.2      0.6                      while start_time < base_schedule.schedule[slot].end_time:
   922                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   923                                                                   # each UE and return the minimum backoff time, if there is more than
   924                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   925                                                                   # and then draw again
   926                                                                   
   927                                           
   928    318461  159243000.0    500.0      0.2                          if start_time - queue_measurement_time >= 1000:
   929                                                                       # for UE_name in UEs_all:
   930     89046   35096000.0    394.1      0.0                              for UE_name in UEs_to_contend:
   931     44523   75993000.0   1706.8      0.1                                  queue_length = bisect.bisect_right(arrival_times[UE_name], start_time)
   932     44523   38269000.0    859.5      0.1                                  self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_lengths"].append(queue_length)
   933     44523   37311000.0    838.0      0.1                                  self.UEs[UE_name].transmission_record[slot]["queue_information"]["queue_times"].append(start_time)
   934     44523   11533000.0    259.0      0.0                              queue_measurement_time = start_time
   935                                           
   936                                                                   
   937    318461  117850000.0    370.1      0.2                          UEs_with_packets = []
   938    636922  339187000.0    532.5      0.5                          for UE_name in UEs_to_contend:
   939    318461  167918000.0    527.3      0.2                              if len(packets_to_transmit[UE_name]) > 0:
   940    301792  114421000.0    379.1      0.2                                  earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   941    301792  210025000.0    695.9      0.3                                  if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   942     85909   39198000.0    456.3      0.1                                      UEs_with_packets.append(UE_name)
   943                                                                       
   944                                           
   945    318461  146118000.0    458.8      0.2                          if len(UEs_with_packets) > 0:
   946     85909   33027000.0    384.4      0.0                              backoff_times = {}
   947    171818   64920000.0    377.8      0.1                              for UE_name in UEs_with_packets:
   948                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   949     85909  551948000.0   6424.8      0.8                                  backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   950     85909   79887000.0    929.9      0.1                              min_backoff = min(backoff_times.values())
   951                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   952     85909  139673000.0   1625.8      0.2                              UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   953                                                                                       backoff_times[UE_name] == min_backoff]
   954                                                                   else:
   955    232552   70257000.0    302.1      0.1                              UEs_to_transmit = []
   956    232552   69794000.0    300.1      0.1                              min_backoff = None
   957                                           
   958                                                                   # save some debug information
   959    318461  123693000.0    388.4      0.2                          if self.debug_mode:
   960                                                                       self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   961                                                                                               start_time, min_backoff, UEs_to_transmit])
   962                                                                   
   963                                                                   # TODO: remove this
   964    318461   86985000.0    273.1      0.1                          n_packets_transmitted = 0
   965                                           
   966                                                                   
   967    318461  142145000.0    446.3      0.2                          if len(UEs_to_transmit) == 0:
   968    232552   81811000.0    351.8      0.1                              start_time = start_time + advance_time
   969    232552  123878000.0    532.7      0.2                              if start_time > base_schedule.schedule[slot].end_time:
   970       226     107000.0    473.5      0.0                                  start_time = base_schedule.schedule[slot].end_time
   971                                                                       
   972                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   973                                                                       # the current start time 
   974                                           
   975    232552  146538000.0    630.1      0.2                              if self.debug_mode:
   976                                                                           print("start_time: ", start_time)
   977                                                                           print("UEs: ", UEs_to_transmit)
   978                                           
   979     85909   34816000.0    405.3      0.0                          elif len(UEs_to_transmit) == 1:
   980                                                                       # Transmit all packets that have arrived till this point (start_time)
   981     85909   32131000.0    374.0      0.0                              UE_name = UEs_to_transmit[0]
   982                                           
   983                                                                       # Determine delivery time
   984    257727  118659000.0    460.4      0.2                              time_remaining = base_schedule.schedule[slot].end_time - start_time - \
   985    171818   62924000.0    366.2      0.1                                              min_backoff*self.wifi_slot_time - self.DIFS
   986    171818   91366000.0    531.8      0.1                              max_packets_time_remaining = bisect.bisect_right(\
   987     85909   23866000.0    277.8      0.0                                  delivery_latency_contention, time_remaining)
   988     85909   53912000.0    627.5      0.1                              max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
   989     85909   22979000.0    267.5      0.0                              n_packets_transmitted = 0
   990                                           
   991     85909   33090000.0    385.2      0.0                              if self.debug_mode:
   992                                                                           print("\nUE_name: ", UE_name)
   993                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
   994                                                                           print("start_time: ", start_time)
   995                                                                           print("min_backoff: ", min_backoff)
   996                                                                           print("DIFS: ", self.DIFS)
   997                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
   998                                                                           print("time_remaining: ", time_remaining)
   999                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
  1000                                                                           print("max_packets_allowed: ", max_packets_allowed)
  1001                                           
  1002                                                                           
  1003                                           
  1004     85909   32458000.0    377.8      0.0                              if max_packets_allowed == 0:
  1005                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
  1006       374     150000.0    401.1      0.0                                  n_packets_transmitted = 0
  1007                                                                       else:
  1008    878966  330372000.0    375.9      0.5                                  while (n_packets_transmitted < max_packets_allowed and 
  1009    800751  393759000.0    491.7      0.6                                         n_packets_transmitted < len(packets_to_transmit[UE_name])):
  1010    800534  269447000.0    336.6      0.4                                      if self.debug_mode:
  1011                                                                                   print("n_packets_transmitted: ", n_packets_transmitted)
  1012                                                                                   print("packet_sequence_number: ", packets_to_transmit[UE_name][n_packets_transmitted])
  1013                                                                                   print(" packets_to_transmit[UE_name]: ",  packets_to_transmit[UE_name])
  1014                                           
  1015    800534  300407000.0    375.3      0.4                                      packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
  1016    800534  324911000.0    405.9      0.5                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
  1017    800534  384110000.0    479.8      0.5                                      if packet.arrival_time <= start_time:
  1018    793431  260121000.0    327.8      0.4                                          n_packets_transmitted += 1
  1019                                                                               else:
  1020      7103    1691000.0    238.1      0.0                                          break
  1021                                                                           
  1022                                                                           # TODO: check indexing of delivery_latency_contention
  1023    256605  146782000.0    572.0      0.2                                  delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
  1024    171070   66328000.0    387.7      0.1                                                  min_backoff*self.wifi_slot_time + self.DIFS
  1025                                                                           
  1026    878966  342655000.0    389.8      0.5                                  for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
  1027    793431  347080000.0    437.4      0.5                                      packet = self.UEs[UE_name].packets[packet_sequence_number]
  1028    793431 1849648000.0   2331.2      2.6                                      if self.UEs[UE_name].transmit_packet(PER_contention):
  1029    793431  574490000.0    724.1      0.8                                          packet.delivery_time = delivery_time 
  1030    793431  387377000.0    488.2      0.5                                          packet.status = PacketStatus.DELIVERED
  1031    793431  598825000.0    754.7      0.8                                          packets_to_transmit[UE_name].remove(packet_sequence_number)
  1032    793431  572531000.0    721.6      0.8                                          arrival_times[UE_name].remove(packet.arrival_time)
  1033    793431  627606000.0    791.0      0.9                                          assert len(arrival_times[UE_name]) == len(packets_to_transmit[UE_name]), \
  1034                                                                                       "Arrival times and packets to transmit are not the same length"
  1035                                                                               else:
  1036                                                                                   packet.status = PacketStatus.DROPPED
  1037                                                                           
  1038     85535   49857000.0    582.9      0.1                                  self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
  1039     85535   61910000.0    723.8      0.1                                  self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
  1040     85535   43669000.0    510.5      0.1                                  self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
  1041     85535   49687000.0    580.9      0.1                                      .append(n_packets_transmitted)
  1042                                                                               
  1043     85909   36106000.0    420.3      0.1                              if n_packets_transmitted > 0:
  1044     85535   29830000.0    348.7      0.0                                  if self.debug_mode:
  1045                                                                               print("start_time: ", start_time)
  1046                                           
  1047     85535   22601000.0    264.2      0.0                                  start_time = delivery_time 
  1048                                           
  1049     85535   30948000.0    361.8      0.0                                  if self.debug_mode:
  1050                                                                               print("delivery_time: ", delivery_time)
  1051                                                                               print("UEs: ", UEs_to_transmit)
  1052                                                                               print("\n")
  1053       374     108000.0    288.8      0.0                              elif n_packets_transmitted == 0:
  1054       374     117000.0    312.8      0.0                                  if max_packets_time_remaining == 0:
  1055       374     289000.0    772.7      0.0                                      start_time = base_schedule.schedule[slot].end_time
  1056       374     150000.0    401.1      0.0                                      if self.debug_mode:
  1057                                                                                   print("Start time advanced to end")
  1058                                                                                   print("Single UE, no packets transmitted")
  1059                                                                                   print("start_time: ", start_time)
  1060                                                                           else:
  1061                                                                               start_time = start_time + advance_time
  1062                                                                               if self.debug_mode:
  1063                                                                                   # This gets triggered towards the end of the slot
  1064                                                                                   # as delivery time exceeds the end time of the slot 
  1065                                                                                   print("Should not happen! start_time (advanced): ", start_time)
  1066                                                                                   print("UEs: ", UEs_to_transmit)
  1067                                                                                   print("\n")
  1068                                           
  1069                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
  1070     85909   60534000.0    704.6      0.1                              n_transmitted_array.append(n_packets_transmitted)
  1071                                           
  1072                                           
  1073                                                                   else:
  1074                                                                       # TODO: Fix the case where UEs contend but there's some of them
  1075                                                                       # have no data to transmit, then exclude them from the list of
  1076                                                                       # UEs contending, prevent packets from being dropped and
  1077                                                                       # prevent the contention window from being doubled
  1078                                                                       delivery_times = []
  1079                                                                       n_packets_transmitted_per_UE = []
  1080                                                                       time_remaining = base_schedule.schedule[slot].end_time - start_time - \
  1081                                                                                       min_backoff*self.wifi_slot_time - self.DIFS
  1082                                                                       # TODO: Make delivery_latency_contention different for different UEs
  1083                                                                       # using different MCSes
  1084                                                                       max_packets_time_remaining = bisect.bisect_right(\
  1085                                                                           delivery_latency_contention, time_remaining)
  1086                                                                       # TODO: Make aggregation different for different UEs
  1087                                                                       max_packets_allowed = min(max_packets_time_remaining, aggregation_limit)
  1088                                           
  1089                                                                       if self.debug_mode:
  1090                                                                           print("end_time: ", base_schedule.schedule[slot].end_time)
  1091                                                                           print("start_time: ", start_time)
  1092                                                                           print("min_backoff: ", min_backoff)
  1093                                                                           print("DIFS: ", self.DIFS)
  1094                                                                           print("wifi_slot_time: ", self.wifi_slot_time)
  1095                                                                           print("time_remaining: ", time_remaining)
  1096                                                                           print("max_packets_time_remaining: ", max_packets_time_remaining)
  1097                                                                           print("max_packets_allowed: ", max_packets_allowed)
  1098                                                                       
  1099                                                                       for UE_name in UEs_to_transmit:
  1100                                                                           n_packets_transmitted = 0
  1101                                                                           if max_packets_allowed == 0:
  1102                                                                           # TODO: handle this case by moving start time to the end of the slot or advancing by 10 us
  1103                                                                               n_packets_transmitted = 0
  1104                                                                           else:
  1105                                                                               while (n_packets_transmitted < max_packets_allowed and 
  1106                                                                                  n_packets_transmitted < len(packets_to_transmit[UE_name])):
  1107                                                                                   if self.debug_mode:
  1108                                                                                       print("n_packets_transmitted: ", n_packets_transmitted)
  1109                                                                                       print("UE_name: ", UE_name)
  1110                                           
  1111                                                                                   packet_sequence_number = packets_to_transmit[UE_name][n_packets_transmitted]
  1112                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
  1113                                                                                   if packet.arrival_time <= start_time:
  1114                                                                                       n_packets_transmitted += 1
  1115                                                                                   else:
  1116                                                                                       break
  1117                                                                               
  1118                                                                               # TODO: check indexing of delivery_latency_contention
  1119                                                                               delivery_time = start_time + delivery_latency_contention[n_packets_transmitted-1] + \
  1120                                                                                               min_backoff*self.wifi_slot_time + self.DIFS
  1121                                                                               delivery_times.append(delivery_time)
  1122                                           
  1123                                           
  1124                                                                               for packet_sequence_number in packets_to_transmit[UE_name][:n_packets_transmitted]:
  1125                                                                                   packet = self.UEs[UE_name].packets[packet_sequence_number]
  1126                                                                                   packet.status = PacketStatus.DROPPED
  1127                                           
  1128                                                                               if n_packets_transmitted > 0: 
  1129                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
  1130                                                                               # across all UEs. Avoids the case that no UE transmits and 
  1131                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
  1132                                                                               # from UEs_winning_backoff?)
  1133                                                                                   self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
  1134                                                                                                           self.UEs[UE_name].CWmax)
  1135                                                                               
  1136                                                                               self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
  1137                                                                               self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
  1138                                                                               self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
  1139                                                                                   .append(n_packets_transmitted)
  1140                                                                           
  1141                                           
  1142                                                                           
  1143                                                                           n_packets_transmitted_per_UE.append(n_packets_transmitted)
  1144                                           
  1145                                                                       total_packets_transmitted = sum(n_packets_transmitted_per_UE)
  1146                                                                       if total_packets_transmitted > 0:
  1147                                                                           if self.debug_mode:
  1148                                                                               print("start_time: ", start_time)
  1149                                           
  1150                                                                           start_time = max(delivery_times)
  1151                                           
  1152                                                                           if self.debug_mode:
  1153                                                                               print("delivery_time: ", delivery_times)
  1154                                                                               print("UEs: ", UEs_to_transmit)
  1155                                                                               print("\n")
  1156                                                                       elif total_packets_transmitted == 0:
  1157                                                                           if max_packets_time_remaining == 0:
  1158                                                                               start_time = base_schedule.schedule[slot].end_time
  1159                                                                               if self.debug_mode:
  1160                                                                                   print("Start time advanced to end")
  1161                                                                                   print("Single UE, no packets transmitted")
  1162                                                                                   print("start_time: ", start_time)
  1163                                                                           else:
  1164                                                                               start_time = start_time + advance_time
  1165                                                                               if self.debug_mode:
  1166                                                                                   # This gets triggered towards the end of the slot
  1167                                                                                   # as delivery time exceeds the end time of the slot
  1168                                                                                   print("Should not happen! start_time: ", start_time)
  1169                                                                                   print("UEs: ", UEs_to_transmit)
  1170                                                                                   print("Line collision Delivery time: ", delivery_times)
  1171                                                                                   print("\n")
  1172                                           
  1173                                                               # print("Mean packets transmitted: ", np.mean(n_transmitted_array))
  1174                                                               # print("array of transmission numbers: ", n_transmitted_array)