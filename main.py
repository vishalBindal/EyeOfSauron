from threading import Thread
from eye_detect import main
from gui import *
from config import settings

# start settings gui
set_gui = settingsGui()
set_gui.run()
# thread_detector = Thread(target=set_gui.run())
# thread_detector.setDaemon(True)
# thread_detector.start()

# Starting the detector
# main()

# save settings
file = open('config.py', 'w')
file.write('state = {"drowsiness": False, "blink_required": False, "night_dark_mode": False}\nsettings=')
file.write(str(settings))
file.close()


