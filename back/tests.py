import cv2
import numpy as np
import requests

from bash_render import print_board, print_path
from board_builder import build_board, get_quarters, get_robots, get_square, resample, clean_solution
from chunk_classifier import predict_chunks
from configs import DATA_PATH, CHUNK_SIZE
from img_render import render_board, render_path
from solver import full_solve

DATA = {
    "20240415_102619.jpg": {
        "quarters": [0, 6, 5, 3],
        "robots": {"red": [3, 7], "green": [4, 12], "yellow": [6, 4], "blue": [12, 2]},
        "solutions": [("yellow", (8, 5), [('yellow', (8, 5), (6, 5)), ('yellow', (6, 5), [6, 4])])],
    },
    "20240415_102648.jpg": {
        "quarters": [3, 5, 6, 0],
        "robots": {"red": [14, 7], "green": [8, 2], "yellow": [8, 3], "blue": [8, 4]},
    },
    "20240415_165852.jpg": {
        "quarters": [2, 4, 0, 6],
        "robots": {"red": [5, 10], "green": [4, 10], "yellow": [5, 9], "blue": [4, 9]},
    },
    "20240415_165840.jpg": {
        "quarters": [0, 2, 6, 4],
        "robots": {"yellow": [3, 11], "green": [1, 9], "blue": [2, 5], "red": [10, 10]},
    },
}


def test_quarters():
    for img_path, data in DATA.items():
        if "quarters" not in data:
            continue
        img = cv2.imread(str(DATA_PATH / "input" / img_path))
        projected = get_square(img)
        chunks = resample(projected, CHUNK_SIZE)
        proba = predict_chunks(chunks).reshape((16, 16, 4))
        quarters = get_quarters(proba)
        assert quarters == data["quarters"]


def test_robots():
    for img_path, data in DATA.items():
        if "robots" not in data:
            continue
        img = cv2.imread(str(DATA_PATH / "input" / img_path))
        projected = get_square(img)
        chunks = resample(projected, CHUNK_SIZE)
        proba = predict_chunks(chunks).reshape((16, 16, 4))
        robots = get_robots(chunks.reshape((16, 16, 64, 64, 3)), proba[:, :, 3])
        for color in data["robots"]:
            assert robots[color] == data["robots"][color]


def test_clean_solution():
    for img_path, data in DATA.items():
        if "solutions" not in data:
            continue
        img = cv2.imread(str(DATA_PATH / "input" / img_path))
        board = build_board(img)
        for robot, goal, solution in data["solutions"]:
            state = {"robots": board["robots"], "cost": 0, "prev_state": None}
            winning_state = full_solve(board["walls"], state, robot, goal)
            board, moves = clean_solution(board, winning_state)
            assert moves == solution
