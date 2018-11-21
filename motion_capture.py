import cv2, time, pandas
from datetime import datetime

count_delay = 0                                     # count to delay video capture
first_frame = None                                  # skips over the first video frame
motion_status = [None, None]                        # keeps track of motion with 0's and 1's
timestamps = []                                     # timestamps of transitions between 0's and 1's
df = pandas.DataFrame(columns = ["start", "end"])   # numpy array of start and end times for motion detection

# capture video from the webcam
video = cv2.VideoCapture(0)

while True:
    # create frame object to read video, returning boolean and numpy array
    check, frame = video.read()

    # denotes no current motion in the frame
    status = 0

    # convert into gray version of frame and apply gaussian blur for better accuracy
    grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.GaussianBlur(grayscale, (21, 21), 0)

    # assign the first frame of the video after count delay
    if count_delay < 40 and first_frame is None:
        count_delay += 1
        continue
    elif first_frame is None:
        first_frame = grayscale
        continue

    # difference between first frame and current frame of the image
    delta_frame = cv2.absdiff(first_frame, grayscale)

    # threshold frame with removed black holes in the bigger white areas
    threshold_frame = cv2.threshold(delta_frame, 30, 255, cv2.THRESH_BINARY)[1]
    threshold_frame = cv2.dilate(threshold_frame, None, iterations = 2)

    # find and create contours of white objects in threshhold frame
    (_,cnts,_) = cv2.findContours(threshold_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in cnts:
        if cv2.contourArea(contour) < 10000:
            continue
        
        # if the area is greater than 10,000 pixels, draw rectangle around it and set motion status
        status = 1
        (x, y, width, height) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)

    # add current status to the motion status list and shorten list to the last two
    motion_status.append(status)
    motion_status = motion_status[-2:]

    # check if the two last items of motion status list shows a change in motion
    if motion_status[-1] == 1 and motion_status[-2] == 0:
        timestamps.append(datetime.now())
    if motion_status[-1] == 0 and motion_status[-2] == 1: 
        timestamps.append(datetime.now())

    # display the images
    cv2.imshow("Grayscaled Frame", grayscale)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", threshold_frame)
    cv2.imshow("Colored Frame", frame)

    # close all image windows and get current time if q is pressed:
    key = cv2.waitKey(1)
    if key == ord("q"):
        if status == 1:
            timestamps.append(datetime.now())
        break
    
# add all the times in timestamps to the data frame and convert data frame into csv file
for i in range(0, len(timestamps), 2):
    df = df.append({"start": timestamps[i], "end": timestamps[i+1]}, ignore_index = True)
df.to_csv("timestamps.csv")

# release the camera and destroy the window
video.release()
cv2.destroyAllWindows()