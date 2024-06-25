echo "urllc"
python3 simulation7_half_HVC.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/hotnets_dummy_results/half_hvcs/urllc.json > urllc_log.txt

echo "embb"
python3 simulation7_half_HVC.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/hotnets_dummy_results/half_hvcs/embb.json > embb_log.txt
