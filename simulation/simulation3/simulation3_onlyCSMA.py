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

def run_simulation_for_lambda(lambda_value, lambda_index, schedule, config, parameters):
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

    # Network properties
    # Obtained from the sheet
    wifi_slot_time = config["wifi_slot_time"] # microseconds
    DIFS = config["DIFS"] # microseconds


    num_iterations_contention = config["num_iterations_contention"]
    mode_contention = config["mode_contention"] 
    advance_time = config["advance_time"] # microseconds
    debug_mode = config["debug_mode"]


    # Create a schedule, UEs and serve the packets

    schedule_contention = schedule

    print("\n###### Lambda value: " + str(lambda_value), ", Lambda index: " + str(lambda_index), "######")
        
        
    results_per_lambda_per_iteration_contention = {}
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
        

        for i in range(num_iterations_contention[lambda_index]):
            print("Contention iteration: " + str(i))
            UEs_contention_temp = copy.deepcopy(UEs_contention)

            test_network = Network(wifi_slot_time, DIFS, UEs_contention_temp, debug_mode)
            test_network.serve_packets(schedule_contention, mode_contention, 
                                        payload_size = payload_size,
                                        delivery_latency = delivery_latency,
                                        PER = PER,
                                        advance_time = advance_time)
            
            


            results_iteration[i] = UEs_contention_temp 
        # for key in results_iteration:
        #     print("results_iteration " + str(key), results_iteration[key])

        # TODO: Scale to multiple UEs, currently you're extracting the results only for one UE,
        # but you should be extracting the results for all UEs
        

        results_per_lambda_per_iteration_contention[num_arrival_iteration] = results_iteration
    
    return results_per_lambda_per_iteration_contention



if __name__ == "__main__":


    parser = argparse.ArgumentParser()
    parser.add_argument("parameters_filename", help = "file containing the wireless parameters")
    parser.add_argument("config_filename", help = "file containing the experiment configuration")
    parser.add_argument("--show_plots", default = False, help = "enable debug mode", action="store_true")
    args = parser.parse_args()

    # In[2]:


    # Parameters affecting how a packet is served: essentially MCS and latency from the Excel sheet
    # TODO: integrate MCS usage into the UE instead of having it outside
    # TODO: Create a simple CSV file of this



    # TODO: Remove the 67us from this that contains backoff 
    parameters_filename = args.parameters_filename
    with open(parameters_filename, 'r') as f:
        parameters = json.load(f)





    # # In[27]:


    # # Set the simulation parameters

    # results_directory_simulation = "./results/simulation_3/"
    # config_file = "No config file"

    # setting_reserved = "setting 12"
    # setting_contention = "setting 12"
    # payload_size = {"reserved": parameters[setting_reserved]["payload_size"]*parameters[setting_reserved]["aggregation"], 
    #                 "contention": parameters[setting_contention]["payload_size"]*parameters[setting_contention]["aggregation"]}
    # delivery_latency = {"reserved": parameters[setting_reserved]["delivery_latency"],
    #                     "contention": parameters[setting_contention]["delivery_latency"]}
    # PER = {"reserved":  parameters[setting_reserved]["PER"], 
    #        "contention":  parameters[setting_contention]["PER"]}




    # num_UEs = 3
    # UE_names = ["UE" + str(i) for i in range(num_UEs)]
    # num_packets_per_ue = None  # Number of packets per UE for the whole period
    # packet_sizes = [parameters[setting_reserved]["payload_size"]] # TODO: Both have same packet size, but what if they don't?
    # priorities = [1]
    # # lambda_range = np.logspace(-4.5, -3, 20)
    # # lambda_range = np.concatenate((np.logspace(-4.5, -3, 10), np.logspace(-3, -2.2, 5)))
    # # For 10 UEs
    # # lambda_range = np.logspace(-4.5, -3.765, 15)
    # # For 3 UEs
    # # lambda_range = np.logspace(-4.5, -3.26, 15)
    # lambda_range = np.concatenate((np.logspace(-4.5, -3.43, 8), np.logspace(-3.34, -3.26, 7)))
    # # lambda_range = [10**(-4.5)]
    # lambda_original = copy.deepcopy(lambda_range)
    # UE_arrival = ["Poisson"]*num_UEs
    # UE_serve_mode = ["Mode 2"]*num_UEs
    # num_iterations_arrival = 20
    # CWmin = 15
    # CWmax = 1023


    # ## Schedule parameters for reserved base schedule
    # start_offset = 10 # microseconds
    # end_time = 1.5*10**6 + start_offset # microseconds


    # # Network properties
    # # Obtained from the sheet
    # wifi_slot_time = 9 # microseconds
    # DIFS = 34 # microseconds



    # # Plot information
    # percentile_to_plot = 99
    # num_iterations_contention = [2]*8 + [10]*7
    # mode_contention = "Mode 3" 
    # advance_time = 10 # microseconds
    # debug_mode = False



    # assert len(num_iterations_contention) == len(lambda_range), "Lengths not equal"


    # In[9]:


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



    # Plot information
    percentile_to_plot = config["percentile_to_plot"]
    num_iterations_contention = config["num_iterations_contention"]
    mode_contention = config["mode_contention"] 
    advance_time = config["advance_time"] # microseconds
    debug_mode = False
    config["debug_mode"] = debug_mode


    assert len(num_iterations_contention) == len(lambda_range), "Lengths not equal"
    # In[22]:


    # Create a schedule, UEs and serve the packets

    slots_temp = {}
    slots_temp[0] = Slot(0, start_offset, end_time, "contention", UE_names)
    schedule_contention = Schedule(start_offset, end_time, 1, slots_temp)


    # print(schedule_reserved)
    print(schedule_contention)

    results_per_lambda_contention = {}

    count = 0

    execution_start_time = time.time()

    profiler = cProfile.Profile()
    profiler.enable()

    with Pool() as pool:
        results_parallel = pool.starmap(run_simulation_for_lambda, \
                               [(lambda_range[i], i, schedule_contention, config, parameters) \
                                for i in range(len(lambda_range))])
        

    for i in range(len(lambda_range)):
        results_per_lambda_contention[lambda_range[i]] = results_parallel[i]

        

    execution_finish_time = time.time()
    execution_duration = execution_finish_time - execution_start_time


    # In[23]:


    # Create a results directory folder using results_directory_simulation and the current time
    experiment_folder_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    results_directory_experiment = os.path.join(results_directory_simulation, experiment_folder_name)
    os.makedirs(results_directory_experiment, exist_ok=True)
    # Plots: CDF of latencies, percentile latency vs lambda, mean latency vs lambda,
    # number of packets not served vs lambda


    # In[24]:


    results_allUEs_per_lambda_contention = {}
    for lambda_value in results_per_lambda_contention:
        print("\n\nlambda value: ", lambda_value)

        mean_latencies_across_arrivals = []
        percentile_latencies_across_arrivals = []
        n_packets_not_served_across_arrivals = []
        contention_wins_across_arrivals = []
        bus_occupancy_across_arrivals = []

        for num_iteration_arrival in results_per_lambda_contention[lambda_value]:
            mean_latencies = []
            percentile_latencies = []
            n_packets_not_served_array = []
            contention_wins = []
            bus_occupancy = []
            print("arrival iteration " + str(num_iteration_arrival))
            for iteration in results_per_lambda_contention[lambda_value][num_iteration_arrival]:
                latencies = []
                bus_occupancy_across_ues = []
                contention_wins_across_ues = []
                n_packets_not_served = 0
                # print("iteration", iteration)
                for ue in results_per_lambda_contention[lambda_value][num_iteration_arrival][iteration]:
                    # print("UE: ", ue)
                    UE_temp = results_per_lambda_contention[lambda_value][num_iteration_arrival][iteration][ue]
                    latencies_UE = UE_temp.obtain_packet_latency()
                    latencies_UE = [latency for latency in latencies_UE if latency is not None]
                    n_packets_not_served += UE_temp.n_packets - len(latencies_UE)
                    latencies.extend(latencies_UE)
                    contention_wins_across_ues.append(UE_temp.transmission_record[0]["num_wins"])
                    bus_occupancy_across_ues.append(np.mean(UE_temp.transmission_record[0]["num_transmissions"]))


                print("iteration", iteration)    
                mean_latencies.append(np.mean(latencies))
                percentile_latencies.append(compute_percentile(latencies, percentile_to_plot))
                n_packets_not_served_array.append(n_packets_not_served)
                contention_wins.append(np.mean(contention_wins_across_ues))
                bus_occupancy.append(np.mean(bus_occupancy_across_ues))

            print("Len(mean_latencies)", len(mean_latencies))
            mean_latencies_across_arrivals.append(np.mean(mean_latencies))
            percentile_latencies_across_arrivals.append(np.mean(percentile_latencies))
            n_packets_not_served_across_arrivals.append(np.mean(n_packets_not_served_array))
            contention_wins_across_arrivals.append(np.mean(contention_wins))
            bus_occupancy_across_arrivals.append(np.mean(bus_occupancy))

        result_temp = {}        
        result_temp["mean_latency"] = np.mean(mean_latencies_across_arrivals)
        result_temp["mean_latency_std"] = np.std(mean_latencies_across_arrivals)
        result_temp["percentile_latency"] = np.mean(percentile_latencies_across_arrivals)
        result_temp["percentile_latency_std"] = np.std(percentile_latencies_across_arrivals)
        result_temp["n_packets_not_served"] = np.mean(n_packets_not_served_across_arrivals)
        result_temp["n_packets_not_served_std"] = np.std(n_packets_not_served_across_arrivals)
        result_temp["contention_wins"] = np.mean(contention_wins_across_arrivals)
        result_temp["bus_occupancy"] = np.mean(bus_occupancy_across_arrivals)
        results_allUEs_per_lambda_contention[lambda_value] = result_temp


    # In[25]:


    # Save the parameters and the results of the experiment to a file

    experiment_parameters = {
        "config_file": config_file,
        "setting_reserved": parameters[setting_reserved],
        "setting_contention": parameters[setting_contention],
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
        "config": config,
    }

    # Write experiment_parameters_json to a json file with filename experiment_parameters.json

    experiment_parameters_json = json.dumps(experiment_parameters, indent=4, cls=NumpyEncoder)
    experiment_parameters_json_filename = os.path.join(results_directory_experiment, \
                                                    "experiment_parameters.json")
    with open(experiment_parameters_json_filename, "w") as file:
        file.write(experiment_parameters_json)


    experiment_parameters_pickle = {
        "schedule_contention": schedule_contention,
        "results_per_lambda_contention": results_per_lambda_contention,
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
    plt.errorbar(np.array(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time), \
            percentiles_contention, percentiles_contention_std, label = "contention", fmt='.-', \
            capsize=3)
    # plt.plot(n_packets_generated, percentiles)
    plt.xlabel("lambda*schedule_duration (us)")
    plt.ylabel(str(percentile_to_plot) + "percentile latency (us)")
    plt.legend()

    if scale == "log":
            plt.yscale('log')

    title = (f"Simulation 3 {percentile_to_plot} percentile latency vs lambda, \n PER = {PER},\n"
            f"num_UEs: {num_UEs}, \n"
            f"allowed_payload: {payload_size} B, \n "
            f"packet size: {packet_sizes[0]} B, \n"
            f"delivery_latency: {delivery_latency} us ,\n"
            )
    plt.title(title)
    # Insert a textbox at the lowest y value of the plot and have y axis be the label
    plt.text(0, percentiles_contention[0], str(np.round(percentiles_contention[0],2)), \
            fontsize=12, verticalalignment='bottom')
    plt.tight_layout()


    plt.savefig(os.path.join(results_directory_experiment, percentile_filename))
    if args.show_plots:
        plt.show()


    slope = np.diff(percentiles_contention)/(np.diff(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time))
    plt.title("Percentile latency slope")
    plt.xlabel("lambda*schedule_duration (us)")
    plt.ylabel(str(percentile_to_plot) + "percentile latency slope (us)")
    if scale == "log":
            plt.yscale('log')
            plt.ylim(10**-2, 10**2)
    plt.plot(np.array(lambda_range[1:])*(schedule_contention.end_time - schedule_contention.start_time), slope, ".-")
    plt.savefig(os.path.join(results_directory_experiment, percentile_slope_filename))
    if args.show_plots:
        plt.show()

    print(slope)
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
    plt.errorbar(np.array(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time),\
            mean_latencies_contention, mean_latencies_contention_std, label = "contention", fmt='.-', \
            capsize=3)

    plt.text(0, mean_latencies_contention[0], str(np.round(mean_latencies_contention[0],2)), \
            fontsize=12, verticalalignment='bottom')

    plt.legend()

    plt.xlabel("lambda*schedule_duration")
    plt.ylabel("Mean latency (us)")

    if scale == "log":
            plt.yscale('log')

    title = (f"Simulation 3 mean latency vs lambda, \n PER = {PER}, \n"
            f"num_UEs: {num_UEs}, \n"
            f"allowed_payload: {payload_size} B, \n "
            f"packet size: {packet_sizes[0]} B, \n"
            f"delivery_latency: {delivery_latency} us ,\n"
            )
    plt.title(title)
    plt.tight_layout()

    plt.savefig(os.path.join(results_directory_experiment, mean_filename))

    if args.show_plots:
        plt.show()


    slope = np.diff(mean_latencies_contention)/(np.diff(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time))
    plt.title("Mean latency slope")
    plt.xlabel("lambda*schedule_duration (us)")
    plt.ylabel("Mean percentile latency slope (us)")
    if scale == "log":
            plt.yscale('log')
    plt.plot(np.array(lambda_range[1:])*(schedule_contention.end_time - schedule_contention.start_time), slope, ".-")
    plt.savefig(os.path.join(results_directory_experiment, mean_slope_filename))
    if args.show_plots:
        plt.show()

    plt.figure(figsize=(10, 8))
    # mean_latencies = []
    # for lambda_value in lambda_range:
    #     mean_latencies.append(results_allUEs_per_lambda_reserved[lambda_value]["mean_latency"])
    # plt.plot(np.array(lambda_range)*(schedule_reserved.end_time - schedule_reserved.start_time),\
    #          mean_latencies, ".-", label = "reserved")

    # scale = "linear"


    unserved_packets_contention = []
    unserved_packets_contention_std = []
    for lambda_value in lambda_range:
        unserved_packets_contention.append(results_allUEs_per_lambda_contention[lambda_value]["n_packets_not_served"])
        unserved_packets_contention_std.append(\
            results_allUEs_per_lambda_contention[lambda_value]["n_packets_not_served_std"])
    plt.errorbar(np.array(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time),\
            np.array(unserved_packets_contention) + 1, np.array(unserved_packets_contention_std) + 0.001, label = "contention", fmt='.-', \
            capsize=3)


    # plt.text(0, unserved_packets_contention[0], str(np.round(unserved_packets_contention[0],2)), \
            #  fontsize=12, verticalalignment='bottom')

    plt.legend()

    plt.xlabel("lambda*schedule_duration")
    plt.ylabel("Unserved packets")

    if scale == "log":
            plt.yscale('log')

    title = (f"Simulation 3 unserved vs lambda, \n PER = {PER}, \n"
            f"num_UEs: {num_UEs}, \n"
            f"allowed_payload: {payload_size} B, \n "
            f"packet size: {packet_sizes[0]} B, \n"
            f"delivery_latency: {delivery_latency} us ,\n"
            )
    plt.title(title)
    plt.tight_layout()

    plt.savefig(os.path.join(results_directory_experiment, n_packets_not_served_filename))

    if args.show_plots:
        plt.show()



    bus_occupancy_contention = []
    for lambda_value in lambda_range:
        bus_occupancy_contention.append(results_allUEs_per_lambda_contention[lambda_value]["bus_occupancy"])
    plt.plot(np.array(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time), \
            bus_occupancy_contention, '.-', label = "contention")
    # plt.plot(n_packets_generated, percentiles)
    plt.xlabel("lambda*schedule_duration (us)")
    plt.ylabel("Bus occupancy")
    plt.legend()

    if scale == "log":
            plt.yscale('log')

    title = (f"Simulation 3 Bus occupancy vs lambda, \n PER = {PER},\n"
            f"num_UEs: {num_UEs}, \n"
            f"allowed_payload: {payload_size} B, \n "
            f"packet size: {packet_sizes[0]} B, \n"
            f"delivery_latency: {delivery_latency} us ,\n"
            )
    plt.title(title)
    # Insert a textbox at the lowest y value of the plot and have y axis be the label
    plt.tight_layout()

    if args.show_plots:
        plt.show()


    wins_contention = []
    for lambda_value in lambda_range:
        wins_contention.append(results_allUEs_per_lambda_contention[lambda_value]["contention_wins"])
    plt.plot(np.array(lambda_range)*(schedule_contention.end_time - schedule_contention.start_time), \
            wins_contention, '.-', label = "contention")
    # plt.plot(n_packets_generated, percentiles)
    plt.xlabel("lambda*schedule_duration (us)")
    plt.ylabel("Contention wins")
    plt.legend()

    if scale == "log":
            plt.yscale('log')

    title = (f"Simulation 3 Bus occupancy vs lambda, \n PER = {PER},\n"
            f"num_UEs: {num_UEs}, \n"
            f"allowed_payload: {payload_size} B, \n "
            f"packet size: {packet_sizes[0]} B, \n"
            f"delivery_latency: {delivery_latency} us ,\n"
            )
    plt.title(title)
    # Insert a textbox at the lowest y value of the plot and have y axis be the label
    plt.tight_layout()

    if args.show_plots:
        plt.show()

    profiler.disable()
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream = s).sort_stats('cumtime')
    stats.print_stats()
    # print this to a file
    stats_filename = os.path.join(results_directory_experiment, "profiler_stats.txt")
    with open(stats_filename, "w+") as file:
        file.write(s.getvalue())







