from time import sleep, time
import datetime
import os

import pexpect
import logging


class CameraTools(object):
    def __init__(self, ffmpeg_path='ffmpeg', recording_dir=''):
        self.recording_dir = recording_dir
        self.ffmpeg_path = ffmpeg_path
        self.restart_on_error = True
        self.start_time = None
        self.last_time = None
        self.elapsed = None

    def pull_rtsp(self, url=None, out_name='video.mp4', duration=0, handler=None):
        """
        Pull rtsp stream from camera
        :return:
        """
        frame_number = 0
        size = 0
        # cmd = "%s -y -probesize 32 -analyzeduration 0 -i %s %s" % (settings.FFMPEG_PATH, generate_cam_url(camera), out_name)
        rpath = os.path.join(self.recording_dir, out_name)
        cmd = "%s -y -i %s -vcodec copy -an %s" % (self.ffmpeg_path, url, rpath)
        self.out_name = out_name

        thread = pexpect.spawn(cmd)
        cpl = thread.compile_pattern_list([
            pexpect.EOF,
            "frame= *(\d+)*.+size= *(\d+)*.+time=(\d+:\d+:\d+)",
            "(.+)"
        ])
        start_time = datetime.datetime.now()
        while True:
            try:
                i = thread.expect_list(cpl, timeout=None)

                if i == 0:  # EOF
                    logging.info("the sub process exited")
                    break
                elif i == 1:
                    # When we get frame initialize start time
                    if not self.start_time:
                        self.start_time = time()
                    frame_number = thread.match.group(1)
                    size = int(thread.match.group(2)) * 1000
                    duration = thread.match.group(3)
                    logging.debug("Frame number %s" % (frame_number))

                self.handler(thread, i)

            except KeyboardInterrupt:  # Break whenever you interupt via keyboard
                self.close_thread(thread)
                break


            except Exception, e:  # on error call the on_error method
                self.on_error(thread)

            finally:  # maybe set error indication here ?
                self.last_time = time()
                if self.start_time:
                    self.elapsed = self.last_time - self.start_time
                self.handler(thread, i)

    def close_thread(self, thread):
        thread.sendintr()
        while thread.isalive():
            # if the thread is still alive, sleep for 1 second
            logging.info("Alive sleeping...")
            sleep(1)
        self.moov_atom(self.out_name)

    def moov_atom(self, fname):
        fname = os.path.join(self.recording_dir, fname)
        temp = "%s_temp.mp4" % (fname)
        cmd = "%s -y -i %s -movflags +faststart %s" % (self.ffmpeg_path, fname, temp)
        thread = pexpect.run(cmd)
        logging.info("did Moov Atom on the file: %s output : %s" % (temp, str(thread)))
        os.remove(fname)
        logging.info("removed the file %s" % (fname))
        os.rename(temp, fname)
        logging.info("renamed %s to %s" % (temp, fname))

    def check_stream_active(self, type='rtsp'):
        pass

    def handler(self, thread, i):
        pass

    def on_error(self, thread):
        if not self.restart_on_error:
            self.close_thread(thread)
