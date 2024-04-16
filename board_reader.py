import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from chunker import get_chunks, resample
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from pathlib import Path
import cv2
import pandas as pd
import pickle
from configs import QUARTERS, DATA_PATH
from quarter_classifier import get_quarter
from chunk_classifier import predict


def rotate_around_point(xy, degrees, origin=(7.5, 7.5)):
    """Rotate a point around a given point."""
    radians = np.radians(degrees)
    x, y = np.array(xy).T
    offset_x, offset_y = origin
    adjusted_x = x - offset_x
    adjusted_y = y - offset_y
    cos_rad = np.cos(radians)
    sin_rad = np.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
    return np.stack([np.round(qx * 2) / 2, np.round(qy * 2) / 2]).T


def get_quarters(img):
    chunks, projected = get_chunks(img, return_projected=True)
    proba = predict(chunks)
    proba = proba.reshape((16, 16, 4))
    quarters = resample(proba, 8)
    qlabels = []
    rot = [0, 1, 3, 2]
    for i, quarter in enumerate(quarters):
        qlabels.append(get_quarter(np.rot90(quarter, rot[i])))
    return qlabels


def build_board(img):
    qlabels = get_quarters(img)
    board = {"walls": np.empty((0, 2)), "goals": {}}
    for i, qlabel in enumerate(qlabels):
        quarter = QUARTERS[qlabel]
        board["walls"] = np.concatenate(
            [board["walls"], (rotate_around_point(quarter["walls"], i * 90))]
        )
        for name, xy in quarter["goals"].items():
            board["goals"][name] = rotate_around_point(xy, i * 90)
    
    return board


