from threading import Thread
from eye_detect import main
from gui import *
from config import settings,state

thread_detector = Thread(target=main)
thread_detector.setDaemon(True)
thread_detector.start()

# start settings gui
set_gui = settingsGui()
set_gui.run()

# save settings
state['brightness'] = int(state['brightness'])
file = open('config.py', 'w')
file.write('state=')
file.write(str(state))
file.write('\nsettings=')
file.write(str(settings))
file.close()
