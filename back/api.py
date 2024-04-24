import string

import cv2
import numpy as np
from flask import Flask, jsonify, request
from PIL import Image

from board_builder import BoardBuilderException, build_board, clean_solution
from solver import full_solve

app = Flask(__name__)


def random_string(y):
    """
    Generate a random string of given length
    """
    return "".join(np.random.choice(list(string.ascii_letters), y, replace=True))


@app.route("/im_size", methods=["POST"])
def process_image():
    file = request.files["image"]
    img = Image.open(file.stream)

    return jsonify({"msg": "success", "size": [img.width, img.height]})


@app.route("/read", methods=["POST"])
def read_board():
    # file = request.files["file"]
    # img = np.array(Image.open(file.stream))[:, :, ::-1]

    # cv2.imwrite(f"./pictures/{random_string(6)}.png", img)

    img = cv2.imread("./data/input/20240415_102619.jpg")

    try:
        board = build_board(img)
    except BoardBuilderException as e:
        return jsonify({"msg": "error", "error": str(e)})
    return jsonify({"msg": "success", "board": board})


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    board = data["board"]
    goal = tuple(data["goal"])
    robot = data["robot"]
    state = {"robots": board["robots"], "cost": 0, "prev_state": None}
    winning_state = full_solve(board["walls"], state, robot, goal)
    board, moves = clean_solution(board, winning_state)
    print(board["robots"])
    return jsonify({"msg": "success", "board": board, "moves": moves})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
