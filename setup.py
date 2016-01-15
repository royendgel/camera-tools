import os
from setuptools import setup

setup(
    name = "camera-tools",
    version = "0.1",
    author = "Royendgel Silberie",
    author_email = "rsilberie@techprocur.com",
    description = ("rtsp, mjpeg client, server and manipulator"),
    keywords = "camera tools rtsp mjpeg jpeg",
    url = "https://github.com/royendgel/camera-tools",
    packages=['cameratools'],
    classifiers=[
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Unix',
      'Development Status :: 3 - Alpha',
      'Topic :: Utilities',
      'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    install_requires=[
      'pexpect',
    ],
)