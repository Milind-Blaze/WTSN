import json
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath('../../../'))

from utils import *

# grouped roundrobin

template_config_path = "./template_config.json"
configs_output_folder = "./generated_configs/"

with open(template_config_path, 'r') as f:
    template_config = json.load(f)

contention_UE_indices_list = [[5],[4,5],[4,5,6],[3,4,5,6], [3,4,5,6,7],[2,3,4,5,6,7]]
qbv_window_sizes = [690, 1000, 1250, 1500, 2000, 2500]
contention_window_sizes = range(700, 2600, 100)
lambda_range_parameters = [[-4.5, -2.68, 20]]
contention_iterations = [5]*20 
num_iterations_arrival = 15
# contention_window_sizes = [1500, 3000, 4500]
# num_UEs_together = 2


for contention_UE_indices in contention_UE_indices_list:
    for qbv_window_size in qbv_window_sizes:
        for contention_window_size in contention_window_sizes:
            config = template_config.copy()
            config["schedule_config"]["qbv_window_size"] = qbv_window_size
            config["schedule_config"]["contention_window_size"] = contention_window_size
            config["schedule_config"]["contention_UE_indices"] = contention_UE_indices
            config["num_iterations_arrival"] = num_iterations_arrival
            config["lambda_range_parameters"] = lambda_range_parameters
            config["num_iterations_contention"] = contention_iterations
            

            os.makedirs(configs_output_folder, exist_ok=True)
            config_name = "_".join(str(x) for x in contention_UE_indices) + \
                f"_UEs_{qbv_window_size}_q_{contention_window_size}_c.json"
            config_output_path = os.path.join(configs_output_folder, config_name)
            config_json = json.dumps(config, indent=4, cls=NumpyEncoder)
            with open(config_output_path, "w") as file:
                file.write(config_json)
