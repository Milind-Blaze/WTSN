echo "urllc"
python3 simulation7_half_HVC.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/hotnets_legit_trial1/half_hvcs/contention_based/urllc_contention.json > urllc_contention_log.txt

echo "embb"
python3 simulation7_half_HVC.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/hotnets_legit_trial1/half_hvcs/contention_based/embb_contention.json > embb_contention_log.txt
