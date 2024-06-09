from inference import InferencePipeline
from functools import partial

# Import the built in render_boxes sink for visualizing results
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import render_boxes
from inference.core.interfaces.stream.sinks import multi_sink

import requests
from threading import Thread

import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("logs.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

import time

prev_alert = time.time()
prev_detection = []

RPI_BASE_URL = "http://192.168.137.201:5000"
MIN_TIME_BETWEEN_ALERTS = 3
MIN_FRAMES_TO_ALERT = 3
DETECTION_CONFIDENCE = 0.4
VIDEO_DEVICE_INDEX = 3


def alert_buzzer():
    requests.post(
        f"{RPI_BASE_URL}/gpio/3/flash",
        json={"interval": 0.1, "duration": 1},
    )


def alert_led():
    requests.post(
        f"{RPI_BASE_URL}/gpio/2/flash",
        json={"interval": 0.1, "duration": 1},
    )


def alert_sink(predictions: dict, video_frame: VideoFrame):
    global prev_alert, prev_detection
    logger.debug(prev_detection)
    if len(predictions["predictions"]) > 0:
        if not (
            video_frame.frame_id - 1 in prev_detection
            or video_frame.frame_id - 2 in prev_detection
        ):
            prev_detection = []
        prev_detection.append(video_frame.frame_id)
        if (
            time.time() - prev_alert > MIN_TIME_BETWEEN_ALERTS
            and len(prev_detection) > MIN_FRAMES_TO_ALERT
        ):
            Thread(target=alert_buzzer).start()
            Thread(target=alert_led).start()
            prev_alert = time.time()


# initialize a pipeline object
pipeline = InferencePipeline.init(
    model_id="geese-sheet/8",  # Roboflow model to use
    video_reference=VIDEO_DEVICE_INDEX,  # Path to video, device id (int, usually 0 for built in webcams), or RTSP stream url
    on_prediction=partial(
        multi_sink,
        sinks=[
            alert_sink,
            lambda p, f: render_boxes(p, f, fps_monitor=None, display_statistics=True),
        ],
    ),  # Function to run after each prediction
    api_key="WtZSDazVEO6NgHstKRYE",  # Roboflow API key
    max_fps=30,
    confidence=DETECTION_CONFIDENCE,
)
pipeline.start()
pipeline.join()
