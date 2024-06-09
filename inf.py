from inference import InferencePipeline
from functools import partial

# Import the built in render_boxes sink for visualizing results
from inference.core.interfaces.camera.entities import VideoFrame
from inference.core.interfaces.stream.sinks import render_boxes
from inference.core.interfaces.stream.sinks import multi_sink

import requests
from threading import Thread

import time

prev_alert = time.time()


def alert():
    requests.post(
        "http://192.168.137.201:5000/gpio/2/flash",
        json={"interval": 0.1, "duration": 1},
    )


def alert_sink(predictions: dict, video_frame: VideoFrame):
    global prev_alert
    if len(predictions["predictions"]) > 0 and time.time() - prev_alert > 5:
        alert_thread = Thread(target=alert)
        prev_alert = time.time()
        alert_thread.start()
    # print the frame ID of the video_frame object
    # requests.post(
    #     "http://192.168.137.201:5000/gpio/2/flash",
    #     json={"interval": 0.1, "duration": 1},
    # )


# initialize a pipeline object
pipeline = InferencePipeline.init(
    model_id="geese-sheet/8",  # Roboflow model to use
    video_reference=0,  # Path to video, device id (int, usually 0 for built in webcams), or RTSP stream url
    on_prediction=partial(
        multi_sink, sinks=[alert_sink, render_boxes]
    ),  # Function to run after each prediction
    api_key="WtZSDazVEO6NgHstKRYE",  # Roboflow API key
    max_fps=30,
    confidence=0.4,
)
pipeline.start()
pipeline.join()
