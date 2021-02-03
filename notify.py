import platform
import subprocess
from time import sleep
import os

base_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(base_dir, 'icons/img4.png')

def notify_user(use_case):
    '''
    use_case: 1,2,3 or 4 according to the use case (see below)
    Returns: True if user interacted with the notification, False otherwise
    '''
    heading = 'Alert from the great eye'
    message,button_msg = None,None
    if use_case == 1:
        message = 'You seem drowsy. The alarm is set to go off soon, unless you press the button within 5s.'
        button_msg = 'I am awake! Cancel alarm'
    elif use_case == 2:
        message = 'Are you there? The alarm is set to go off soon, unless you press the button within 5s.'
        button_msg = 'Yes, I am here! Cancel alarm'
    elif use_case == 3:
        message = 'You are staring at the screen far too long. You are advised to take a break.'
    elif use_case == 4:
        message = 'It seems you are working in unhealthy lighting conditions. You are advised to turn on night mode/dark mode.'

    if platform.system() == 'Linux':
        cmd = ['notify-send.py', heading, message, '-i', icon_path]
        if button_msg is not None:
            cmd += ['--action', '42:'+"'"+button_msg+"'"]
        subp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        sleep(5)
        if subp.poll() is not None:
            out = subp.communicate()[0].decode('utf-8')
            return ('closed' in out.split('\n'))
        else:
            subp.terminate()
            return False

    elif platform.system() == 'Darwin':
        display_cmd = f'display alert "{heading}" message "{message}"'
        cmd = ['osascript', '-e', display_cmd]
        subp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        sleep(5)
        if subp.poll() is not None:
            return True
        else:
            subp.terminate()
            return False

if __name__=='__main__':
    print(notify_user(1))