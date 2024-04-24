import io

import cv2 as cv
import imageio.v3 as iio
import numpy as np
from matplotlib import colors

from configs import BOARD_SIZE

CHUNK_SIZE = 32


def render_path(walls, state, robot_name, goal=None):
    """Display all the states along the path we took"""
    count = 0
    images = []
    while state is not None:
        images = [render_board(state["robots"], walls, goal)] + images
        state = state["prev_state"]
        count += 1
    gif = io.BytesIO()
    iio.imwrite(gif, images, extension=".gif", duration=600)
    gif.seek(0)
    return gif


def render_robot(color):
    """Print a robot"""
    chunk = np.full((CHUNK_SIZE, CHUNK_SIZE, 3), 255, np.uint8)
    cv_color = np.array(colors.to_rgb(color)) * 255
    cv.circle(chunk, (CHUNK_SIZE // 2, CHUNK_SIZE // 2), CHUNK_SIZE // 3, cv_color, -1)
    return chunk


def render_goal(color):
    """Print a goal"""
    chunk = np.full((CHUNK_SIZE, CHUNK_SIZE, 3), 255, np.uint8)
    chunk[:, :, :] = np.array(colors.to_rgb(color)) * 255
    return chunk


def render_grid(board):
    """Render empty board, to add stuff to later"""
    h = w = CHUNK_SIZE * 16
    for x in np.linspace(start=CHUNK_SIZE, stop=w - CHUNK_SIZE, num=BOARD_SIZE - 1):
        x = int(round(x))
        cv.line(board, (x, 0), (x, h), color=(0, 0, 0), thickness=1)
    for y in np.linspace(start=CHUNK_SIZE, stop=h - CHUNK_SIZE, num=BOARD_SIZE - 1):
        y = int(round(y))
        cv.line(board, (0, y), (w, y), color=(0, 0, 0), thickness=1)
    cv.line(board, (0, 0), (0, h), color=(0, 0, 0), thickness=3)
    cv.line(board, (0, 0), (h, 0), color=(0, 0, 0), thickness=3)
    cv.line(board, (0, h), (h, h), color=(0, 0, 0), thickness=3)
    cv.line(board, (h, 0), (h, h), color=(0, 0, 0), thickness=3)
    return board


def render_wall(board, x, y):
    """Draws a wall at x, y on the board"""
    x1 = int(CHUNK_SIZE * np.ceil(y))
    y1 = int(CHUNK_SIZE * np.ceil(x))
    x2 = int(CHUNK_SIZE * (np.floor(y) + 1))
    y2 = int(CHUNK_SIZE * (np.floor(x) + 1))
    cv.line(board, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=3)


def render_board(robots, walls, goal=None):
    """Draw the board
    robots: dictionary of name: (x,y)
    walls: list of (x,y) tuples
    goal: optional (x,y)"""
    h = w = CHUNK_SIZE * 16
    board = np.full((h, w, 3), 255, np.uint8)

    # add goal
    if goal is not None:
        x, y = goal
        board[
            CHUNK_SIZE * x : CHUNK_SIZE * (x + 1), CHUNK_SIZE * y : CHUNK_SIZE * (y + 1)
        ] = render_goal("grey")

    # add robots
    for name, (x, y) in robots.items():
        board[
            CHUNK_SIZE * x : CHUNK_SIZE * (x + 1), CHUNK_SIZE * y : CHUNK_SIZE * (y + 1)
        ] = render_robot(name)

    render_grid(board)

    # add walls
    for x, y in walls:
        render_wall(board, x, y)

    return board
