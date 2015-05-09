from __future__ import division
from __future__ import print_function

import threading
import time
import isobar as iso
import sys
import numpy as np


class SequencerThread(threading.Thread):
    def __init__(self, name='mysong', bpm=132):
        threading.Thread.__init__(self)
        self.bpm = bpm
        self.quit = False
        self.name = name
        self.t = iso.Timeline(
            bpm,
            ticks_per_beat=96,
            division=4,
            debug=False,
            device=None
        )

    def write(self, pattern):

        if isinstance(pattern, list):
            self.check_clip_index(pattern)
            for p in pattern:
                self.write(p)
            return

        # replace notes with isobar pattern
        isobar_pattern = {}

        isobar_pattern['note'] = iso.PSeq(pattern['note'])
        isobar_pattern['amp'] = iso.PSeq(pattern['amp'])
        isobar_pattern['channel'] = pattern['channel'] - 1
        isobar_pattern['dur'] = pattern['dur']

        if pattern['type'] in ["monophon", "polyphon"]:
            isobar_pattern['gate'] = pattern['gate']

        elif pattern['type'] is "drums":
            pass

        idx = self.clip_index(pattern['name'])

        if idx > -1:
            print("Modifying", self.t.channels[idx].name)
            self.t.sched_mod(idx, isobar_pattern, quantize=16)
        else:
            print("Adding", pattern['name'])
            self.t.sched(isobar_pattern, name=pattern['name'], quantize=16)

    def clip_index(self, name):
        ''' checks if timeline is in clip and returns index if found'''
        for idx, ch in enumerate(self.t.channels):
            if ch.name == name:
                return idx
        return -1

    def check_clip_index(self, pattern):
        ''' check for clips to brutally removed'''
        channels = []
        for p in pattern:
            idx = self.clip_index(p['name'])
            if idx > -1:
                channels.append(self.t.channels[idx])
        self.t.channels = channels

    def get_running_clips(self):
        clips = []
        for ch in self.t.channels:
            amps = "".join(
                map(str, (np.array(ch.events['amp'].list) > 0).astype(int))
            ).replace("0", " ").replace('1', '.')
            clips.append((
                str(ch.events['channel'].constant + 1),
                ch.name,
                amps,
                ch.events['note'].pos
            ))

        return clips

    def start(self):
        self.t.background()

    def pause(self):
        pass

    def launch_clip(self, clip_id):
        pass

    def show_clip(self, clip_id):
        pass

    def stop_all(self):
        print("stop")
        for channel in self.t.channels:
            channel.finished = True

    def run(self):
        self.i = 0
        while True:
            if self.quit:
                return

            # get pattern status
            for channel in self.t.channels:
                print("%02d" % channel.events['note'].pos, end='\b\b')
                sys.stdout.flush()

            # TODO: Put repeating logic here.
            # Put reusable subtasks in their own methods/files/modules

            # All data meant for the application should be saved in an
            # attribute of this class.

            # All mode-sets, calls and other interactions from application
            # should be declared as methods of this object.

            time.sleep(0.1)


if __name__ == "__main__":
    pass
