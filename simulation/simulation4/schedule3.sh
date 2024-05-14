echo "1500_1500_1UEs"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_schedule3/num_together_1/1500_1500_1.json  &> logs/1500_1500_1.log

echo "1500_3000_1UEs"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_schedule3/num_together_1/1500_3000_1.json  &> logs/1500_3000_1.log

echo "1500_4500_1UEs"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_schedule3/num_together_1/1500_4500_1.json  &> logs/1500_4500_1.log
