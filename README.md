# Eye of Sauron
## How to run
### Installing prerequisites
- Installing CMake, Boost, Boost.Python, and X11. (These are prerequisites for dlib)
  - **Ubuntu:**
    ```bash
    $ sudo apt-get install build-essential cmake
    $ sudo apt-get install libgtk-3-dev
    $ sudo apt-get install libboost-all-dev
    ```
  - **macOS:** Download Xquartz/X11 from this link https://www.xquartz.org/ and install manually and then
    ```bash
    brew install cmake
    brew install boost
    brew install boost-python3
    ```

- Using Conda/Miniconda to create a python 3.6 environment
  Python 3.6 is required for an old OpenCV version that we are using in the current project. Also, it is a good practice in python to make virtual environments for each project.
  ```bash
  conda create --name newenv python=3.6
  conda activate newenv

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
    $ pip install playsound
    $ pip install pyobjc
    ```

- Running eye_detect.py
  ``` bash
  python eye_detect.py --shape-predictor shape_predictor_68_face_landmarks.dat --alarm alarm.wav
  ```
