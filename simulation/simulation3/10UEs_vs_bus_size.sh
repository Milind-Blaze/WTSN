# python3 simulation3_onlyCSMA.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_dummy.json 
# python3 simulation3_onlyCSMA.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_10_extension2.json 
# python3 simulation3_onlyCSMA.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_5_extension2.json
# python3 simulation3_onlyCSMA.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_2_extension.json 

# With the faster code
# echo "3 UEs"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet/3UEs.json > logs/3UEs.log
# echo "5 UEs"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet/5UEs.json > logs/5UEs.log
# echo "7 UEs"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet/7UEs.json > logs/7UEs.log
# echo "10 UEs"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet/10UEs.json > logs/10UEs.log

# echo "2 aggr"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_2.json > logs/2aggr.log
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_2_extension.json > logs/2aggr_ext.log

# echo "5 aggr"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_5.json > logs/5aggr_ext.log
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_5_extension.json > logs/5aggr_ext.log
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_5_extension2.json > logs/5aggr_ext2.log

# echo "10 aggr"
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_10.json > logs/10aggr_ext.log
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_10_extension.json > logs/10aggr_ext.log
# python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3/10UEs_bus_size_10_extension2.json > logs/10aggr_ext2.log




# With mode 4 code
echo "3 UEs"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet_mode4/3UEs.json > logs/3UEs.log
echo "5 UEs"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet_mode4/5UEs.json > logs/5UEs.log
echo "7 UEs"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet_mode4/7UEs.json > logs/7UEs.log
echo "10 UEs"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/basic_csma_1_packet_mode4/10UEs.json > logs/10UEs.log

echo "2 aggr"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_2.json > logs/2aggr.log
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_2_extension.json > logs/2aggr_ext.log

echo "5 aggr"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_5.json > logs/5aggr_ext.log
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_5_extension.json > logs/5aggr_ext.log
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_5_extension2.json > logs/5aggr_ext2.log

echo "10 aggr"
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_10.json > logs/10aggr_ext.log
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_10_extension.json > logs/10aggr_ext.log
python3 simulation3_onlyCSMA_optimized.py ../wireless_parameters.json ../experiment_configs/simulation3_mode4/10UEs_bus_size_10_extension2.json > logs/10aggr_ext2.log
