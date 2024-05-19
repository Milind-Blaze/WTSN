#!/usr/bin/env python
# coding: utf-8

# # Simulation 3

# In[1]:


"""
Simulating the WTSN setting

Authors: Milind Kumar Vaddiraju, ChatGPT, Copilot
"""

# Necessary imports
import argparse
import copy
import cProfile
from datetime import datetime
import io
import json
# %matplotlib inline
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from multiprocessing import Pool
import numpy as np
import os
import pickle
import pstats
import sys
import time

sys.path.insert(0, os.path.abspath('..'))

from network_classes import *
from utils import *
from schedules import *

# @profile
def run_simulation_for_lambda(lambda_value, lambda_index, config, parameters,\
                            results_directory_experiment):
    """
    Run the simulation for a given lambda value

    Args:
    lambda_value: float, the lambda value to run the simulation for
    lambda_index: int, the index of the lambda value in the original lambda_range
    config: dict, the configuration for the simulation

    Returns:
    results_per_lambda_per_iteration_contention: dict, the results of the simulation
    """

    setting_reserved = config["setting_reserved"]
    setting_contention = config["setting_contention"]
    payload_size = {"reserved": parameters[setting_reserved]["payload_size"]*parameters[setting_reserved]["aggregation"], 
                    "contention": parameters[setting_contention]["payload_size"]*parameters[setting_contention]["aggregation"]}
    delivery_latency = {"reserved": parameters[setting_reserved]["delivery_latency"],
                        "contention": parameters[setting_contention]["delivery_latency"]}
    PER = {"reserved":  parameters[setting_reserved]["PER"], 
        "contention":  parameters[setting_contention]["PER"]}
    aggregation_limit = config["aggregation_limit"]

    num_UEs = config["num_UEs"]
    UE_names = ["UE" + str(i) for i in range(num_UEs)]
    num_packets_per_ue = config["num_packets_per_ue"]  # Number of packets per UE for the whole period
    packet_sizes = [parameters[setting_reserved]["payload_size"]] # TODO: Both have same packet size, but what if they don't?
    priorities = [1]

    UE_arrival = ["Poisson"]*num_UEs
    UE_serve_mode = ["Mode 2"]*num_UEs
    num_iterations_arrival = config["num_iterations_arrival"]
    CWmin = config["CWmin"]
    CWmax = config["CWmax"]

    ## Schedule parameters for reserved base schedule
    start_offset = config["start_offset"] # microseconds
    end_time = config["duration"] + start_offset # microseconds
    schedule_config = config["schedule_config"]

    # Network properties
    # Obtained from the sheet
    wifi_slot_time = config["wifi_slot_time"] # microseconds
    DIFS = config["DIFS"] # microseconds


    num_iterations_contention = config["num_iterations_contention"]
    mode_contention = config["mode_contention"] 
    advance_time = config["advance_time"] # microseconds
    debug_mode = config["debug_mode"]

    percentile_to_plot = config["percentile_to_plot"]

    UEs_directory = os.path.join(results_directory_experiment, "UEs")
    os.makedirs(UEs_directory, exist_ok=True)
    schedules_directory = os.path.join(results_directory_experiment, "schedules")
    os.makedirs(schedules_directory, exist_ok=True)

    # Create a schedule, UEs and serve the packets


    schedule_contention, cycle_time = create_schedule_dynamic(UE_names, start_offset, end_time, \
                                                    config, lambda_value, \
                                                    delivery_latency["contention"])

    # print(schedule_reserved)
    print(schedule_contention)

    schedule_filename = "schedule" + str(lambda_index) + ".png"
    save_schedule_plot(UE_names, schedule_contention, start_offset, cycle_time + 100, \
                        os.path.join(schedules_directory, schedule_filename))



    print("\n###### Lambda value: " + str(lambda_value), ", Lambda index: " + str(lambda_index), "######")
        
        
    results_per_lambda_per_iteration_contention = {}
    mean_latencies_across_arrivals = []
    percentile_latencies_across_arrivals = []
    n_packets_not_served_across_arrivals = []
    # contention_wins_across_arrivals = []
    # bus_occupancy_across_arrivals = []
    queue_slope_across_arrivals = []

    for num_arrival_iteration in range(num_iterations_arrival):
        print("\nArrival iteration: " + str(num_arrival_iteration))
        # Create UEs and packets
        
        UEs_contention = {}
            
        for i in range(num_UEs): 
            # TODO: Move the UE creation parameters to the cell above?
            UE_temp = UE(i, {1: 0, 2: 1}, UE_arrival[i], UE_serve_mode[i],  num_packets_per_ue, \
                        CWmin=CWmin, CWmax=CWmax)
            UE_temp.set_poisson_lambda(lambda_value)
            UE_temp.initialize_transmission_record(schedule_contention)
            UE_temp.generate_packets(schedule_contention, packet_sizes, priorities) # TODO: Change this
            UEs_contention[UE_names[i]] = UE_temp

        # TODO: Check that the delivery times are always in ascending order
        # TODO: check that the arrival times are always in ascending order

        # TODO: Make this more general i.e handle packet statuses directly instead of opearting under the 
        # restrictions of this simulation
        print("Num packets: " + str(UEs_contention["UE0"].n_packets))


        # Serve the packets with contention
        results_iteration = {}
        mean_latencies = []
        percentile_latencies = []
        n_packets_not_served_array = []
        # contention_wins = []
        # bus_occupancy = []
        queue_slope = []
        

        for i in range(num_iterations_contention[lambda_index]):
            print("Contention iteration: " + str(i))
            UEs_contention_temp = copy.deepcopy(UEs_contention)

            test_network = Network(wifi_slot_time, DIFS, UEs_contention_temp, debug_mode)
            test_network.serve_packets(schedule_contention, mode_contention, 
                                        payload_size = payload_size,
                                        delivery_latency = delivery_latency,
                                        PER = PER,
                                        advance_time = advance_time,
                                        aggregation_limit = aggregation_limit)
            
            
            latencies = []
            # bus_occupancy_across_ues = []
            # contention_wins_across_ues = []
            queue_slope_across_ues = []
            n_packets_not_served = 0

            for ue in UEs_contention_temp:
                # print("UE: ", ue)
                UE_temp = UEs_contention_temp[ue]
                latencies_UE = UE_temp.obtain_packet_latency()
                latencies_UE = [latency for latency in latencies_UE if latency is not None]
                n_packets_not_served += UE_temp.n_packets - len(latencies_UE)
                latencies.extend(latencies_UE)
                # contention_wins_across_ues.append(UE_temp.transmission_record[0]["num_wins"])
                # bus_occupancy_across_ues.append(np.mean(UE_temp.transmission_record[0]["num_transmissions"]))

                # queue_lengths = np.array(UE_temp.transmission_record[0]["queue_information"]["queue_lengths"])
                # queue_times = np.array(UE_temp.transmission_record[0]["queue_information"]["queue_times"])
                queue_lengths = []
                queue_times = []
                for slot in UE_temp.transmission_record:
                    queue_lengths.extend(UE_temp.transmission_record[slot]["queue_information"]["queue_lengths"])
                    queue_times.extend(UE_temp.transmission_record[slot]["queue_information"]["queue_times"])
                slope, intercept = np.polyfit(queue_times, queue_lengths, 1)
                queue_slope_across_ues.append(slope)
            
            mean_latencies.append(np.mean(latencies))
            percentile_latencies.append(compute_percentile(latencies, percentile_to_plot))
            n_packets_not_served_array.append(n_packets_not_served)
            # contention_wins.append(np.mean(contention_wins_across_ues))
            # bus_occupancy.append(np.mean(bus_occupancy_across_ues))
            queue_slope.append(np.mean(queue_slope_across_ues))

            if config["save_UEs"]:
                print("Save UEs_contetion_temp")
                # results_iteration[i] = UEs_contention_temp
                UEs_filename = os.path.join(UEs_directory, "UEs_contention_" + \
                                            str(lambda_index) + "_" + str(num_arrival_iteration) + "_" + \
                                            str(i) + ".pkl")
                with open(UEs_filename, "wb") as file:
                    pickle.dump(UEs_contention_temp, file)

            # results_iteration[i] = UEs_contention_temp 
        # for key in results_iteration:
        #     print("results_iteration " + str(key), results_iteration[key])

        # TODO: Scale to multiple UEs, currently you're extracting the results only for one UE,
        # but you should be extracting the results for all UEs
        mean_latencies_across_arrivals.append(np.mean(mean_latencies))
        percentile_latencies_across_arrivals.append(np.mean(percentile_latencies))
        n_packets_not_served_across_arrivals.append(np.mean(n_packets_not_served_array))
        # contention_wins_across_arrivals.append(np.mean(contention_wins))
        # bus_occupancy_across_arrivals.append(np.mean(bus_occupancy))
        queue_slope_across_arrivals.append(np.mean(queue_slope))


        # results_per_lambda_per_iteration_contention[num_arrival_iteration] = results_iteration
    
    result_temp = {}        
    result_temp["mean_latency"] = np.mean(mean_latencies_across_arrivals)
    result_temp["mean_latency_std"] = np.std(mean_latencies_across_arrivals)
    result_temp["percentile_latency"] = np.mean(percentile_latencies_across_arrivals)
    result_temp["percentile_latency_std"] = np.std(percentile_latencies_across_arrivals)
    result_temp["n_packets_not_served"] = np.mean(n_packets_not_served_across_arrivals)
    result_temp["n_packets_not_served_std"] = np.std(n_packets_not_served_across_arrivals)
    # result_temp["contention_wins"] = np.mean(contention_wins_across_arrivals)
    # result_temp["bus_occupancy"] = np.mean(bus_occupancy_across_arrivals)
    result_temp["queue_slope"] = np.mean(queue_slope_across_arrivals)

    return (result_temp, schedule_contention)


# @profile
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("parameters_filename", help = "file containing the wireless parameters")
    parser.add_argument("config_filename", help = "file containing the experiment configuration")
    parser.add_argument("--show_plots", default = False, help = "show plots", action="store_true")
    parser.add_argument("--save_UEs", default = False, help = "save UEs", action="store_true")
    parser.add_argument("--single_process", default = False, \
                        help = "if set, use a single process instead of pool", action="store_true")
    args = parser.parse_args()

    # In[2]:


    # Parameters affecting how a packet is served: essentially MCS and latency from the Excel sheet
    # TODO: integrate MCS usage into the UE instead of having it outside
    # TODO: Create a simple CSV file of this



    # TODO: Remove the 67us from this that contains backoff 
    parameters_filename = args.parameters_filename
    with open(parameters_filename, 'r') as f:
        parameters = json.load(f)






    config_file = args.config_filename
    with open(config_file, 'r') as f:
        config = json.load(f)

    # Set the simulation parameters

    results_directory_simulation = config["results_directory_simulation"]

    setting_reserved = config["setting_reserved"]
    setting_contention = config["setting_contention"]
    payload_size = {"reserved": parameters[setting_reserved]["payload_size"]*parameters[setting_reserved]["aggregation"], 
                    "contention": parameters[setting_contention]["payload_size"]*parameters[setting_contention]["aggregation"]}
    delivery_latency = {"reserved": parameters[setting_reserved]["delivery_latency"],
                        "contention": parameters[setting_contention]["delivery_latency"]}
    PER = {"reserved":  parameters[setting_reserved]["PER"], 
        "contention":  parameters[setting_contention]["PER"]}
    aggregation_limit = config["aggregation_limit"]


    num_UEs = config["num_UEs"]
    UE_names = ["UE" + str(i) for i in range(num_UEs)]
    num_packets_per_ue = config["num_packets_per_ue"]  # Number of packets per UE for the whole period
    packet_sizes = [parameters[setting_reserved]["payload_size"]] # TODO: Both have same packet size, but what if they don't?
    priorities = [1]

    
    lambda_range = np.array([])
    for lambda_range_parameter in config["lambda_range_parameters"]:
        lambda_range_low = lambda_range_parameter[0]
        lambda_range_high = lambda_range_parameter[1]
        num_lambda_values = lambda_range_parameter[2]
        lambda_range = np.concatenate((lambda_range, \
                                    np.logspace(lambda_range_low, lambda_range_high, num_lambda_values)))


    lambda_original = copy.deepcopy(lambda_range)
    UE_arrival = ["Poisson"]*num_UEs
    UE_serve_mode = ["Mode 2"]*num_UEs
    num_iterations_arrival = config["num_iterations_arrival"]
    CWmin = config["CWmin"]
    CWmax = config["CWmax"]


    ## Schedule parameters for reserved base schedule
    start_offset = config["start_offset"] # microseconds
    end_time = config["duration"] + start_offset # microseconds
    



    # Network properties
    # Obtained from the sheet
    wifi_slot_time = config["wifi_slot_time"] # microseconds
    DIFS = config["DIFS"] # microseconds
    schedule_config = config["schedule_config"]



    # Plot information
    percentile_to_plot = config["percentile_to_plot"]
    num_iterations_contention = config["num_iterations_contention"]
    mode_contention = config["mode_contention"] 
    advance_time = config["advance_time"] # microseconds
    debug_mode = False
    config["debug_mode"] = debug_mode
    config["save_UEs"] = args.save_UEs

    assert len(num_iterations_contention) == len(lambda_range), "Lengths not equal"
    # In[22]:


    # Create a schedule, UEs and serve the packets

    # slots_temp = {}
    # slots_temp[0] = Slot(0, start_offset, end_time, "contention", UE_names)
    # schedule_contention = Schedule(start_offset, end_time, 1, slots_temp)


    
    # results_per_lambda_contention = {}
    # count = 0

    execution_start_time = time.time()



    # Create a results directory folder using results_directory_simulation and the current time
    experiment_folder_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    results_directory_experiment = os.path.join(results_directory_simulation, experiment_folder_name)
    os.makedirs(results_directory_experiment, exist_ok=True)
    


    # Save the schedule figure


    if args.single_process:
        results_parallel = {}
        
        for i in range(len(lambda_range)):
            results_parallel[i] = run_simulation_for_lambda(lambda_range[i], i, config, parameters, \
                                                            results_directory_experiment)
    else:
        with Pool() as pool:
            results_parallel = pool.starmap(run_simulation_for_lambda, \
                                [(lambda_range[i], i, config, parameters, \
                                    results_directory_experiment) for i in range(len(lambda_range))]) 


    results_allUEs_per_lambda_contention = {}
    schedules = {}
    for i in range(len(lambda_range)):
        results_allUEs_per_lambda_contention[lambda_range[i]] = results_parallel[i][0]
        schedules[lambda_range[i]] = results_parallel[i][1]
        

    execution_finish_time = time.time()
    execution_duration = execution_finish_time - execution_start_time


   


    # Save the parameters and the results of the experiment to a file

    experiment_parameters = {
        "config_file": config_file,
        "setting_reserved": parameters[setting_reserved],
        "setting_contention": parameters[setting_contention],
        "aggregation_limit": aggregation_limit,
        "schedule_config": schedule_config,
        "num_UEs": num_UEs,
        "num_packets_per_ue": num_packets_per_ue,
        "packet_sizes": packet_sizes,
        "priorities": priorities,
        "UE_arrival": UE_arrival,
        "UE_serve_mode": UE_serve_mode,
        "start_offset": start_offset, # microseconds
        "end_time": end_time,
        "percentile_to_plot": percentile_to_plot,
        "wifi_slot_time": wifi_slot_time,
        "DIFS": DIFS,
        "num_iterations_contention": num_iterations_contention,
        "num_iterations_arrival": num_iterations_arrival,
        "contention_mode": mode_contention,
        "advance_time": advance_time,
        "CWmin": CWmin,
        "CWmax": CWmax,
        "lambda_range": lambda_range,
        "execution_duration": execution_duration,
        "lambda_range_parameters": config["lambda_range_parameters"],
        "config": config,
    }

    # Write experiment_parameters_json to a json file with filename experiment_parameters.json

    experiment_parameters_json = json.dumps(experiment_parameters, indent=4, cls=NumpyEncoder)
    experiment_parameters_json_filename = os.path.join(results_directory_experiment, \
                                                    "experiment_parameters.json")
    with open(experiment_parameters_json_filename, "w") as file:
        file.write(experiment_parameters_json)


    experiment_parameters_pickle = {
        "schedule_contention": schedules,
        "results_allUEs_per_lambda_contention": results_allUEs_per_lambda_contention,
        "experiment_parameters": experiment_parameters
    }

    experiment_parameters_pickle_filename = os.path.join(results_directory_experiment, \
                                                        "experiment_parameters.pkl")

    with open(experiment_parameters_pickle_filename, "wb") as file:
        pickle.dump(experiment_parameters_pickle, file)


    # In[26]:


    lambda_range = lambda_original

    # lambda_range = lambda_range[:8]

    scale = "linear"
    percentile_filename = "percentile_latency_allUEs_all_" + scale + ".png"
    percentile_slope_filename = "percentile_slope_allUEs_all_" + scale + ".png"
    mean_filename = "mean_latency_allUEs_all_" + scale + ".png"
    mean_slope_filename = "mean_slope_allUEs_all_" + scale + ".png"
    n_packets_not_served_filename = "n_packets_not_served_allUEs_all_" + scale + ".png"
    scaling_factor = 10**6

    # Plot the percentile curve

    plt.figure(figsize=(10, 8))
    # percentiles = []
    # for lambda_value in lambda_range:
    #     percentiles.append(results_allUEs_per_lambda_reserved[lambda_value]["percentile_latency"])
    # plt.plot(np.array(lambda_range)*(schedule_reserved.end_time - schedule_reserved.start_time), \
    #          percentiles, ".-", label = "reserved")

    percentiles_contention = []
    percentiles_contention_std = []
    for lambda_value in lambda_range:
        percentiles_contention.append(results_allUEs_per_lambda_contention[lambda_value]["percentile_latency"])
        percentiles_contention_std.append(\
            results_allUEs_per_lambda_contention[lambda_value]["percentile_latency_std"])
    plt.errorbar(np.array(lambda_range)*scaling_factor, \
            percentiles_contention, percentiles_contention_std, label = "contention", fmt='.-', \
            capsize=3)
    # plt.plot(n_packets_generated, percentiles)
    plt.xlabel("lambda (packets/s)")
    plt.ylabel(str(percentile_to_plot) + "percentile latency (us)")
    plt.legend()

    if scale == "log":
            plt.yscale('log')

    title = (f"{percentile_to_plot} percentile latency vs lambda"
            )
    plt.title(title)
    # Insert a textbox at the lowest y value of the plot and have y axis be the label
    plt.text(0, percentiles_contention[0], str(np.round(percentiles_contention[0],2)), \
            fontsize=12, verticalalignment='bottom')
    plt.tight_layout()


    plt.savefig(os.path.join(results_directory_experiment, percentile_filename))
    if args.show_plots:
        plt.show()


    # Plot the mean latency curve

    plt.figure(figsize=(10, 8))
    # mean_latencies = []
    # for lambda_value in lambda_range:
    #     mean_latencies.append(results_allUEs_per_lambda_reserved[lambda_value]["mean_latency"])
    # plt.plot(np.array(lambda_range)*(schedule_reserved.end_time - schedule_reserved.start_time),\
    #          mean_latencies, ".-", label = "reserved")



    mean_latencies_contention = []
    mean_latencies_contention_std = []
    for lambda_value in lambda_range:
        mean_latencies_contention.append(results_allUEs_per_lambda_contention[lambda_value]["mean_latency"])
        mean_latencies_contention_std.append(\
            results_allUEs_per_lambda_contention[lambda_value]["mean_latency_std"])
    plt.errorbar(np.array(lambda_range)*scaling_factor,\
            mean_latencies_contention, mean_latencies_contention_std, label = "contention", fmt='.-', \
            capsize=3)

    plt.text(0, mean_latencies_contention[0], str(np.round(mean_latencies_contention[0],2)), \
            fontsize=12, verticalalignment='bottom')

    plt.legend()

    plt.xlabel("lambda (packets/s)")
    plt.ylabel("Mean latency (us)")

    if scale == "log":
            plt.yscale('log')

    title = (f"Mean latency vs lambda"
            )
    plt.title(title)
    plt.tight_layout()

    plt.savefig(os.path.join(results_directory_experiment, mean_filename))

    if args.show_plots:
        plt.show()


    unserved_packets_contention = []
    unserved_packets_contention_std = []
    for lambda_value in lambda_range:
        unserved_packets_contention.append(results_allUEs_per_lambda_contention[lambda_value]["n_packets_not_served"])
        unserved_packets_contention_std.append(\
            results_allUEs_per_lambda_contention[lambda_value]["n_packets_not_served_std"])
    plt.errorbar(np.array(lambda_range)*scaling_factor,\
            np.array(unserved_packets_contention) + 1, np.array(unserved_packets_contention_std) + 0.001, label = "contention", fmt='.-', \
            capsize=3)


    # plt.text(0, unserved_packets_contention[0], str(np.round(unserved_packets_contention[0],2)), \
            #  fontsize=12, verticalalignment='bottom')

    plt.legend()

    plt.xlabel("lambda (packets/s)")
    plt.ylabel("Unserved packets")

    if scale == "log":
            plt.yscale('log')

    title = (f"Unserved vs lambda"
            )
    plt.title(title)
    plt.tight_layout()

    plt.savefig(os.path.join(results_directory_experiment, n_packets_not_served_filename))

    if args.show_plots:
        plt.show()



    # bus_occupancy_contention = []
    # for lambda_value in lambda_range:
    #     bus_occupancy_contention.append(results_allUEs_per_lambda_contention[lambda_value]["bus_occupancy"])
    # plt.plot(np.array(lambda_range)*scaling_factor, \
    #         bus_occupancy_contention, '.-', label = "contention")
    # # plt.plot(n_packets_generated, percentiles)
    # plt.xlabel("lambda*schedule_duration (us)")
    # plt.ylabel("Bus occupancy")
    # plt.legend()

    # if scale == "log":
    #         plt.yscale('log')

    # title = (f"Simulation 3 Bus occupancy vs lambda, \n PER = {PER},\n"
    #         f"num_UEs: {num_UEs}, \n"
    #         f"allowed_payload: {payload_size} B, \n "
    #         f"packet size: {packet_sizes[0]} B, \n"
    #         f"delivery_latency: {delivery_latency} us ,\n"
    #         )
    # plt.title(title)
    # # Insert a textbox at the lowest y value of the plot and have y axis be the label
    # plt.tight_layout()

    # if args.show_plots:
    #     plt.show()


    # wins_contention = []
    # for lambda_value in lambda_range:
    #     wins_contention.append(results_allUEs_per_lambda_contention[lambda_value]["contention_wins"])
    # plt.plot(np.array(lambda_range)*scaling_factor, \
    #         wins_contention, '.-', label = "contention")
    # # plt.plot(n_packets_generated, percentiles)
    # plt.xlabel("lambda*schedule_duration (us)")
    # plt.ylabel("Contention wins")
    # plt.legend()

    # if scale == "log":
    #         plt.yscale('log')

    # title = (f"Simulation 3 Bus occupancy vs lambda, \n PER = {PER},\n"
    #         f"num_UEs: {num_UEs}, \n"
    #         f"allowed_payload: {payload_size} B, \n "
    #         f"packet size: {packet_sizes[0]} B, \n"
    #         f"delivery_latency: {delivery_latency} us ,\n"
    #         )
    # plt.title(title)
    # # Insert a textbox at the lowest y value of the plot and have y axis be the label
    # plt.tight_layout()

    # if args.show_plots:
    #     plt.show()

    

if __name__ == "__main__":
    main()




