import requests
from PIL import Image,  ImageSequence
from io import BytesIO
import tempfile
from nudenet import NudeDetector
import os
import cv2


async def process_video_from_url(url, lookfor):
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError("Could not download video.")

    # Save the video content to a temporary file (OpenCV can't read from memory directly)
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
        temp_video.write(response.content)
        video_path = temp_video.name

    cap = cv2.VideoCapture(video_path)
    detector = NudeDetector()

    results = []
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1

        # Save current frame temporarily for classification
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_frame:
            cv2.imwrite(temp_frame.name, frame)
            temp_frame_path = temp_frame.name

        result = detector.detect(temp_frame_path)
        os.remove(temp_frame_path)

        results.append((frame_number, result))

        for item in result:
            if item['class'] in lookfor:
                cap.release()
                os.remove(video_path)
                return result  # Return early if matched

    cap.release()
    os.remove(video_path)
    return False  # No match found

async def detect_from_url(url, lookfor=None):
    if lookfor is None:
        lookfor = [
    "FEMALE_GENITALIA_COVERED",
    "FACE_FEMALE",
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "BELLY_COVERED",
    "FEET_COVERED",
    "ARMPITS_COVERED",
    "ARMPITS_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
    "FEMALE_BREAST_COVERED",
    "BUTTOCKS_COVERED",
]
# Step 1: Load image from URL
    response = requests.get(url)
    if response.ok:
        img = Image.open(BytesIO(response.content))

        # Step 2: Initialize classifier
        classifier = NudeDetector()
        results = []

        # Step 3: Handle static vs animated
        if getattr(img, "is_animated", False):
            frames = ImageSequence.Iterator(img)
        else:
            frames = [img]

        # Step 4: Iterate through frames
        for i, frame in enumerate(frames):
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                frame.convert("RGB").save(temp_file.name)
                temp_path = temp_file.name

            # Classify the frame
            result = classifier.detect(temp_path)
            results.append((i, result))

            # Cleanup
            os.remove(temp_path)

            # Check for matches
            for item in result:
                if item['class'] in lookfor:
                    return result  # early return if match found
    return False  # no match found
