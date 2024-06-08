import cv2
import numpy as np
import roboflow

# init roboflow
rf = roboflow.Roboflow(api_key="UkD8Rd4mKQYHAAXBJ6f2")
project = rf.workspace().project("geese-sheet")
model = project.version("8").model

screen_width = 3024
screen_height = 1964

# video capture object
cap = cv2.VideoCapture(1)  # Use 0 for the default camera (usually the first connected camera)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

while True:
    ret, frame = cap.read()

    # Predict on the captured frame using Roboflow
    prediction = model.predict(frame)
    print(prediction)

    # # Check if any objects are detected
    # if prediction.objects:
    #     # Object detected
    #     print("Object detected!")
    #     result = 1
    # else:
    #     # No object detected
    #     result = 0

    # Display the captured frame
    cv2.imshow('Camera Feed', frame)

    # Check for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close windows
cap.release()
cv2.destroyAllWindows()
