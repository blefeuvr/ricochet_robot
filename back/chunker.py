import numpy as np
import cv2
from matplotlib import pyplot as plt
import math
from pathlib import Path
from sklearn.cluster import KMeans, AffinityPropagation, Birch, DBSCAN, HDBSCAN
import string
import hashlib
from configs import *


def random_string(y):
    """
    Generate a random string of given length
    """
    return "".join(np.random.choice(list(string.ascii_letters), y, replace=True))


def image_resize(img, height=1000):
    """Resize image to same normalized area (height**2)"""
    pixels = height * height
    shape = list(np.shape(img))
    scale = math.sqrt(float(pixels) / float(shape[0] * shape[1]))
    shape[0] *= scale
    shape[1] *= scale
    img = cv2.resize(img, (int(shape[1]), int(shape[0])))
    img_shape = np.shape(img)
    return img, img_shape, scale


def get_intersect(a1, a2, b1, b2):
    """
    Return the point of intersection of the lines passing through a2,a1 and b2,b1
    """
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return (float("inf"), float("inf"))
    return (x / z, y / z)


def get_lines(img):
    """
    Get lines from image using Canny and Hough transform
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
    lines = np.reshape(lines, (-1, 4))

    return lines


def classify_lines(lines):
    """
    Classify lines to horizontal and vertical, filter outliers
    The median angle for each direction is calculated and only lines within a threshold angle are kept
    """
    threshold = 360 / 32
    thetas = (
        np.rad2deg(np.arctan2(lines[:, 1] - lines[:, 3], lines[:, 0] - lines[:, 2]))
        + 225
    ) % 180
    mask = thetas < 90

    h_median = np.median(thetas[mask])
    h_mask = np.logical_and(
        mask,
        np.logical_or(
            np.abs(thetas - h_median) < threshold,
            np.abs((thetas + 360 / 2) % 360 - h_median) < threshold,
        ),
    )

    v_median = np.median(thetas[~mask])
    v_mask = np.logical_and(
        ~mask,
        np.logical_or(
            np.abs(thetas - v_median) < threshold,
            np.abs((thetas + 360 / 2) % 360 - v_median) < threshold,
        ),
    )
    h_lines = lines[h_mask]
    v_lines = lines[v_mask]
    return h_lines, v_lines


def get_corners(img, h_lines, v_lines):
    """
    Get corners of the image using the intersection of the min and max horizontal and vertical lines
    """
    sorted_v_lines = sorted(v_lines, key=lambda x: x[0] + x[2])
    sorted_h_lines = sorted(h_lines, key=lambda x: x[1] + x[3])

    x1, y1, x2, y2 = sorted_h_lines[0]
    htop = sorted_h_lines[0]
    x1, y1, x2, y2 = sorted_h_lines[-1]
    hbot = sorted_h_lines[-1]
    x1, y1, x2, y2 = sorted_v_lines[0]
    vleft = sorted_v_lines[0]
    x1, y1, x2, y2 = sorted_v_lines[-1]
    vright = sorted_v_lines[-1]

    corners = np.array(
        [
            get_intersect(htop[:2], htop[2:], vleft[:2], vleft[2:]),
            get_intersect(htop[:2], htop[2:], vright[:2], vright[2:]),
            get_intersect(hbot[:2], hbot[2:], vleft[:2], vleft[2:]),
            get_intersect(hbot[:2], hbot[2:], vright[:2], vright[2:]),
        ]
    )
    return corners


def reproject_image(img, corners):
    """
    Reproject image to a square using the corners coords
    """
    h, mask = cv2.findHomography(
        corners, np.array([[0, 0], [1024, 0], [0, 1024], [1024, 1024]]), cv2.RANSAC, 5.0
    )
    reprojected = cv2.warpPerspective(img.copy(), h, (1024, 1024))
    return reprojected


def resample(arr, N):
    """
    Resample image to NxN chunks
    """
    A = []
    for v in np.vsplit(arr, arr.shape[0] // N):
        A.extend([*np.hsplit(v, arr.shape[0] // N)])
    return np.array(A)


def get_chunks(img, return_projected=False):
    """
    Split reprojection into 64 chunks
    """
    img, img_shape, scale = image_resize(img, height=1000)
    # plt.imshow(img)
    lines = get_lines(img)
    h_lines, v_lines = classify_lines(lines)
    # for x1, y1, x2, y2 in lines:
    #     plt.plot([x1, x2], [y1, y2], "-", color="red")
    # for x1, y1, x2, y2 in lines:
    #     plt.plot([x1, x2], [y1, y2], "-", color="blue")
    corners = get_corners(img, h_lines, v_lines)
    # plt.plot(corners[:, 0], corners[:, 1], "o", markersize=5, color="orange")
    reprojected = reproject_image(img, corners)
    # plt.imshow(reprojected[:, :, ::-1])
    chunks = resample(reprojected, 64)
    if return_projected:
        return chunks, reprojected
    return chunks


def clusterize_points(grey_img, h_lines, v_lines):
    """
    UNUSED: Clusterize intersection points to find the 64 chunks
    """
    points = []
    for h_line in h_lines:
        for v_line in v_lines:
            inter_point = get_intersect(h_line[:2], h_line[2:], v_line[:2], v_line[2:])
            points.append(inter_point)

    # Get all intersections
    img_lines = np.full_like(grey_img, 0)
    for x1, y1, x2, y2 in h_lines:
        cv2.line(img_lines, (x1, y1), (x2, y2), (255), 2)
    img_h_lines = np.full((*grey_img.shape, 4), 0)
    img_h_lines[:, :, 0] = 255
    img_h_lines[:, :, 3] = img_lines

    img_lines = np.full_like(grey_img, 0)
    for x1, y1, x2, y2 in v_lines:
        cv2.line(img_lines, (x1, y1), (x2, y2), (255), 2)
    img_v_lines = np.full((*grey_img.shape, 4), 0)
    img_v_lines[:, :, 1] = 255
    img_v_lines[:, :, 3] = img_lines

    points = []
    for h_line in h_lines:
        for v_line in v_lines:
            inter_point = get_intersect(h_line[:2], h_line[2:], v_line[:2], v_line[2:])
            points.append(inter_point)
    points = np.array(points)

    clustering = DBSCAN(eps=10, min_samples=2).fit(points)
    labels = clustering.labels_

    clusters_center = []
    for k in set(labels):
        xy = points[labels == k]
        clusters_center.append(xy.mean(axis=0))
        # plt.plot(xy[:, 0], xy[:, 1], "o", markersize=3)
        # plt.plot(xy[:, 0].mean(), xy[:, 1].mean(), "x", markersize=5, color="orange")
    clusters_center = np.array(clusters_center)


def main():
    """
    Generate all chunks for all input images and save them to disk
    """
    imgs_path = list((DATA_PATH / "input").glob("*.jpg"))
    for i, img_path in enumerate(imgs_path):
        img = cv2.imread(str(img_path))
        chunks = get_chunks(img)
        for chunk in chunks:
            hash = hashlib.md5(chunk.tobytes()).hexdigest()
            cv2.imwrite(str(DATA_PATH / "chunks" / f"{hash}.jpg"), chunk)
