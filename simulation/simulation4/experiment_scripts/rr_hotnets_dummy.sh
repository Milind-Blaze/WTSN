#!/bin/bash
cd ../
mkdir -p logs/
# Directory containing the files
DIRECTORY="../experiment_configs/hotnets_dummy_results/roundrobin"

# Loop through all files in the directory
for FILE in "$DIRECTORY"/*; do
  if [ -f "$FILE" ]; then
    FILENAME=$(basename "$FILE")
    echo "$FILENAME"
    python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80Mhz_Nss2_98usBA.json "../experiment_configs/hotnets_dummy_results/$FILENAME" &> "logs/$FILENAME.log"
  fi
done
