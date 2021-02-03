# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import os
import imutils
import time
import dlib
import cv2
from pydub import AudioSegment, playback
from time import sleep
import utilities

# Import config settings and state
from config import settings, state

# Import notify_user
from notify import notify_user


def play_alarm(file_path, flag):
    if flag == 1 or flag == 2:
        if not notify_user(flag):
            file_type = file_path.split('.')[-1]
            sound = AudioSegment.from_file(file_path, file_type)
            sound_chunk = playback.make_chunks(sound, 3000)[0]
            playback.play(sound_chunk)
        else:
            print('Alarm cancelled!')
    else:
        notify_user(flag)


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear


def get_avg_brightness(rgb_image):
    # Convert image to HSV
    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

    # Add up all the pixel values in the V channel
    sum_brightness = np.sum(hsv[:, :, 2])
    area = hsv.shape[0] * hsv.shape[0]  # pixels

    # find the avg
    avg = sum_brightness / area

    return avg


def main():
    shape_predictor = 'shape_predictor_68_face_landmarks.dat'
    webcam = 0
    # define two constants, one for the eye aspect ratio to indicate
    # blink and then a second constant for the number of consecutive
    # frames the eye must be below the threshold for to set off the
    # alarm
    EYE_AR_THRESH = 0.28
    EYE_AR_CONSEC_FRAMES = 48
    ALPHA = 0.5
    EYE_BLINK_THRESH = 0.25
    BLINK_THRESH = 150
    ear_ratio = 0.4

    # initialize the frame counter as well as a boolean used to
    # indicate if the alarm is going off
    COUNTER = 0
    NOT_BLINK_COUNTER = 0
    ALARM_ON = False

    NIGHT_BRIGHTNESS_THRES = 120
    ALARM_DARK_MODE = False

    AWAY_THRES = 200
    AWAY_COUNTER = 200
    ALARM_AWAY = False


    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(shape_predictor)
    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # start the video stream thread
    print("[INFO] starting video stream thread...")
    vs = VideoStream(webcam).start()
    time.sleep(1.0)

    # loop over frames from the video stream
    while True:
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=450)
        avg_brightness = get_avg_brightness(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)

        cv2.putText(frame, "Brightness: " + str(round(avg_brightness, 2)), (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if (not utilities.dark_mode_on()) and avg_brightness < NIGHT_BRIGHTNESS_THRES:
            state["night_dark_mode"] = True
            if not ALARM_DARK_MODE:
                ALARM_DARK_MODE = True
                alarm_path = os.path.join('alarms', settings['alarm_file'])
                t = Thread(target=play_alarm,
                           args=(alarm_path, 4))
                t.deamon = True
                t.start()
        else:
            state["night_dark_mode"] = False
            ALARM_DARK_MODE = False



        if settings['away']:
            if len(rects) == 0:
                AWAY_COUNTER += 1
                if AWAY_COUNTER >= AWAY_THRES:
                    # if the alarm is not on, turn it on
                    if not ALARM_AWAY:
                        ALARM_AWAY = True
                        # start a thread to have the alarm
                        # sound played in the background
                        alarm_path = os.path.join('alarms', settings['alarm_file'])
                        t = Thread(target=play_alarm,
                                   args=(alarm_path, 2))
                        t.deamon = True
                        t.start()
                    cv2.putText(frame, "ARE YOU THERE!", (280, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            else:
                AWAY_COUNTER = 0
                ALARM_AWAY = False

        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0
            ear_ratio = (1 - ALPHA) * ear_ratio + ALPHA * ear

            # compute the convex hull for the left and right eye, then
            # visualize each of the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

            if settings['stare']:
                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < EYE_BLINK_THRESH:
                    NOT_BLINK_COUNTER = 0
                else:
                    NOT_BLINK_COUNTER += 1
                    if NOT_BLINK_COUNTER > BLINK_THRESH:
                        cv2.putText(frame, "BLINK ALERT!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if settings['drowsy']:
                if ear_ratio < EYE_AR_THRESH:
                    COUNTER += 1
                    # if the eyes were closed for a sufficient number of
                    # then sound the alarm
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        # if the alarm is not on, turn it on
                        if not ALARM_ON:
                            ALARM_ON = True
                            # start a thread to have the alarm
                            # sound played in the background
                            alarm_path = os.path.join('alarms', settings['alarm_file'])
                            t = Thread(target=play_alarm,
                                       args=(alarm_path, 1))
                            t.deamon = True
                            t.start()
                        # draw an alarm on the frame
                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                # otherwise, the eye aspect ratio is not below the blink
                # threshold, so reset the counter and alarm
                else:
                    COUNTER = 0
                    ALARM_ON = False

            # draw the computed eye aspect ratio on the frame to help
            # with debugging and setting the correct eye aspect ratio
            # thresholds and frame counters
            cv2.putText(frame, "E.A.R.: {:.2f}".format(ear_ratio), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # show the frame
        if settings['display_frames']:
            cv2.imshow("I see everything", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            # if key == ord("q"):
            #     break
        else:
            cv2.destroyAllWindows()
            sleep(0.001)
    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()