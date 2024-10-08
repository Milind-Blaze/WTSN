# echo "embb"
# python3 simulation10_halfHVC_dynamic.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/dynamic_HVCs/dynamicHBC_eMBB.json > dynamicHBC_eMBB.txt


# echo "urllc"
# python3 simulation10_halfHVC_dynamic.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/dynamic_HVCs/dynamicHBC_URLLC.json > dynamicHBC_URLLC.txt


# echo "embb"
# python3 simulation10_halfHVC_dynamic.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/dynamic_HVCs/dynamicHBCLLC_eMBB.json > dynamicHBCLLC_eMBB.txt


echo "urllc"
python3 simulation10_halfHVC_dynamic.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json ../experiment_configs/dynamic_HVCs/dynamicHBCLLC_URLLC.json > dynamicHBCLLC_URLLC.txt
