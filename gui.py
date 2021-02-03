import threading
from tkinter import *
from tkinter.ttk import *
from config import settings, state
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


def play_alarm(file_path):
    file_type = file_path.split('.')[-1]
    sound = AudioSegment.from_file(file_path, file_type)
    sound_chunk = playback.make_chunks(sound, 3000)[0]
    playback.play(sound_chunk)


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


class settingsGui:
    def __init__(self):
        # Process for alarm audio playback
        self.play_process = None

        # Setting up the window
        self.window = Tk()
        self.window.title("The Great Eye's settings")
        self.window.geometry('600x400')

        # Setting window icon
        photo = PhotoImage(file='icons/img4.png')
        self.window.iconphoto(False, photo)

        # Setting up tabs
        tab_control = Notebook(self.window)
        self.alarm_tab = Frame(tab_control)
        self.gen_tab = Frame(tab_control)
        tab_control.add(self.gen_tab, text='General')
        tab_control.add(self.alarm_tab, text='Alarm')
        tab_control.pack(expand=1, fill='both')

        # -- Setting up general tab --
        self.display_state = BooleanVar()
        self.display_state.set(settings['display_frames'])
        self.chk_display = Checkbutton(self.gen_tab, text='Display webcam video with eye segmentation', var=self.display_state, padding=5, command=self.display_callback)
        self.chk_display.grid(row=0, column=0, sticky='w')

        self.drowsy_state = BooleanVar()
        self.drowsy_state.set(settings['drowsy'])
        self.chk_drowsy = Checkbutton(self.gen_tab, text='Alarm if user is drowsy', var=self.drowsy_state, padding=5, command=self.ftr_drowsy_callback)
        self.chk_drowsy.grid(row=1, column=0, sticky='w')

        self.away_state = BooleanVar()
        self.away_state.set(settings['away'])
        self.chk_away = Checkbutton(self.gen_tab, text='Alarm if user is away', var=self.away_state, padding=5, command=self.ftr_away_callback)
        self.chk_away.grid(row=2, column=0, sticky='w')

        self.stare_state = BooleanVar()
        self.stare_state.set(settings['stare'])
        self.chk_stare = Checkbutton(self.gen_tab, text='Alarm if user is continuosly staring at the screen', var=self.stare_state, padding=5, command=self.ftr_stare_callback)
        self.chk_stare.grid(row=3, column=0, sticky='w')

        self.light_state = BooleanVar()
        self.light_state.set(settings['light'])
        self.chk_light = Checkbutton(self.gen_tab, text='Advise user regarding lighting conditions', var=self.light_state, padding=5, command=self.ftr_light_callback)
        self.chk_light.grid(row=4, column=0, sticky='w')

        frame = Frame(self.gen_tab)
        frame.grid(row=5, column=0, sticky='w')
        self.time_lbl = Label(frame, text="Notification time before alarm (in seconds)", padding=5)
        self.time_lbl.grid(row=0, column=0, sticky='w')
        self.time_var = IntVar()
        self.time_var.set(settings['time_warn'])
        self.spin = Spinbox(frame, from_=0, to=100, width=5, textvariable=self.time_var, command=self.time_val_change)
        self.spin.grid(row=0, column=1, sticky='w')

        # -- Setting up alarm tab --
        self.alarm_tab.rowconfigure([0, 2, 3], weight=1, minsize=30)
        self.alarm_tab.rowconfigure([1], weight=2, minsize=80)
        self.alarm_tab.columnconfigure(0, weight=1, minsize=200)

        self.alarm_header = Label(self.alarm_tab, text="Current alarm sound: None", padding=10)
        self.alarm_header.grid(column=0, row=0, sticky='nsew')

        self.alarms_dir = 'alarms'
        self.listbox = Listbox(self.alarm_tab, height=10, width=70, bg="white", activestyle='dotbox', fg="black")

        alarm_files = [f for f in os.listdir(self.alarms_dir) if os.path.isfile(os.path.join(self.alarms_dir, f))]

        if settings['alarm_file'] in alarm_files:
            i = alarm_files.index(settings['alarm_file'])
            alarm_files[0], alarm_files[i] = alarm_files[i], alarm_files[0]

        self.file_names = [f.split('.')[0] for f in alarm_files]
        self.file_extensions = [f.split('.')[1] for f in alarm_files]

        for i, f in enumerate(self.file_names):
            self.listbox.insert(i + 1, f)

        self.listbox.grid(column=0, row=1, sticky='nsew')
        self.listbox.select_set(0)
        self.selectalarm()

        self.listbox.configure(justify='center')

        self.btn_play = Button(self.alarm_tab, text='Play selected sound', command=self.playcallback)
        self.btn_select = Button(self.alarm_tab, text='Choose selected sound', command=self.selectalarm)
        self.btn_play.grid(column=0, row=2, sticky='nsew')
        self.btn_select.grid(column=0, row=3, sticky='nsew')

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.live_video_capture_display, args=())
        self.thread.start()
        # thread_detector = Thread(target=self.live_video_capture_display())
        # thread_detector.setDaemon(True)
        # thread_detector.start()

    def live_video_capture_display(self):
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
        NIGHT_BRIGHTNESS_THRES = 120
        ear_ratio = 0.4

        # initialize the frame counter as well as a boolean used to
        # indicate if the alarm is going off
        COUNTER = 0
        NOT_BLINK_COUNTER = 0
        ALARM_ON = False

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

            # loop over the face detections
            for rect in rects:
                cv2.putText(frame, "Brightness: " + str(round(avg_brightness, 2)), (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                if avg_brightness < NIGHT_BRIGHTNESS_THRES:
                    state["night_dark_mode"] = True
                else:
                    state["night_dark_mode"] = False

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

                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < EYE_BLINK_THRESH:
                    NOT_BLINK_COUNTER = 0
                    state["blink_required"] = False
                else:
                    NOT_BLINK_COUNTER += 1
                    if NOT_BLINK_COUNTER > BLINK_THRESH:
                        state["blink_required"] = True
                        cv2.putText(frame, "BLINK ALERT!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                if ear_ratio < EYE_AR_THRESH:
                    COUNTER += 1
                    # if the eyes were closed for a sufficient number of
                    # then sound the alarm
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        state["drowsiness"] = True
                        # if the alarm is not on, turn it on
                        if not ALARM_ON:
                            ALARM_ON = True
                            # start a thread to have the alarm
                            # sound played in the background
                            alarm_path = os.path.join('alarms', settings['alarm_file'])
                            t = Thread(target=play_alarm,
                                       args=(alarm_path,))
                            t.deamon = True
                            t.start()
                        # draw an alarm on the frame
                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                # otherwise, the eye aspect ratio is not below the blink
                # threshold, so reset the counter and alarm
                else:
                    state["drowsiness"] = False
                    COUNTER = 0
                    ALARM_ON = False

                # draw the computed eye aspect ratio on the frame to help
                # with debugging and setting the correct eye aspect ratio
                # thresholds and frame counters
                cv2.putText(frame, "E.A.R.: {:.2f}".format(ear_ratio), (330, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

            # show the frame
            if settings['display_frames']:
                temptemptemp = 1
                # self.panel = tki.Label(image=frame)
                # self.panel.image = frame
                # self.panel.pack(side="left", padx=10, pady=10)

                # cv2.imshow("I see everything", frame)
                # key = cv2.waitKey(1) & 0xFF
                #
                # # if the `q` key was pressed, break from the loop
                # if key == ord("q"):
                #     break
            else:
                cv2.destroyAllWindows()
                sleep(0.001)
        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()

    def run(self):
        self.window.mainloop()


    def time_val_change(self):
        settings['time_warn'] = self.spin.get()
        print('Warning time changed to:', settings['time_warn'])

    def display_callback(self):
        settings['display_frames'] = self.display_state.get()
        print('Set Display:', settings['display_frames'])

    def ftr_drowsy_callback(self):
        settings['drowsy'] = self.drowsy_state.get()
        print('Set Drowsy:', settings['drowsy'])

    def ftr_away_callback(self):
        settings['away'] = self.away_state.get()
        print('Set away:', settings['away'])

    def ftr_stare_callback(self):
        settings['stare'] = self.stare_state.get()
        print('Set stare:', settings['stare'])

    def ftr_light_callback(self):
        settings['light'] = self.light_state.get()
        print('Set Light:', settings['light'])

    def playcallback(self):
        selection = self.listbox.curselection()
        if selection:
            i = selection[0]
            f = self.file_names[i] + '.' + self.file_extensions[i]
            file_path = os.path.join(self.alarms_dir, f)
            print('Playing:', file_path)
            alarm_path = os.path.join('alarms', settings['alarm_file'])
            t = Thread(target=play_alarm,
                       args=(file_path,))
            t.deamon = True
            t.start()
            # play_alarm(file_path)

    def selectalarm(self):
        selection = self.listbox.curselection()
        if selection:
            i = selection[0]
            f = self.file_names[i]
            self.alarm_header.configure(text='Current alarm sound: ' + f)
            settings['alarm_file'] = f + '.' + self.file_extensions[i]
            print('Alarm tone set to:', settings['alarm_file'])


if __name__ == '__main__':
    gui = settingsGui()
    gui.run()
