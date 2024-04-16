import numpy as np
import cv2
from matplotlib import pyplot as plt
from configs import QUARTERS, DATA_PATH


def get_quarter(quarter):
    threshold = 0.5
    prediction = np.logical_or(
        quarter[:, :, 1] > threshold, quarter[:, :, 2] > threshold
    ).astype(bool)
    scores = []
    for model in QUARTERS:
        solution = np.zeros((8, 8), dtype=bool)
        x, y = zip(*model["goals"].values())
        solution[x, y] = True
        score = (np.logical_and(solution, ~prediction)).sum()
        scores.append(score)
    return QUARTERS[np.argmin(scores)]


imgs_path = list((DATA_PATH / "input").glob("*.jpg"))
img = cv2.imread(str(np.random.choice(imgs_path, 1)[0]))

plt.show()
