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

num_UEs_together_list = [1,2,3,4]
qbv_window_sizes = [690, 1000, 1250, 1500, 2000, 2500]
contention_window_sizes = [690, 1000, 1250, 1500, 2000, 2500]
lambda_range_parameters = [[-4.5, -2.68, 20]]
contention_iterations = [5]*20
# contention_window_sizes = [1500, 3000, 4500]
# num_UEs_together = 2
results_directory_base = "../results/simulation_4/10UEs_schedule5/"

for num_UEs in num_UEs_together_list:
    for qbv_window_size in qbv_window_sizes:
        for contention_window_size in contention_window_sizes:
            config = template_config.copy()
            config["schedule_config"]["num_UEs_together_qbv"] = 1
            config["schedule_config"]["qbv_window_size"] = qbv_window_size
            config["schedule_config"]["contention_window_size"] = contention_window_size
            config["schedule_config"]["num_UEs_together_contention"] = num_UEs
            config["results_directory_simulation"] = results_directory_base 
            config["num_iterations_arrival"] = 10
            config["lambda_range_parameters"] = lambda_range_parameters
            config["num_iterations_contention"] = contention_iterations
            

            os.makedirs(configs_output_folder, exist_ok=True)
            config_name = f"{num_UEs}_UEs_{qbv_window_size}_qbv_{contention_window_size}_contention.json"
            config_output_path = os.path.join(configs_output_folder, config_name)
            config_json = json.dumps(config, indent=4, cls=NumpyEncoder)
            with open(config_output_path, "w") as file:
                file.write(config_json)
