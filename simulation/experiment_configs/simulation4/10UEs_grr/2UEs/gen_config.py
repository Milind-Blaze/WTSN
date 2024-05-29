import json
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath('../../../../'))

from utils import *

# grouped roundrobin

template_config_path = "./template_config.json"
configs_output_folder = "./generated_configs/"

with open(template_config_path, 'r') as f:
    template_config = json.load(f)

num_UEs = 10
offsets = range(1, num_UEs)
qbv_window_sizes = [690, 800, 1000, 1100, 1250, 1500, 1700, 1900, 2000, 2200, 2500]
lambda_range_parameters = [[-4.5, -2.68, 20]]
contention_iterations = [5]*20 
num_iterations_arrival = 15
duration = 3*10**6



for offset in offsets:
    for qbv_window_size in qbv_window_sizes:
    
        config = template_config.copy()
        config["schedule_config"]["qbv_window_size"] = qbv_window_size
        config["schedule_config"]["offset"] = offset
        config["num_iterations_arrival"] = num_iterations_arrival
        config["lambda_range_parameters"] = lambda_range_parameters
        config["num_iterations_contention"] = contention_iterations
        config["duration"] = duration
        

        os.makedirs(configs_output_folder, exist_ok=True)
        config_name = f"2_UEs_{qbv_window_size}_q_{offset}_offset.json"
        config_output_path = os.path.join(configs_output_folder, config_name)
        config_json = json.dumps(config, indent=4, cls=NumpyEncoder)
        with open(config_output_path, "w") as file:
            file.write(config_json)
