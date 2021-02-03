import platform
import os
import subprocess


def dark_mode_on():
    if platform.system() == 'Darwin':
        cmd = 'defaults read -g AppleInterfaceStyle'
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        return bool(p.communicate()[0])
    else:
        return False
