from threading import Thread
from eye_detect import main
from gui import *
from config import settings

thread_detector = Thread(target=main)
thread_detector.setDaemon(True)
thread_detector.start()

# start settings gui
set_gui = settingsGui()
set_gui.run()

# save settings
file = open('config.py', 'w')
file.write('state = {"drowsiness": False, "blink_required": False, "night_dark_mode": False}\nsettings=')
file.write(str(settings))
file.close()
