import cv2
import numpy as np


# Function to extract frames from a video file
def dynamic_key_frames_extraction(video_path, update_status=None, threshold=0.15):
    cap = cv2.VideoCapture(video_path)
    frames = []
    ret, last_frame = cap.read()
    if ret:
        frames.append(last_frame)
        last_gray = cv2.cvtColor(last_frame, cv2.COLOR_BGR2GRAY)
        if update_status:
            update_status("Extracting key frames...")

    last_frame_extracted = None  # 用于存储最后一帧

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        delta = cv2.absdiff(current_gray, last_gray)
        frame_score = np.mean(delta)
        relative_change = frame_score / np.mean(current_gray)

        if relative_change > threshold:
            frames.append(frame)
            last_gray = current_gray

        last_frame_extracted = frame  # 更新最后一帧

    # 在循环结束后添加最后一帧
    if last_frame_extracted is not None and (len(frames) == 0 or not np.array_equal(frames[-1], last_frame_extracted)):
        frames.append(last_frame_extracted)

    cap.release()
    cv2.destroyAllWindows()
    return frames


# Function to stitch frames into a panorama
def stitch_frames(frames, update_status):
    try:
        # 更新状态为拼接中
        update_status("Stitching images...")
        # Create a stitcher object
        stitcher = cv2.Stitcher.create()
        status, stitched_image = stitcher.stitch(frames)
        if status == cv2.Stitcher_OK:
            return stitched_image
        else:
            print("Stitching failed.")
            return None
    except Exception as e:
        update_status("Failed with error: " + str(e))


def drop_black_edges(image_array):
    # panoramic contour extraction
    border_color = (0, 0, 0)
    stitched = cv2.copyMakeBorder(image_array,
                                  10, 10, 10, 10,
                                  cv2.BORDER_CONSTANT, value=border_color)
    gray = cv2.cvtColor(stitched, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)[1]
    # finding the minimum positive rectangle of the contour
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    mask = np.zeros(thresh.shape, dtype="uint8")
    (x, y, w, h) = cv2.boundingRect(cnts[0])
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
    # corrosion treatment
    minRect = mask.copy()
    sub = mask.copy()
    while cv2.countNonZero(sub) > 0:
        minRect = cv2.erode(minRect, None)
        sub = cv2.subtract(minRect, thresh)
    # clipping
    x, y, w, h = cv2.boundingRect(minRect)
    cropped_result = stitched[y:y + h, x:x + w]
    return cropped_result
