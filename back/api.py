from flask import Flask, request, jsonify
from PIL import Image
from board_builder import build_board
from solver import full_solve
import numpy as np
from img_render import render_path
from flask import send_file

app = Flask(__name__)


@app.route("/im_size", methods=["POST"])
def process_image():
    file = request.files['image']
    img = Image.open(file.stream)

    return jsonify({'msg': 'success', 'size': [img.width, img.height]})


@app.route("/solve", methods=["POST"])
def solve():
    file = request.files['image']
    img = np.array(Image.open(file.stream))

    board = build_board(img)

    state = {"robots": board["robots"], "cost": 0, "prev_state": None}
    winning_state = full_solve(board["walls"], state, "green", (1, 3))
    gif = render_path(board["walls"], winning_state, "green", (1, 3))

    return send_file(gif, mimetype='image/gif')


if __name__ == "__main__":
    app.run(debug=True)
