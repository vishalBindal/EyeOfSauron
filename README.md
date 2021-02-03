# Eye of Sauron
## How to run
- Installing CMake, Boost, Boost.Python, and X11. (These are prerequisites for dlib)
  - **Ubuntu:**
    ```bash
    $ sudo apt-get install build-essential cmake
    $ sudo apt-get install libgtk-3-dev
    $ sudo apt-get install libboost-all-dev
    ```
  - **macOS:** Download Xquartz/X11 from this link https://www.xquartz.org/ and install manually and then
    ```bash
    $ brew install cmake
    $ brew install boost
    $ brew install boost-python3
    ```

- Installing ffmpeg and libav or pyaudio (prerequisites for pydub)  
  ffmpeg is only used if pyaudio is not installed. 
  - **Ubuntu**
    ```bash
    $ sudo apt-get install ffmpeg libavcodec-extra
    ```
  - **macOS** ffmpeg didn't work for me in mac. So, I used pyaudio.
    ```bash
    $ brew install portaudio
    $ pip install --global-option='build_ext' --global-option='-I/usr/local/include' --global-option='-L/usr/local/lib' pyaudio
    ```

- Using Conda/Miniconda to create a python 3.6 environment
  Python 3.6 is required for an old OpenCV version that we are using in the current project. Also, it is a good practice in python to make virtual environments for each project.
  ```bash
  $ conda create --name newenv python=3.6
  $ conda activate newenv
  ```

- Install required python libs
  - Now, `$ pip install requirements.txt`
  - or  
    ```bash
    $ pip install numpy
    $ pip install scipy
    $ pip install scikit-image
    $ pip install dlib
    $ pip install opencv-contrib-python==3.4.2.16
    $ pip install imutils
    $ pip install pydub
    $ pip install pyobjc # if using macOS
    ```
  - Install notify-send.py for sending notifications in Ubuntu (not needed for macOS)
    ```bash
    $ pip install notify-send.py
    ```

- Running main.py
  ``` bash
  $ python main.py
  ```
