from configs import DATA_PATH
from board_builder import get_quarters, get_robots, build_board
from chunk_classifier import predict_chunks
from robot_classifier import predict_robots
from chunker import get_chunks, get_square
from bash_render  import print_board
import numpy as np
from solver import full_solve
from bash_render import print_path
from img_render import render_board, render_path
from matplotlib import pyplot as plt
import requests

import cv2

DATA = {
    "20240415_102619.jpg": {
        "quarters": [0, 6, 5, 3],
        "robots": {"red": [3, 7], "green": [4, 12], "yellow": [6, 4], "blue": [12, 2]},
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
    }
}


def test_quarters():
    for img_path, data in DATA.items():
        if "quarters" not in data:
            continue
        img = cv2.imread(str(DATA_PATH / "input" / img_path))
        projected = get_square(img)
        chunks = get_chunks(projected)
        proba = predict_chunks(chunks).reshape((16, 16, 4))
        quarters = get_quarters(proba)
        assert quarters == data["quarters"]


def test_robots():
    for img_path, data in DATA.items():
        if "robots" not in data:
            continue
        img = cv2.imread(str(DATA_PATH / "input" / img_path))
        chunks, projected = get_chunks(img, return_projected=True)
        proba = predict_chunks(chunks).reshape((16, 16, 4))
        robots = get_robots(chunks.reshape((16, 16, 64, 64, 3)), proba[:, :, 3])
        for color in data["robots"]:
            assert robots[color] == data["robots"][color]


def test_api():
    img_path = str(DATA_PATH / "input/20240415_102658.jpg")
    url = 'http://127.0.0.1:5000/im_size'
    img = {'image': open(img_path, 'rb')}
    r = requests.post(url, files=img)

    assert r.json() == {'msg': 'success', 'size': [1807, 1807]}, r.json()


def test_api_solve():
    img_path = str(DATA_PATH / "input/20240415_102658.jpg")
    url = 'http://127.0.0.1:5000/solve'
    img = {'image': open(img_path, 'rb')}
    r = requests.post(url, files=img, stream=True)

    with open("output.gif", "wb") as f:
        f.write(r.content)

    assert r.json() == {'msg': 'success', 'size': [1807, 1807]}, r.json()


if __name__ == "__main__":
    img_paths = list((DATA_PATH / "input").glob("*.jpg"))
    img_path = str(np.random.choice(img_paths))
    print(img_path)
    img = cv2.imread(img_path)
    board = build_board(img)
    
    print_board(board["robots"], board["walls"])
    img = render_board(board["robots"], board["walls"], (1, 3))

    state = {"robots": board["robots"], "cost": 0, "prev_state": None}
    winning_state = full_solve(board["walls"], state, "green", (1, 3))
    print_path(board["walls"], winning_state, "green", (1, 3))
    gif = render_path(board["walls"], winning_state, "green", (1, 3))
    with open("output.gif", "wb") as f:
        f.write(gif.getbuffer())
