# With varying Qbv window size
mkdir -p logs
# # echo "Qbv window size 597"
# # python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_roundrobin/10UEs_qbv_window_597.json > logs/597.log
# # echo "Qbv window size 660"
# # python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_roundrobin/10UEs_qbv_window_660.json > logs/660.log
# # echo "Qbv window size 1000"
# # python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_roundrobin/10UEs_qbv_window_1000.json > logs/1000.log
# # echo "Qbv window size 1500"
# # python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_roundrobin/10UEs_qbv_window_1500.json > logs/1500.log
# echo "Qbv window size 660"
# python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_64B.json ../experiment_configs/simulation4/10UEs_roundrobin/10UEs_qbv_window_690.json > logs/690.log

echo "Qbv window size 660"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation4/10UEs_roundrobin_964B_80MHz/10UEs_qbv_window_660.json > logs/660.log
echo "Qbv window size 690"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation4/10UEs_roundrobin_964B_80MHz/10UEs_qbv_window_690.json > logs/690.log
echo "Qbv window size 1000"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation4/10UEs_roundrobin_964B_80MHz/10UEs_qbv_window_1000.json > logs/1000.log
echo "Qbv window size 1250"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation4/10UEs_roundrobin_964B_80MHz/10UEs_qbv_window_1250.json > logs/1250.log
echo "Qbv window size 1500"
python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json ../experiment_configs/simulation4/10UEs_roundrobin_964B_80MHz/10UEs_qbv_window_1500.json > logs/1500.log
