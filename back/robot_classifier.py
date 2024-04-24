import pickle

import albumentations as A
import cv2
import matplotlib.pyplot as plt
import numpy as np
from sklearn import svm
from sklearn.metrics import (
    accuracy_score,
)
from sklearn.model_selection import train_test_split

from configs import DATA_PATH


def learn():
    """
    Train a model to predict the labels of the robots
    Save the model
    """
    labels = ["yellow", "red", "green", "blue"]
    labels_path = [(DATA_PATH / "sorted_robots" / label) for label in labels]

    X = []
    y = []

    transform = A.Compose(
        [
            A.ColorJitter(p=0.5, hue=(0, 0.05)),
            A.RandomGamma(p=0.5),
            A.Blur(p=0.5),
            A.RandomRotate90(p=0.5),
        ]
    )

    for i, label_path in enumerate(labels_path):
        for chunk in label_path.glob("*"):
            img = transform(image=cv2.imread(str(chunk)))["image"]
            X.append(img.flatten())
            y.append(i)

    X = np.array(X)
    y = np.array(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=0, stratify=y
    )
    model = svm.SVC(probability=True)
    # model = GridSearchCV(svc, param_grid)
    model.fit(X_train, y_train)

    pickle.dump(model, open("models/robot_model.pkl", "wb"))

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_pred, y_test)
    print(acc)

    # print(classification_report(y_test, y_pred, target_names=labels))
    # cm = confusion_matrix(y_test, y_pred, labels=range(len(labels)))
    # disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    # disp.plot()
    # plt.show()


def predict_robots(chunks):
    """
    Predict the labels of the chunks
    """
    X = np.array([chunk.flatten() for chunk in chunks])

    model = pickle.load(open("models/robot_model.pkl", "rb"))

    y_pred = model.predict_proba(X)
    return y_pred


def show_predictions(y_pred):
    plt.subplot(221)
    plt.imshow(y_pred[:, :, 0])
    plt.subplot(222)
    plt.imshow(y_pred[:, :, 1])
    plt.subplot(223)
    plt.imshow(y_pred[:, :, 2])
    plt.subplot(224)
    plt.imshow(y_pred[:, :, 3])


if __name__ == "__main__":
    learn()
