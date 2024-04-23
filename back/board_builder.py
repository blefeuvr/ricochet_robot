import numpy as np
import matplotlib.pyplot as plt
from chunker import get_chunks, resample, get_square
from configs import QUARTERS, DATA_PATH
from chunk_classifier import predict_chunks
from robot_classifier import predict_robots
from sklearn.cluster import DBSCAN, KMeans
from bash_render import print_board
from matplotlib import pyplot as plt


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


def get_quarter(quarter):
    threshold = 0.5
    prediction = np.logical_or(
        quarter[:, :, 2] > threshold, quarter[:, :, 3] > threshold
    ).astype(bool)
    scores = []
    for model in QUARTERS:
        solution = np.zeros((8, 8), dtype=bool)
        x, y = zip(*model["goals"].values())
        solution[x, y] = True
        score = (np.logical_and(solution, ~prediction)).sum()
        scores.append(score)
    return np.argmin(scores)


def get_quarters(proba):
    quarters = resample(proba, 8)
    qlabels = []
    rot = [0, 1, 3, 2]
    for i, quarter in enumerate(quarters):
        qlabels.append(get_quarter(np.rot90(quarter, rot[i])))
    return qlabels


def get_board_bg(proba):
    rot = [0, 1, 3, 2]
    qlabels = get_quarters(proba)
    board = {"walls": np.empty((0, 2)), "goals": {}}
    for i, qlabel in enumerate(qlabels):
        quarter = QUARTERS[qlabel]
        board["walls"] = np.concatenate(
            [board["walls"], (rotate_around_point(quarter["walls"], rot[i] * 90))]
        )
        for name, xy in quarter["goals"].items():
            board["goals"][name] = rotate_around_point(xy, rot[i] * 90)
    board["walls"] = board["walls"].tolist()
    for name, xy in board["goals"].items():
        board["goals"][name] = xy.tolist()
    return board


def get_robots(chunks, proba):
    labels = ["yellow", "red", "green", "blue"]
    threshold = 0.2
    coords = np.argwhere(proba >= threshold)
    robot_proba = predict_robots(chunks[coords[:, 0], coords[:, 1]])
    order = np.argsort(proba[proba >= threshold])[::-1]
    robots = {}
    for i, idx in enumerate(order):
        robot = labels[np.argmax(robot_proba[idx])]
        if robot not in robots:
            robots[robot] = coords[idx].tolist()
    return robots


def build_board(img):
    projected = get_square(img)
    chunks = get_chunks(projected)
    proba = predict_chunks(chunks).reshape((16, 16, 4))
    board = get_board_bg(proba)
    robots = get_robots(chunks.reshape((16, 16, 64, 64, 3)), proba[:, :, 3])
    board["robots"] = robots
    return board
