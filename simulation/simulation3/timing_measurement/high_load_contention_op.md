Timer unit: 1e-09 s

Total time: 0.263321 s
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
   448         1       2000.0   2000.0      0.0          if service_mode_of_operation == "Mode 1" or service_mode_of_operation == "Mode 2":
   449                                                       for ue in self.UEs:
   450                                                           ue.serve_packets(base_schedule, **kwargs)
   451         1          0.0      0.0      0.0          elif service_mode_of_operation == "Mode 3":
   452                                                       # Mode 3 handles contention as well, the behaviour is the same as Mode 2 in the reserved
   453                                                       # slots but different in the contention slot
   454                                                       # The following are the assumptions in the reserved slot:
   455                                                           # Only one UE can transmit in the slot
   456                                                           # All UEs have the same characteristics: payload size, delivery latency, PER
   457                                                       # The following are the assumptions in the contetion slot:
   458                                                       # 
   459                                                       
   460         1          0.0      0.0      0.0              assert 'payload_size' in kwargs, "Payload size not provided"
   461         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['payload_size'], "Payload size for reserved \
   462                                                           slots not provided"
   463         1          0.0      0.0      0.0              assert "contention" in kwargs['payload_size'], "Payload size for \
   464                                                           contention slots not provided"
   465         1          0.0      0.0      0.0              assert 'delivery_latency' in kwargs, "Delivery latency not provided"
   466         1       1000.0   1000.0      0.0              assert "reserved" in kwargs['delivery_latency'], "Delivery latency for \
   467                                                           reserved slots not provided"
   468         1       1000.0   1000.0      0.0              assert "contention" in kwargs['delivery_latency'], "Delivery latency for \
   469                                                           contention slots not provided"
   470         1       1000.0   1000.0      0.0              assert 'PER' in kwargs, "PER not provided"
   471         1          0.0      0.0      0.0              assert "reserved" in kwargs['PER'], "PER for reserved slots not provided"
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
   488         1       1000.0   1000.0      0.0              payload_size_reserved = kwargs['payload_size']["reserved"]
   489         1       1000.0   1000.0      0.0              payload_size_contention = kwargs['payload_size']["contention"]
   490         1          0.0      0.0      0.0              delivery_latency_reserved = kwargs['delivery_latency']["reserved"]
   491         1          0.0      0.0      0.0              delivery_latency_contention = kwargs['delivery_latency']["contention"]
   492         1          0.0      0.0      0.0              PER_reserved = kwargs['PER']["reserved"]    
   493         1          0.0      0.0      0.0              PER_contention = kwargs['PER']["contention"]
   494                                                       
   495                                           
   496         2       3000.0   1500.0      0.0              for slot in base_schedule.schedule:
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
   528         1          0.0      0.0      0.0                      start_time = base_schedule.schedule[slot].start_time
   529                                                               # Contend only with the spcified UEs
   530         1          0.0      0.0      0.0                      UEs_to_contend = base_schedule.schedule[slot].UEs
   531                                           
   532                                                               # Create queues of all packets to be trasmitted for each UE
   533                                                               # TODO: Check how this works when you have a mix of slots
   534         1          0.0      0.0      0.0                      packets_to_transmit = {}
   535        11       3000.0    272.7      0.0                      for UE_name in UEs_to_contend:
   536        10       4000.0    400.0      0.0                          packets_per_UE = []
   537      6588    2090000.0    317.2      0.8                          for packet in self.UEs[UE_name].packets:
   538      6578    4064000.0    617.8      1.5                              if packet.arrival_time <= base_schedule.schedule[slot].end_time:
   539                                                                           # TODO: dropped and queued packets are treated the same way
   540      6578    3204000.0    487.1      1.2                                  if (packet.status == PacketStatus.ARRIVED 
   541                                                                               or packet.status == PacketStatus.QUEUED 
   542                                                                               or packet.status == PacketStatus.DROPPED):
   543                                                                               
   544      6578    3369000.0    512.2      1.3                                      packets_per_UE.append(packet.sequence_number)
   545                                                                   
   546        10       9000.0    900.0      0.0                          packets_to_transmit[UE_name] = packets_per_UE
   547                                           
   548                                           
   549                                           
   550                                           
   551         1       1000.0   1000.0      0.0                      n_transmitted_array = []
   552      2333    2805000.0   1202.3      1.1                      while start_time < base_schedule.schedule[slot].end_time:
   553                                                                   # Draw a random backoff time uniformly between 0 and CW for 
   554                                                                   # each UE and return the minimum backoff time, if there is more than
   555                                                                   # one UE with the same minimum backoff time, return that list of UEs1
   556                                                                   # and then draw again
   557                                                                   
   558                                                                   
   559      2332     991000.0    425.0      0.4                          UEs_with_packets = []
   560     25652    9616000.0    374.9      3.7                          for UE_name in UEs_to_contend:
   561     23320   12936000.0    554.7      4.9                              if len(packets_to_transmit[UE_name]) > 0:
   562     23299    9425000.0    404.5      3.6                                  earliest_packet_sequence_number = packets_to_transmit[UE_name][0]
   563     23299   16392000.0    703.5      6.2                                  if self.UEs[UE_name].packets[earliest_packet_sequence_number].arrival_time <= start_time:
   564     17782    8294000.0    466.4      3.1                                      UEs_with_packets.append(UE_name)
   565                                                                       
   566                                           
   567      2332    1113000.0    477.3      0.4                          if len(UEs_with_packets) > 0:
   568      2325    1041000.0    447.7      0.4                              backoff_times = {}
   569     20107    7578000.0    376.9      2.9                              for UE_name in UEs_with_packets:
   570                                                                           # TODO: Maybe initialize RNG each time to get different backoff times
   571     17782   79554000.0   4473.8     30.2                                  backoff_times[UE_name] = np.random.randint(0, self.UEs[UE_name].CW) 
   572      2325    2478000.0   1065.8      0.9                              min_backoff = min(backoff_times.values())
   573                                                                       # TODO: Check if start_time + min_backoff is less than the end time of the slot
   574      2325    7409000.0   3186.7      2.8                              UEs_to_transmit = [UE_name for UE_name in UEs_with_packets if \
   575                                                                                       backoff_times[UE_name] == min_backoff]
   576                                                                   else:
   577         7          0.0      0.0      0.0                              UEs_to_transmit = []
   578         7       5000.0    714.3      0.0                              min_backoff = None
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
   617      4664    3276000.0    702.4      1.2                          self.selected_UEs.append([base_schedule.schedule[slot].slot_index,
   618      2332     773000.0    331.5      0.3                                                    start_time, min_backoff, UEs_to_transmit])
   619                                           
   620      2332     656000.0    281.3      0.2                          n_packets_transmitted = 0
   621                                                                   
   622      2332    1124000.0    482.0      0.4                          if len(UEs_to_transmit) == 0:
   623         7       3000.0    428.6      0.0                              start_time = start_time + advance_time
   624                                                                       
   625                                                                       # Find the minimum packet arrival time for a packet that is  among the UEs which is greater than
   626                                                                       # the current start time 
   627                                           
   628         7       3000.0    428.6      0.0                              if self.debug_mode:
   629                                                                           print("start_time: ", start_time)
   630                                           
   631      2325    1067000.0    458.9      0.4                          elif len(UEs_to_transmit) == 1:
   632                                                                       # Transmit all packets that have arrived till this point (start_time)
   633      5898    2164000.0    366.9      0.8                              delivery_time = start_time + delivery_latency_contention + \
   634      3932    1334000.0    339.3      0.5                                              min_backoff*self.wifi_slot_time + self.DIFS
   635      1966    1049000.0    533.6      0.4                              if delivery_time <= base_schedule.schedule[slot].end_time:
   636      3920    1590000.0    405.6      0.6                                  for UE_name in UEs_to_transmit:
   637      1960     510000.0    260.2      0.2                                      payload_used = 0
   638                                                                               # TODO: Check if the slice is being used correctly
   639                                                                               # TODO: Change the slice size once delivery time is calculated
   640                                                                               # dynamically
   641      8420    5382000.0    639.2      2.0                                      for packet_sequence_number in packets_to_transmit[UE_name][:]:
   642                                                                                   # TODO: Check if this packet is being used correctly
   643      8418    4355000.0    517.3      1.7                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
   644      8418    5884000.0    699.0      2.2                                          if packet.arrival_time <= start_time:
   645      6623    2975000.0    449.2      1.1                                              if payload_used + packet.size <= payload_size_contention:
   646      6460    2384000.0    369.0      0.9                                                  payload_used += packet.size 
   647      6460    2051000.0    317.5      0.8                                                  n_packets_transmitted += 1
   648      6460   15783000.0   2443.2      6.0                                                  if self.UEs[UE_name].transmit_packet(PER_contention):
   649      6460    2539000.0    393.0      1.0                                                      packet.delivery_time = delivery_time 
   650      6460    3349000.0    518.4      1.3                                                      packet.status = PacketStatus.DELIVERED
   651      6460    4857000.0    751.9      1.8                                                      packets_to_transmit[UE_name].remove(packet_sequence_number)
   652                                                                                           else:
   653                                                                                               packet.status = PacketStatus.DROPPED
   654                                                                                       else:
   655       163     196000.0   1202.5      0.1                                                  break
   656                                                                                   else:
   657      1795    1940000.0   1080.8      0.7                                              break
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
   685      1960    1350000.0    688.8      0.5                                      self.UEs[UE_name].CW = self.UEs[UE_name].CWmin
   686      1960    1356000.0    691.8      0.5                                      self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   687      1960    1051000.0    536.2      0.4                                      self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   688      1960    1262000.0    643.9      0.5                                          .append(n_packets_transmitted)
   689                                                                               
   690      1966     682000.0    346.9      0.3                              if n_packets_transmitted > 0:
   691      1960     617000.0    314.8      0.2                                  if self.debug_mode:
   692                                                                               print("start_time: ", start_time)
   693                                           
   694      1960     564000.0    287.8      0.2                                  start_time = delivery_time 
   695                                           
   696      1960    1000000.0    510.2      0.4                                  if self.debug_mode:
   697                                                                               print("delivery_time: ", delivery_time)
   698                                                                               print("UEs: ", UEs_to_transmit)
   699         6       3000.0    500.0      0.0                              elif n_packets_transmitted == 0:
   700         6       4000.0    666.7      0.0                                  start_time = start_time + advance_time
   701         6          0.0      0.0      0.0                                  if self.debug_mode:
   702                                                                               # This gets triggered towards the end of the slot
   703                                                                               # as delivery time exceeds the end time of the slot 
   704                                                                               print("Should not happen! start_time (advanced): ", start_time)
   705                                                                               print("UEs: ", UEs_to_transmit)
   706                                                                               print("Line595 Delivery time: ", delivery_time)
   707                                                                       # print("n_packets_transmitted : ", n_packets_transmitted)
   708      1966    1102000.0    560.5      0.4                              n_transmitted_array.append(n_packets_transmitted)
   709                                           
   710                                           
   711                                                                   else:
   712                                                                       # TODO: Fix the case where UEs contend but there's some of them
   713                                                                       # have no data to transmit, then exclude them from the list of
   714                                                                       # UEs contending, prevent packets from being dropped and
   715                                                                       # prevent the contention window from being doubled
   716      1077     417000.0    387.2      0.2                              delivery_time = start_time + delivery_latency_contention + \
   717       718     229000.0    318.9      0.1                                              min_backoff*self.wifi_slot_time + self.DIFS
   718       359     197000.0    548.7      0.1                              if delivery_time <= base_schedule.schedule[slot].end_time:
   719       358     112000.0    312.8      0.0                                  n_transmitted_old = 0 # TODO: remove the need for this by cleaning up the logic of the code
   720      1107     404000.0    365.0      0.2                                  for UE_name in UEs_to_transmit: 
   721       749     196000.0    261.7      0.1                                      payload_used = 0
   722                                                                               
   723      3195    1793000.0    561.2      0.7                                      for packet_sequence_number in packets_to_transmit[UE_name][:]:
   724                                                                                   # TODO: Check if this packet is being used correctly
   725      3195    1636000.0    512.1      0.6                                          packet = self.UEs[UE_name].packets[packet_sequence_number]
   726      3195    2119000.0    663.2      0.8                                          if packet.arrival_time <= start_time:
   727      2506    1094000.0    436.6      0.4                                              if payload_used + packet.size <= payload_size_contention:
   728      2446     951000.0    388.8      0.4                                                  payload_used += packet.size 
   729      2446     812000.0    332.0      0.3                                                  n_packets_transmitted += 1
   730      2446    1306000.0    533.9      0.5                                                  packet.status = PacketStatus.DROPPED
   731                                                                                       else:
   732        60      70000.0   1166.7      0.0                                                  break
   733                                                                                   else:
   734       689     755000.0   1095.8      0.3                                              break
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
   750       749     289000.0    385.8      0.1                                      if n_packets_transmitted > 0: 
   751                                                                               # TODO: enforce behaviour only if at least one packet is transmitted 
   752                                                                               # across all UEs. Avoids the case that no UE transmits and 
   753                                                                               # contention window is still doubled (Done by redefining UEs_to_transmit
   754                                                                               # from UEs_winning_backoff?)
   755      1498    1106000.0    738.3      0.4                                          self.UEs[UE_name].CW = min(2*self.UEs[UE_name].CW + 1, 
   756       749     282000.0    376.5      0.1                                                                  self.UEs[UE_name].CWmax)
   757                                                                                   
   758       749     469000.0    626.2      0.2                                      self.UEs[UE_name].transmission_record[slot]["num_contentions"] += 1
   759       749     433000.0    578.1      0.2                                      self.UEs[UE_name].transmission_record[slot]["num_wins"] += 1
   760       749     376000.0    502.0      0.1                                      self.UEs[UE_name].transmission_record[slot]["num_transmissions"]\
   761       749     406000.0    542.1      0.2                                          .append(n_packets_transmitted - n_transmitted_old)
   762       749     291000.0    388.5      0.1                                      n_transmitted_old = n_packets_transmitted
   763                                                                                   
   764                                           
   765                                                                       # TODO: there is a corner case where a UE's backoff might finish just
   766                                                                       # after the end of delivery_time in which case it should transmit
   767                                                                       # right away instead of starting again
   768       359     131000.0    364.9      0.0                              if n_packets_transmitted > 0:
   769       358     127000.0    354.7      0.0                                  if self.debug_mode:
   770                                                                               print("start_time: ", start_time)
   771                                           
   772       358      86000.0    240.2      0.0                                  start_time = delivery_time
   773                                           
   774       358     121000.0    338.0      0.0                                  if self.debug_mode:
   775                                                                               print("delivery_time: ", delivery_time)
   776                                                                               print("UEs: ", UEs_to_transmit)
   777         1          0.0      0.0      0.0                              elif n_packets_transmitted == 0:
   778         1          0.0      0.0      0.0                                  start_time = start_time + 1
   779         1          0.0      0.0      0.0                                  if self.debug_mode:
   780                                                                               # This gets triggered towards the end of the slot
   781                                                                               # as delivery time exceeds the end time of the slot
   782                                                                               print("Should not happen! start_time: ", start_time)
   783                                                                               print("UEs: ", UEs_to_transmit)
   784                                                                               print("Line647 Delivery time: ", delivery_time)
   785                                           
   786         1     482000.0 482000.0      0.2                      print("Mean packets transmitted: ", np.mean(n_transmitted_array))
   787                                                               # print("array of transmission numbers: ", n_transmitted_array)