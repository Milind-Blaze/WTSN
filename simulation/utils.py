"""
File to store utility functions for the simulation

Author: Milind Kumar Vaddiraju, ChatGPT
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    

def save_schedule_plot(UE_names, schedule, start_offset, end_time, filename):
    """Save the schedule plot to a file"""
    # Plotting the schedule

    fig, ax = plt.subplots(figsize=(10, 5))

    # Define Y-axis labels and their corresponding positions
    ue_positions = {ue: i for i, ue in enumerate(UE_names)}
    height = 1  # Height of the rectangles

    # Plot rectangles for each slot
    for slot in schedule.schedule.values():
        for ue in slot.UEs:
            rect = Rectangle((slot.start_time, ue_positions[ue] - height / 2), slot.end_time - slot.start_time, height, color='red', alpha=0.8)
            ax.add_patch(rect)
            # ax.text((slot.start_time + slot.end_time) / 2, ue_positions[ue], ue, horizontalalignment='center', verticalalignment='center')

    # Set Y-axis with UE names
    ax.set_yticks(list(ue_positions.values()))
    ax.set_yticklabels(UE_names)

    # Set labels and title
    ax.set_xlabel('Time (microseconds)')
    ax.set_title('UE Activity Schedule')

    # Set limits for the axes
    ax.set_xlim(start_offset, end_time)
    ax.set_ylim(-1, len(UE_names))
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(filename)