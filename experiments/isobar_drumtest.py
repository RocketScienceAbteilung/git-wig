#!/usr/bin/python
import isobar as iso

'''
Volca Beats Four-on-the-floor
'''

# setting sequences
BD = iso.PSeq([36, None, None, None])
CL = iso.PSeq([None, 39])
CH = iso.PSeq([42, None, 42, None])

# a Timeline schedules events at a given BPM.
# by default, send these over the first MIDI output.
timeline = iso.Timeline(
    136,
    ticks_per_beat=96,
    division=4,
    debug=False
)

# duration of 1 is now set to 1/16 note per beat
timeline.sched({'note': BD, 'channel': 9, 'dur': 1})
timeline.sched({'note': CL, 'channel': 9, 'dur': 4})
timeline.sched({'note': CH, 'channel': 9, 'dur': 2})

timeline.background()

import ipdb; ipdb.set_trace()

'''
Try to update the patterns on the fly
'''

# # update some of the paramters
# timeline.sched_mod(2, {'dur': 4.0/3}, quantize=16)
