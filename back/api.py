from flask import Flask, request, jsonify
from PIL import Image
from board_builder import build_board
from solver import full_solve
import numpy as np
from img_render import render_path
from bash_render import print_board
from flask import send_file
import cv2
from configs import DATA_PATH
import string

app = Flask(__name__)

def random_string(y):
    """
    Generate a random string of given length
    """
    return "".join(np.random.choice(list(string.ascii_letters), y, replace=True))

@app.route("/im_size", methods=["POST"])
def process_image():
    file = request.files['image']
    img = Image.open(file.stream)

    return jsonify({'msg': 'success', 'size': [img.width, img.height]})


@app.route("/read", methods=["POST"])
def read_board():
    file = request.files['file']
    img = np.array(Image.open(file.stream))[:, :, ::-1]

    cv2.imwrite(f"./pictures/{random_string(6)}.png", img)

    # imgs_path = list((DATA_PATH / "input").glob("*.jpg"))
    # img_path = str(np.random.choice(imgs_path, 1)[0])
    # img = cv2.imread(img_path)
    # print(img_path)

    board = build_board(img)
    return jsonify({'msg': 'success', 'board': board})


@app.route("/solve", methods=["POST"])
def solve():
    data = request.get_json()
    board = data["board"]
    goal = tuple(data["goal"])
    robot = data["robot"]
    state = {"robots": board["robots"], "cost": 0, "prev_state": None}
    winning_state = full_solve(board["walls"], state, robot, goal)
    
    gif = render_path(board["walls"], winning_state, robot, goal)

    solution_id = "solution"
    with open(f"./solutions/{solution_id}.gif", "wb") as f:
        f.write(gif.getbuffer())

    return jsonify({'msg': 'success', 'solution_id': solution_id})


@app.route("/solution/<solution_id>", methods=["GET"])
def get_solution(solution_id):
    if not solution_id.isalpha():
        return jsonify({'msg': 'error', 'error': 'Invalid solution id'})
    return send_file(f"./solutions/{solution_id}.gif", mimetype='image/gif')


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
