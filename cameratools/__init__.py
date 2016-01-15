from time import sleep, time
import datetime
import os

import pexpect
import logging

import sys

logger = logging.getLogger(__name__)


class CameraTools(object):
    def __init__(self, ffmpeg_path='ffmpeg', recording_dir=''):
        self.recording_dir = recording_dir
        self.ffmpeg_path = ffmpeg_path
        self.restart_on_error = True
        self.start_time = None
        self.last_time = None
        self.elapsed = None
        self.thread = None
        self.errors = 0
        self.max_errors = 10

    def pull_rtsp(self, url=None, out_name='video.mp4', duration=0, handler=None):
        logger.debug("its inside swa!")
        """
        Pull rtsp stream from camera
        :return:
        """
        self.frame_number = 0
        size = 0
        # cmd = "%s -y -probesize 32 -analyzeduration 0 -i %s %s" % (settings.FFMPEG_PATH, generate_cam_url(camera), out_name)
        rpath = os.path.join(self.recording_dir, out_name)
        cmd = "%s -y -i %s -vcodec copy -an %s" % (self.ffmpeg_path, url, rpath)
        self.out_name = out_name

        thread = pexpect.spawn(cmd)
        self.thread = thread
        cpl = thread.compile_pattern_list([
            pexpect.EOF,
            "frame= *(\d+)*.+size= *(\d+)*.+time=(\d+:\d+:\d+)",
            "(.+)"
        ])
        start_time = datetime.datetime.now()
        while True:
            logger.debug('active!! in while loop before try')
            try:
                i = thread.expect_list(cpl, timeout=None)
                logger.debug("thread group: %s" % (i))
                if i == 0:  # EOF
                    logger.info("the sub process exited")
                    break
                elif i == 1:
                    # When we get frame initialize start time
                    if not self.start_time:
                        self.start_time = time()
                    self.frame_number = thread.match.group(1)
                    logger.debug("Frame number %s" % (self.frame_number))

                self.handler(thread, i)

            except KeyboardInterrupt:  # Break whenever you interupt via keyboard
                logger.error('Keyboard interupt')
                self.close_thread(thread)
                break


            except Exception, e:  # on error call the on_error method
                logger.error("error %s ==>" % (e))
                self.on_error(thread)


            finally:  # maybe set error indication here ?
                logger.debug("in finally block")
                self.last_time = time()
                if self.start_time:
                    self.elapsed = self.last_time - self.start_time
                self.handler(thread, i)

    def close_thread(self, thread):
        try:
            logger.info("in close thread sending sendintr")
            thread.sendintr()
            logger.info("sendintr sent")
            c = 0
            while thread.isalive():
                # if the thread is still alive, sleep for 1 second
                logger.debug("Alive sleeping...")
                sleep(1)
        except Exception, e:
            logger.info('Closed')

        self.moov_atom(self.out_name)

    def moov_atom(self, fname):
        logger.info("in moov_atom")
        fname = os.path.join(self.recording_dir, fname)
        temp = "%s_temp.mp4" % (fname)
        cmd = "%s -y -i %s -movflags +faststart %s" % (self.ffmpeg_path, fname, temp)
        thread = pexpect.run(cmd)
        logger.debug("did Moov Atom on the file: %s output : %s" % (temp, str(thread)))
        os.remove(fname)
        logger.debug("removed the file %s" % (fname))
        os.rename(temp, fname)
        logger.debug("renamed %s to %s" % (temp, fname))

    def check_stream_active(self, type='rtsp'):
        pass

    def handler(self, thread, i):
        pass

    def on_error(self, thread=None):
        if not self.restart_on_error:
            self.close_thread(thread)
