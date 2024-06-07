mkdir -p logs/

echo "sf1" 
python3 simulation5.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation5/playing_around/10UEs_dynamic_grr_sf1.json > logs/sf1.log

echo "sf2" 
python3 simulation5.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation5/playing_around/10UEs_dynamic_grr_sf2.json > logs/sf2.log