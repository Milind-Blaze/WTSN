Timer unit: 1e-09 s

Total time: 21.0731 s
File: /Users/milindkumarvaddiraju/projects/HVC_use/WTSN/simulation/network_classes.py
Function: serve_packets at line 437

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   437                                               def serve_packets(self, base_schedule: Schedule, service_mode_of_operation: str, 
   438                                                                 **kwargs) -> None:
   439                                                   '''
   440                                                   Function to serve the packets that the UEs have to transmit
   441                                           
   442                                                   Args:
   443                                                       base_schedule (Schedule): A base schedule specifying
   444                                                           Qbv windows for different UEs across time
   445                                                       service_mode_of_operation (str): Mode of operation of the UEs within 
   446                                                           a Qbv window
   447                                                   '''
   448         1       3000.0   3000.0      0.0          if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
   449                                                       for ue in self.UEs:
   450                                                           ue.serve_packets(base_schedule, **kwargs)
   451         1       1000.0   1000.0      0.0          elif service_mode_of_operation == "Mode 3":
   452                                                       # Mode 3 handles contention as well, the behaviour is the same as Mode 2 in the reserved
   453                                                       # slots but different in the contention slot
   454                                                       # The following are the assumptions in the reserved slot:
   455                                                           # Only one UE can transmit in the slot
   456                                                           # All UEs have the same characteristics: payload size, delivery latency, PER
   457                                                       # The following are the assumptions in the contetion slot:
   458                                                       # 
   459                                                       
   460         1       1000.0   1000.0      0.0              assert 'payload_size' in kwargs, "Payload size not provided"
   461         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   462                                                           slots not provided"
   463         1          0.0      0.0      0.0              assert "contention" in kwargs['payload_size'], "Payload size for \
   464                                                           contention slots not provided"
   465         1          0.0      0.0      0.0              assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   466         1          0.0      0.0      0.0              assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   467                                                           reserved slots not provided"
   468         1          0.0      0.0      0.0              assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   469                                                           contention slots not provided"
   470         1       1000.0   1000.0      0.0              assert 'PER' in kwargs, "PER not provided"
   471         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
   472         1          0.0      0.0      0.0              assert "contention" in kwargs['PER'], "PER for contention slots not provided"
   473                                           
   474         1          0.0      0.0      0.0              if "advance_time" in kwargs:
   475         1       1000.0   1000.0      0.0                  advance_time = kwargs["advance_time"]
   476                                                       else:
   477                                                           advance_time = 1
   478                                                       
   479         1       1000.0   1000.0      0.0              if self.debug_mode:
   480                                                           print("advance time: ", advance_time)
   481                                           
   482                                                       # Need to map PER to MCS somehow
   483                                                       
   484                                                       # TODO: maybe refactor the code to serve the reserved slots and contention slots
   485                                                       # separately
   486                                           
   487                                           
   488         1          0.0      0.0      0.0              payload_size_reserved = kwargs['payload_size']["reserved"]
   489         1          0.0      0.0      0.0              payload_size_contention = kwargs['payload_size']["contention"]
   490         1          0.0      0.0      0.0              delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   491         1       1000.0   1000.0      0.0              delivery_latency_contention = kwargs['delivery_latency']["contention"]
   492         1       1000.0   1000.0      0.0              PER_reserved = kwargs['PER']["reserved"]    
   493         1       1000.0   1000.0      0.0              PER_contention = kwargs['PER']["contention"]
   494                                                       
   495                                           
   496         2       5000.0   2500.0      0.0              for slot in base_schedule.schedule:
   497         1       1000.0   1000.0      0.0                  if base_schedule.schedule[slot].mode == "reserved":
   498                                                               assert len(base_schedule.schedule[slot].UEs) == 1 , "No UEs in reserved slot"
   499                                                               UE_name = base_schedule.schedule[slot].UEs[0]
   500                                                               # Get the packets that can be served in this slot
   501                                                               payload_used = 0
   502                                                               for packet in self.UEs[UE_name].packets: # Relying on this being ordered by sequence number
   503                                                                   if packet.arrival_time <= base_schedule.schedule[slot].start_time:
   504                                                                       if (packet.status == PacketStatus.ARRIVED or packet.status == PacketStatus.QUEUED 
   505                                                                           or packet.status == PacketStatus.DROPPED):
   506                                                                           # TODO: Currently, this assumes that there will always be more packets
   507                                                                           # ready to be transmitted than payload_size. So, the delivery latency is
   508                                                                           # always the maximum possible. However, if there are fewer packets than
   509                                                                           # paylaod size, then the delivery latency will be lower
   510                                                                           if payload_used + packet.size <= payload_size_reserved:
   511                                                                               # TODO: Add a guard interval
   512                                                                               # TODO: Implement number of retries-currently there are no retries
   513                                                                               # within the slot
   514                                                                               payload_used += packet.size
   515                                                                               if self.UEs[UE_name].transmit_packet(PER_reserved):
   516                                                                                   packet.delivery_time = base_schedule.schedule[slot].start_time + \
   517                                                                                                       delivery_latency_reserved
   518                                                                                   assert packet.delivery_time <= base_schedule.schedule[slot].end_time, \
   519                                                                                       "Packet delivery time exceeds slot end time" 
   520                                                                                   packet.status = PacketStatus.DELIVERED
   521                                                                               else:
   522                                                                                   packet.status = PacketStatus.DROPPED
   523                                                                           else:
   524                                                                               packet.status = PacketStatus.QUEUED
   525                                                           
   526                                                           
   527         1       1000.0   1000.0      0.0                  elif base_schedule.schedule[slot].mode == "contention":
   528         1       1000.0   1000.0      0.0                      start_time = base_schedule.schedule[slot].start_time
   529                                                               # Contend only with the spcified UEs
   530         1       1000.0   1000.0      0.0                      UEs_to_contend = base_schedule.schedule[slot].UEs
   531                                           
   532                                                               # Create queues of all packets to be trasmitted for each UE
   533                                                               # TODO: Check how this works when you have a mix of slots
   534         1       1000.0   1000.0      0.0                      packets_to_transmit = {}
   535        11       5000.0    454.5      0.0                      for UE_name in UEs_to_contend:
   536        10       1000.0    100.0      0.0                          packets_per_UE = []
   537      3175     954000.0    300.5      0.0                          for packet in self.UEs[UE_name].packets:
   538      3165    1764000.0    557.3      0.0                              if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   539                                                                           # TODO: dropped and queued packets are treated the same way
   540      3165    1475000.0    466.0      0.0                                  if (packet.status == PacketStatus.ARRIVED 
   541                                                                               or packet.status == PacketStatus.QUEUED 
   542                                                                               or packet.status == PacketStatus.DROPPED):
   543                                                                               
   544      3165    1539000.0    486.3      0.0                                      packets_per_UE.append(packet.sequence_number)
   545                                                                   
   546        10       6000.0    600.0      0.0                          packets_to_transmit[UE_name] = packets_per_UE
   547                                           
   548                                           
   549                                           
   550                                           
   551         1       1000.0   1000.0      0.0                      n_transmitted_array = []
   552    785314  865537000.0   1102.2      4.1                      while start_time < base_schedule.schedule[slot].end_time:
   553                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   554                                                                   # each UE and return the minimum backoff time, if there is more than
   555                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   556                                                                   # and then draw again
   557                                                                   
   558                                                                   
   559    785313  344569000.0    438.8      1.6                          UEs_with_packets = []
   560   8638443 3974877000.0    460.1     18.9                          for UE_name in UEs_to_contend:
   561   7853130 4095072000.0    521.5     19.4                              if len(packets_to_transmit[UE_name]) > 0:
   562   7825765 3079085000.0    393.5     14.6                                  earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   563   7825765 5040013000.0    644.0     23.9                                  if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   564      3323    3224000.0    970.2      0.0                                      UEs_with_packets.append(UE_name)
   565                                                                       
   566                                           
   567    785313  368674000.0    469.5      1.7                          if len(UEs_with_packets) > 0:
   568      3199    3901000.0   1219.4      0.0                              backoff_times = {}
   569      6522    3696000.0    566.7      0.0                              for UE_name in UEs_with_packets:
   570                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   571      3323   98355000.0  29598.3      0.5                                  backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   572      3199    5127000.0   1602.7      0.0                              min_backoff = min(backoff_times.values())
   573                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   574      3199    8936000.0   2793.4      0.0                              UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   575                                                                                       backoff_times[UE_name] == min_backoff]
   576                                                                   else:
   577    782114  203640000.0    260.4      1.0                              UEs_to_transmit = []
   578    782114  200395000.0    256.2      1.0                              min_backoff = None
   579                                           
   580                                           
   581                                                                   # backoff_times = {}
   582                                                                   # for UE_name in UEs_to_contend:
   583                                                                   #     # TODO: Maybe initialize RNG each time to get different backoff times
   584                                                                   #     backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   585                                                                   # min_backoff = min(backoff_times.values())
   586                                                                   # # TODO: Check if start_time + min_backoff is less than the end time of the slot
   587                                                                   # UEs_winning_backoff = [UE_name for UE_name in UEs_to_contend if \
   588                                                                   #                 backoff_times[UE_name] == min_backoff]
   589                                                                   
   590                                                                   # # CW_array = [self.UEs[UE_name].CW for UE_name in UEs_to_contend]
   591                                                                   # # backoff_times = np.random.randint(0, CW_array)
   592                                                                   # # min_backoff = np.min(backoff_times)
   593                                                                   # # UEs_winning_backoff = np.array(UEs_to_contend)[backoff_times == min_backoff]
   594                                           
   595                                                                   # assert len(UEs_winning_backoff) > 0, "No UEs to transmit"
   596                                                                   
   597                                                                   # # Check that at least one UE has a packet to transmit and if not,
   598                                                                   # # advance the start_time by 1 and redo the backoff
   599                                                                   # UEs_to_transmit = []
   600                                                                   # for UE_name in UEs_winning_backoff:
   601                                                                   #     if len(packets_to_transmit[UE_name]) > 0:
   602                                                                   #         earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   603                                                                   #         if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   604                                                                   #             UEs_to_transmit.append(UE_name)
   605                                                                           
   606                                           
   607                                           
   608                                                                   # UEs_to_transmit = [UE_name for UE_name in UEs_winning_backoff if \
   609                                                                   #                 any((packet.arrival_time <= start_time and  
   610                                                                   #                     (packet.status == PacketStatus.ARRIVED 
   611                                                                   #                     or packet.status == PacketStatus.QUEUED 
   612                                                                   #                     or packet.status == PacketStatus.DROPPED)) \
   613                                                                   #                     for packet in self.UEs[UE_name].packets)]
   614                                           
   615                                           
   616                                                                   # save some debug information
   617   1570626 1248665000.0    795.0      5.9                          self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   618    785313  258226000.0    328.8      1.2                                                    start_time, min_backoff, UEs_to_transmit])
   619                                           
   620    785313  220497000.0    280.8      1.0                          n_packets_transmitted = 0
   621                                                                   
   622    785313  345203000.0    439.6      1.6                          if len(UEs_to_transmit) == 0:
   623    782114  276896000.0    354.0      1.3                              start_time = start_time + advance_time
   624                                                                       
   625                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   626                                                                       # the current start time 
   627                                           
   628    782114  345116000.0    441.3      1.6                              if self.debug_mode:
   629                                                                           print("start_time: ", start_time)
   630                                           
   631      3199    1319000.0    412.3      0.0                          elif len(UEs_to_transmit) == 1:
   632                                                                       # Transmit all packets that have arrived till this point (start_time)
   633      9567    4091000.0    427.6      0.0                              delivery_time = start_time + delivery_latency_contention + \
   634      6378    2848000.0    446.5      0.0                                              min_backoff*self.wifi_slot_time + self.DIFS
   635      3189    2050000.0    642.8      0.0                              if delivery_time <= base_schedule.schedule[slot].end_time:
   636      6304    2502000.0    396.9      0.0                                  for UE_name in UEs_to_transmit:
   637      3152    1147000.0    363.9      0.0                                      payload_used = 0
   638                                                                               # TODO: Check if the slice is being used correctly
   639                                                                               # TODO: Change the slice size once delivery time is calculated
   640                                                                               # dynamically
   641      6316    7476000.0   1183.7      0.0                                      for packet_sequence_number in packets_to_transmit[UE_name][:]:
   642                                                                                   # TODO: Check if this packet is being used correctly
   643      6307    3361000.0    532.9      0.0                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
   644      6307    4218000.0    668.8      0.0                                          if packet.arrival_time <= start_time:
   645      3164    1798000.0    568.3      0.0                                              if payload_used + packet.size <= payload_size_contention:
   646      3164    1276000.0    403.3      0.0                                                  payload_used += packet.size 
   647      3164    1050000.0    331.9      0.0                                                  n_packets_transmitted += 1
   648      3164   15362000.0   4855.2      0.1                                                  if self.UEs[UE_name].transmit_packet(PER_contention):
   649      3164    2122000.0    670.7      0.0                                                      packet.delivery_time = delivery_time 
   650      3164    3793000.0   1198.8      0.0                                                      packet.status = PacketStatus.DELIVERED
   651      3164    3541000.0   1119.2      0.0                                                      packets_to_transmit[UE_name].remove(packet_sequence_number)
   652                                                                                           else:
   653                                                                                               packet.status = PacketStatus.DROPPED
   654                                                                                       else:
   655                                                                                           break
   656                                                                                   else:
   657      3143    2913000.0    926.8      0.0                                              break
   658                                           
   659                                           
   660                                           
   661                                                                               # for packet in self.UEs[UE_name].packets:
   662                                                                               #     if packet.arrival_time <= start_time:
   663                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   664                                                                               #             or packet.status == PacketStatus.QUEUED 
   665                                                                               #             or packet.status == PacketStatus.DROPPED):
   666                                                                               #             if payload_used + packet.size <= payload_size_contention:
   667                                                                               #                 payload_used += packet.size 
   668                                                                               #                 n_packets_transmitted += 1
   669                                                                               #                 if self.UEs[UE_name].transmit_packet(PER_contention):
   670                                                                               #                     packet.delivery_time = delivery_time 
   671                                                                               #                     packet.status = PacketStatus.DELIVERED
   672                                                                               #                     packets_to_transmit[UE_name].remove(packet.sequence_number)
   673                                                                               #                 else:
   674                                                                               #                     packet.status = PacketStatus.DROPPED
   675                                                                               #     else:
   676                                                                               #     # assume packets are in ascending order of arrival time
   677                                                                               #     # if you've already reached the packets that haven't arrived
   678                                                                               #     # then break and don't evaluate any further
   679                                                                               #         break
   680                                                                                       
   681                                                                               # reset the contention window
   682                                                                               # TODO: You're skipping cases towards the end where delivery time
   683                                                                               # exceeds the end time of the slot. Need to fix this in the 
   684                                                                               # variable delivery latency case
   685      3152    2094000.0    664.3      0.0                                      self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
   686      3152    3202000.0   1015.9      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   687      3152    1689000.0    535.9      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   688      3152    2362000.0    749.4      0.0                                          .append(n_packets_transmitted)
   689                                                                               
   690      3189    1133000.0    355.3      0.0                              if n_packets_transmitted > 0:
   691      3152    1167000.0    370.2      0.0                                  if self.debug_mode:
   692                                                                               print("start_time: ", start_time)
   693                                           
   694      3152     868000.0    275.4      0.0                                  start_time = delivery_time 
   695                                           
   696      3152    1318000.0    418.1      0.0                                  if self.debug_mode:
   697                                                                               print("delivery_time: ", delivery_time)
   698                                                                               print("UEs: ", UEs_to_transmit)
   699        37      14000.0    378.4      0.0                              elif n_packets_transmitted == 0:
   700        37       8000.0    216.2      0.0                                  start_time = start_time + advance_time
   701        37      15000.0    405.4      0.0                                  if self.debug_mode:
   702                                                                               # This gets triggered towards the end of the slot
   703                                                                               # as delivery time exceeds the end time of the slot 
   704                                                                               print("Should not happen! start_time (advanced): ", start_time)
   705                                                                               print("UEs: ", UEs_to_transmit)
   706                                                                               print("Line595 Delivery time: ", delivery_time)
   707                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
   708      3189    1880000.0    589.5      0.0                              n_transmitted_array.append(n_packets_transmitted)
   709                                           
   710                                           
   711                                                                   else:
   712                                                                       # TODO: Fix the case where UEs contend but there's some of them
   713                                                                       # have no data to transmit, then exclude them from the list of
   714                                                                       # UEs contending, prevent packets from being dropped and
   715                                                                       # prevent the contention window from being doubled
   716        30      12000.0    400.0      0.0                              delivery_time = start_time + delivery_latency_contention + \
   717        20       8000.0    400.0      0.0                                              min_backoff*self.wifi_slot_time + self.DIFS
   718        10       7000.0    700.0      0.0                              if delivery_time <= base_schedule.schedule[slot].end_time:
   719        10       6000.0    600.0      0.0                                  n_transmitted_old = 0 # TODO: remove the need for this by cleaning up the logic of the code
   720        30      10000.0    333.3      0.0                                  for UE_name in UEs_to_transmit: 
   721        20       8000.0    400.0      0.0                                      payload_used = 0
   722                                                                               
   723        40      30000.0    750.0      0.0                                      for packet_sequence_number in packets_to_transmit[UE_name][:]:
   724                                                                                   # TODO: Check if this packet is being used correctly
   725        40      19000.0    475.0      0.0                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
   726        40      23000.0    575.0      0.0                                          if packet.arrival_time <= start_time:
   727        20      12000.0    600.0      0.0                                              if payload_used + packet.size <= payload_size_contention:
   728        20      10000.0    500.0      0.0                                                  payload_used += packet.size 
   729        20       6000.0    300.0      0.0                                                  n_packets_transmitted += 1
   730        20      16000.0    800.0      0.0                                                  packet.status = PacketStatus.DROPPED
   731                                                                                       else:
   732                                                                                           break
   733                                                                                   else:
   734        20      10000.0    500.0      0.0                                              break
   735                                           
   736                                                                               # for packet in self.UEs[UE_name].packets:
   737                                                                               #     if packet.arrival_time <= start_time:
   738                                                                               #         if (packet.status == PacketStatus.ARRIVED 
   739                                                                               #             or packet.status == PacketStatus.QUEUED 
   740                                                                               #             or packet.status == PacketStatus.DROPPED):
   741                                                                               #             if payload_used + packet.size <= payload_size_contention:
   742                                                                               #                 n_packets_transmitted += 1
   743                                                                               #                 payload_used += packet.size 
   744                                                                               #                 packet.status = PacketStatus.DROPPED
   745                                                                               #     else:
   746                                                                               #         break
   747                                           
   748                                           
   749                                                                               # double contention window for each UE
   750        20       3000.0    150.0      0.0                                      if n_packets_transmitted > 0: 
   751                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
   752                                                                               # across all UEs. Avoids the case that no UE transmits and 
   753                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
   754                                                                               # from UEs_winning_backoff?)
   755        40      47000.0   1175.0      0.0                                          self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
   756        20      10000.0    500.0      0.0                                                                  self.UEs[UE_name].CWmax)
   757                                                                                   
   758        20      15000.0    750.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
   759        20      14000.0    700.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   760        20       9000.0    450.0      0.0                                      self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   761        20      10000.0    500.0      0.0                                          .append(n_packets_transmitted - n_transmitted_old)
   762        20       7000.0    350.0      0.0                                      n_transmitted_old = n_packets_transmitted
   763                                                                                   
   764                                           
   765                                                                       # TODO: there is a corner case where a UE's backoff might finish just
   766                                                                       # after the end of delivery_time in which case it should transmit
   767                                                                       # right away instead of starting again
   768        10       4000.0    400.0      0.0                              if n_packets_transmitted > 0:
   769        10       4000.0    400.0      0.0                                  if self.debug_mode:
   770                                                                               print("start_time: ", start_time)
   771                                           
   772        10       2000.0    200.0      0.0                                  start_time = delivery_time
   773                                           
   774        10       5000.0    500.0      0.0                                  if self.debug_mode:
   775                                                                               print("delivery_time: ", delivery_time)
   776                                                                               print("UEs: ", UEs_to_transmit)
   777                                                                       elif n_packets_transmitted == 0:
   778                                                                           start_time = start_time + 1
   779                                                                           if self.debug_mode:
   780                                                                               # This gets triggered towards the end of the slot
   781                                                                               # as delivery time exceeds the end time of the slot
   782                                                                               print("Should not happen! start_time: ", start_time)
   783                                                                               print("UEs: ", UEs_to_transmit)
   784                                                                               print("Line647 Delivery time: ", delivery_time)
   785                                           
   786         1     733000.0 733000.0      0.0                      print("Mean packets transmitted: ", np.mean(n_transmitted_array))
   787                                                               # print("array of transmission numbers: ", n_transmitted_array)