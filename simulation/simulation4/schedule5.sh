#!/bin/bash

# Directory containing the files
DIRECTORY="../experiment_configs/simulation4/10UEs_schedule5/generated_configs/"

# Loop through all files in the directory
for FILE in "$DIRECTORY"/*; do
  if [ -f "$FILE" ]; then
    FILENAME=$(basename "$FILE")
    echo "$FILENAME"
    python3 simulation4.py ../wireless_parameters/wireless_parameters_DL_MU_964B_80MHz.json "../experiment_configs/simulation4/10UEs_schedule5/generated_configs/$FILENAME" &> "logs/$FILENAME.log"
  fi
done
