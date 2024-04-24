import hashlib

import cv2

from board_builder import get_square, resample
from configs import CHUNK_SIZE, DATA_PATH


def main():
    """
    Generate all chunks for all input images and save them to disk
    """
    imgs_path = list((DATA_PATH / "input").glob("*.jpg"))
    for i, img_path in enumerate(imgs_path):
        img = cv2.imread(str(img_path))
        projected = get_square(img)
        chunks = resample(projected, CHUNK_SIZE)
        for chunk in chunks:
            hash = hashlib.md5(chunk.tobytes()).hexdigest()
            cv2.imwrite(str(DATA_PATH / "chunks" / f"{hash}.jpg"), chunk)
