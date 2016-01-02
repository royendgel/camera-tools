CAMERA-TOOLS
=============
### pull, manipulate rtsp, mjpeg streams, it uses ffmpeg and pexpect.


Requirements:
- Python 2.7
- Pexpect
- ffmpeg

##Usage

Import it :

`from cameratools import CameraTools`

initialize it :

`cam = CameraTools()`

To pull and save a stream : 

`cam.pull_rtsp('your_ip/stream')`