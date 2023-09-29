import cv2
import torch
import numpy as np
import time
import datetime
import os
import requests
from requests.auth import HTTPBasicAuth

url = "http://13.233.149.171/api/v1/record/"  #Server api url
username = "admin"
password = "admin1771"

model = torch.hub.load('ultralytics/yolov5','custom', path='/home/cv/Project/advertising-tracking/new_m.pt')
print("Model Loaded")
model.conf = 0.95  # NMS confidence threshold
model.iou = 0.45  # NMS IoU threshold
model.multi_label = False  # NMS multiple labels per box
model.amp = False  # Automatic Mixed Precision (AMP) inference
model.cuda()  # GPU
video_writer = False
channel_name = "sevimli_tv"
output_folder = 'videos'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')

video_path = 'https://api.itv.uz/hls/iptv/1056/index.m3u8?type=live&&token=artel'  # Change this to your video file's path
cap = cv2.VideoCapture(video_path)
frame_rate = cap.get(cv2.CAP_PROP_FPS)
frame_width = 640
frame_height = 640

frame_size = (frame_width, frame_height)

print("Frame Width:", frame_width)
print("Frame Height:", frame_height)
print("Frame rate:", frame_rate)

frame_delay = 1 / frame_rate  # Calculate the time delay between frames

try:
    detected_time = 0
    det_last_time = 0
    last_time = time.time()
    data_send = True
    while cap.isOpened():
        current_datetime = datetime.datetime.now()
        start_time = time.time()
        ret, color_frame = cap.read()
        color_frame = cv2.resize(color_frame ,(frame_width, frame_height))
        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame)
        results = model(color_image)
        results.render()
        detections = results.pred[0][results.pred[0][:,4] >= 0.95]
        for det in detections: 
            x1, y1, x2, y2, conf, cls = det.tolist()
            class_name = model.names[int(cls)]
            if (x1 >= 0 and x1 < frame_width/6 and y1 >= 0 and y1 < frame_height/6 and x2 >= 0 and x2 < frame_width/4 and y2 >= 0 and y2 < frame_height/4 and class_name == "Artel"):        
                formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
                if data_send :
                    video_url = f"video_{channel_name}_{formatted_datetime}.mp4"
                    video_filename = os.path.join(output_folder, video_url) 
                    video_writer = cv2.VideoWriter(video_filename, fourcc, frame_rate, frame_size)
                video_writer.write(color_frame)
                # print("writing video")
                det_elapsed = time.time() - last_time
                detected_time = detected_time + det_elapsed
                det_last_time = time.time()
                data_send = False
             
        elapsed = time.time() - det_last_time
        if (elapsed > 3 and data_send == False):
            if (int(detected_time) >= 5):
                data = { 
                        "is_active": True,
                        "duration": int(detected_time),
                        "channel_name": channel_name,
                        "company_name": "artel",
                        "video_url": "/root/Project/advertising-tracking/videos/"+video_url,
                        "data": current_datetime.strftime("%Y-%m-%d"),
                        "time": current_datetime.strftime("%H:%M:%S")
                    }
                # print(data)
                response = requests.post(url, json=data, auth=HTTPBasicAuth(username, password))
                if response.status_code == 201:
                    print("Data sent successfully")
                    print("Response:", response.json())
                else:
                    print("Failed to send data")
                    print("Response:", response.text)

            detected_time = 0
            data_send = True
            video_writer.release()
        
        last_time = time.time()

        # cv2.imshow(f'{channel_name}', color_image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        elapsed_time = time.time() - start_time
        # Add a delay to achieve the desired frame rate
        if elapsed_time < frame_delay:
            time.sleep(frame_delay - elapsed_time)

except Exception as e:
    print("Error occured: ", e)

finally:
    cap.release()
    if video_writer:
        video_writer.release()

    cv2.destroyAllWindows()
    


