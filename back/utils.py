import string

import numpy as np


def random_string(y):
    """
    Generate a random string of given length
    """
    return "".join(np.random.choice(list(string.ascii_letters), y, replace=True))
