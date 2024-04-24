import math

import cv2
import numpy as np

from chunk_classifier import predict_chunks
from configs import CHUNK_SIZE, IMG_SIZE, QUARTERS
from robot_classifier import predict_robots


class BoardBuilderException(Exception):
    pass


class NotEnoughLinesException(BoardBuilderException):
    pass


def image_resize(img, height=1024):
    """
    Resize image to same normalized area (height**2)
    """
    pixels = height * height
    shape = list(np.shape(img))
    scale = math.sqrt(float(pixels) / float(shape[0] * shape[1]))
    shape[0] *= scale
    shape[1] *= scale
    img = cv2.resize(img, (int(shape[1]), int(shape[0])))
    return img


def get_intersect(a1, a2, b1, b2):
    """
    Return the point of intersection of the lines passing through a2,a1 and b2,b1
    """
    s = np.vstack([a1, a2, b1, b2])
    h = np.hstack((s, np.ones((4, 1))))
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return (float("inf"), float("inf"))
    return (x / z, y / z)


def get_lines(img):
    """
    Get all lines from image using Canny and Hough transform
    """
    # Preprocess
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grey_img = cv2.blur(grey_img, (3, 3))

    # Canny
    sigma = 0.75
    v = np.median(grey_img)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edges = cv2.Canny(grey_img, lower, upper)

    # Hough
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, 100, minLineLength=200, maxLineGap=50
    )
    if lines is None:
        return np.array([])

    return np.reshape(lines, (-1, 4))


def classify_lines(lines):
    """
    Classify lines between horizontal and vertical, remove diagonals that are a threshold away from 0 and 90 degrees
    """
    threshold = 360 / 16
    # Compute tilted thetas (angles of lines) so that
    # h lines are around 45 degrees and v lines around 135 degrees
    thetas = (
        np.rad2deg(np.arctan2(lines[:, 1] - lines[:, 3], lines[:, 0] - lines[:, 2]))
        + 45
        + 180
    ) % 180
    # Horizontal lines
    h_median = 45
    h_mask = np.abs(thetas - h_median) < threshold
    h_lines = lines[h_mask]
    # Vertical lines
    v_median = 135
    v_mask = np.abs(thetas - v_median) < threshold
    v_lines = lines[v_mask]
    return h_lines, v_lines


def get_corners(img, h_lines, v_lines):
    """
    Get 4 corners of the board in the image
    using the intersection of the min and max horizontal and vertical lines
    """
    sorted_v_lines = sorted(v_lines, key=lambda x: x[0] + x[2])
    sorted_h_lines = sorted(h_lines, key=lambda x: x[1] + x[3])

    h_top = sorted_h_lines[0]
    h_bot = sorted_h_lines[-1]
    v_left = sorted_v_lines[0]
    v_right = sorted_v_lines[-1]

    corners = np.array(
        [
            get_intersect(h_top[:2], h_top[2:], v_left[:2], v_left[2:]),
            get_intersect(h_top[:2], h_top[2:], v_right[:2], v_right[2:]),
            get_intersect(h_bot[:2], h_bot[2:], v_left[:2], v_left[2:]),
            get_intersect(h_bot[:2], h_bot[2:], v_right[:2], v_right[2:]),
        ]
    )
    return corners


def warp_image(img, corners):
    """
    Reproject image to a square using corners coords
    """
    h, _ = cv2.findHomography(
        corners,
        np.array([[0, 0], [IMG_SIZE, 0], [0, IMG_SIZE], [IMG_SIZE, IMG_SIZE]]),
        cv2.RANSAC,
        5.0,
    )
    projected = cv2.warpPerspective(img.copy(), h, (IMG_SIZE, IMG_SIZE))
    return projected


def resample(mat, N):
    """
    Resample mat to NxN chunks
    """
    A = []
    for v in np.vsplit(mat, mat.shape[0] // N):
        A.extend([*np.hsplit(v, mat.shape[0] // N)])
    return np.array(A)


def get_square(img):
    """
    Return board image cropped and projected to a IMG_SIZExIMG_SIZE img
    """
    img = image_resize(img, height=IMG_SIZE)
    lines = get_lines(img)
    if len(lines) == 0:
        raise NotEnoughLinesException("No lines found")
    h_lines, v_lines = classify_lines(lines)
    corners = get_corners(img, h_lines, v_lines)
    projected = warp_image(img, corners)
    # Remove 12 pixels of border
    border = 12
    cropped = projected[border:-border, border:-border, :]
    cropped = image_resize(cropped, height=IMG_SIZE)
    return cropped


def rotate_around_point(xy, degrees, origin=(7.5, 7.5)):
    """
    Rotate a point coords around a given point
    """
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
    """
    Detect the quarter of the board from the prediction
    """
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
    """
    Detect four quarters of the board from the prediction
    """
    quarters = resample(proba, 8)
    qlabels = []
    rot = [0, 1, 3, 2]
    for i, quarter in enumerate(quarters):
        qlabels.append(get_quarter(np.rot90(quarter, rot[i])))
    return qlabels


def get_board_bg(proba):
    """
    Get the board background (ie walls+goals) from the prediction
    """
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
    """
    Get the robots positions from the prediction
    """
    labels = ["yellow", "red", "green", "blue"]
    threshold = 0.0
    coords = np.argwhere(proba >= threshold)
    robot_proba = predict_robots(chunks[coords[:, 0], coords[:, 1]])
    order = np.argsort(proba[proba >= threshold])[::-1]
    robots = {}
    for idx in order:
        if len(robots) == 4:
            break
        robot = labels[np.argmax(robot_proba[idx])]
        if robot not in robots:
            robots[robot] = coords[idx].tolist()
    return robots


def build_board(img):
    projected = get_square(img)
    chunks = resample(projected, CHUNK_SIZE)
    proba = predict_chunks(chunks).reshape((16, 16, 4))
    board = get_board_bg(proba)
    robots = get_robots(chunks.reshape((16, 16, 64, 64, 3)), proba[:, :, 3])
    board["robots"] = robots
    return board


def clean_solution(board, winning_state):
    new_board = board.copy()
    new_board["robots"] = winning_state["robots"]
    moves = []
    while True:
        if not winning_state["prev_state"]:
            break
        moving_robot = [
            robot
            for robot in winning_state["robots"]
            if winning_state["robots"][robot]
            != winning_state["prev_state"]["robots"][robot]
        ][0]
        moves.append((
            moving_robot,
            winning_state["robots"][moving_robot],
            winning_state["prev_state"]["robots"][moving_robot],
        ))
        winning_state = winning_state["prev_state"]
    return new_board, moves
