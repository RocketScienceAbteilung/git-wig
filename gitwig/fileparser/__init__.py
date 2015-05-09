from __future__ import division
import __future__
import threading
import time
import os
import numpy as np
import re
import isobar as iso
import argparse
from itertools import izip


class ParserThread(threading.Thread):

    rest_char = ' '
    piano_char = '.'
    forte_char = ','

    instrument = ''
    note_array = []

    num_notes = 0

    piano_vel = 64
    forte_vel = 127

    drum_dict = {}
    mel_dict = {}

    def __init__(self):
        threading.Thread.__init__(self)
        self.quit = False

    def run(self):
        self.i = 0
        while True:
            if self.quit:
                return

            # TODO: Put repeating logic here.
            # Put reusable subtasks in their own methods/files/modules

            # All data meant for the application should be saved in an
            # attribute of this class.

            # All mode-sets, calls and other interactions from application
            # should be declared as methods of this object.

            # self.note_array = np.array(notes)

            # print self.note_array

            time.sleep(1)

    def parse_folder(self, foldername):
        patterns = []
        for root, dirs, files in os.walk(foldername):
            for file in files:
                if file.endswith(('.gwd', '.gwm', '.gwp')):
                    parsed = self.parse_file(os.path.join(root, file))
                    if parsed is not None:
                        if isinstance(parsed, list):
                            patterns += parsed
                        else:
                            patterns.append(parsed)
        return patterns

    def parse_file(self, filename):

        lines = open(filename)

        basename = os.path.splitext(os.path.basename(filename))[0]
        if filename.endswith(".gwd"):
            return parse_drums(lines, basename)
        if filename.endswith(".gwm"):
            return parse_mels(lines, basename)
        if filename.endswith(".gwp"):
            return parse_poly(lines, basename)


def parse_mels(lines, name):

    # num_notes = len(lines)

    pattern_list = []
    tr_type = 'monophon'

    chan = ''
    notes = []
    vels = []

    for i in lines:
        m = re.search('([CDEFGAB])([b\#]?)-?(\d)\s(\d{2})\s(\d{3})', i)

        if m:
            curr_note = iso.util.nametomidi(
                str(m.group(1) + m.group(2) + m.group(3))
            ) + 12
            chan = int(m.group(4))
            curr_vel = int(m.group(5))
        else:
            curr_note = 0
            curr_vel = 0

        notes.append(curr_note)
        vels.append(curr_vel)

    curr_dict = {
        'name': name,
        'type': tr_type,
        'channel': chan,
        'note': notes,
        'amp': vels,
        'gate': 0.75,
        'dur': 1
    }
    pattern_list.append(curr_dict)

    return pattern_list


def parse_poly(lines, name):

    pattern_list = []
    tr_type = 'polyphon'

    chan = ''

    k = 0
    for i in lines:
        ch_rgx = re.search('ch\:\s*(\d+)', i)
        if ch_rgx:
            chan = int(ch_rgx.group(1))

        m = re.search('([CDEFGAB])([b\#]?)-?(\d)\s((?:[\+\-][0-9a-fA-F]){1,}):?((\d)\/?(\d)?)?', i)

        if m:


            k += 1
            root_note = iso.util.nametomidi(
                str(m.group(1) + m.group(2) + m.group(3))
            ) + 12

            note_mods = m.group(4)
            num_notes = len(note_mods) / 2

            notes = np.zeros((num_notes,), dtype=np.int)
            vels = np.ones((num_notes,), dtype=np.int) * 127

            mod_vals = splitCount(note_mods, 2)
            i_mod_vals = np.array([ int(x, 16) for x in mod_vals ])
            

            pattern_duration = m.group(5)

            if pattern_duration is None:
                pattern_duration = 1
            else:
                pattern_duration = eval(
                    compile(
                        pattern_duration,
                        '<string>',
                        'eval',
                        __future__.division.compiler_flag
                    )
                )

            notes = (i_mod_vals + root_note)

            curr_dict = {
                'name': name + str(k),
                'type': tr_type,
                'channel': chan,
                'note': notes.tolist(),
                'amp': vels.tolist(),
                'gate': 0.9,
                'dur': pattern_duration
            }
            pattern_list.append(curr_dict)

        else:
            root_note = 0
            curr_vel = 0

    return pattern_list


def parse_drums(lines, name):

    pattern_list = []

    tr_type = 'drums'

    chan = ''

    for i in lines:
        ch_rgx = re.search('ch\:\s*(\d+)', i)
        if ch_rgx:
            chan = int(ch_rgx.group(1))

        m = re.search('(#)?([.,\s]+)(.+):(\d{2}):?((\d)\/?(\d)?)?', i)
        if m:
            content_line = m.group(2)
            num_notes = len(content_line)

            # process content

            # content_line = content.strip('\n')

            notes = np.zeros((num_notes,), dtype=np.int)
            vels = np.zeros((num_notes,), dtype=np.int)

            # rest_idcs = list(find_all(content_line, ParserThread.rest_char))

            piano_idcs = list(find_all(content_line, ParserThread.piano_char))

            forte_idcs = list(find_all(content_line, ParserThread.forte_char))

            pattern_duration = m.group(5)

            if pattern_duration is None:
                pattern_duration = 1
            else:
                pattern_duration = eval(
                    compile(
                        pattern_duration,
                        '<string>',
                        'eval',
                        __future__.division.compiler_flag
                    )
                )

            mute = m.group(1)

            for i in piano_idcs:
                notes[i] = m.group(4)
                if mute is not None:
                    vels[i] = 0
                else:
                    vels[i] = ParserThread.piano_vel

            for i in forte_idcs:
                notes[i] = m.group(4)
                if mute is not None:
                    vels[i] = 0
                else:
                    vels[i] = ParserThread.forte_vel

            curr_dict = {
                'name': m.group(3),
                'type': tr_type,
                'channel': chan,
                'note': notes.tolist(),
                'amp': vels.tolist(),
                'dur': pattern_duration
            }

            pattern_list.append(curr_dict)

    return pattern_list


def splitCount(s, count):
    return [
        ''.join(x)
        for x in zip(
            *[list(s[z::count]) for z in range(count)]
        )
    ]


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse git-wig clip files')
    parser.add_argument('clip', type=str, help='Input clip file')

    args = parser.parse_args()

    p = ParserThread()
    p.start()

    pattern = p.parse_file(args.clip)
    print pattern
