"""
File to store utility functions for the simulation

Author: Milind Kumar Vaddiraju, ChatGPT
"""

import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)