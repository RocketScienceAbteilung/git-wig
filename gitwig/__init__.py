import time
import argparse
import sched
import curses
import curses.panel
import sys
import signal

from .fileparser import ParserThread
from .sequencer import SequencerThread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ui:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)
        (self.width, self.height) = self.stdscr.getmaxyx()

    def quit_ui(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()
        print "Quit User Interface"


def main(inargs=None):
    parser = argparse.ArgumentParser(description='git-wig sequencer')
    parser.add_argument('track_folder')
    parser.add_argument('--noui', dest='noui', action='store_false')
    parser.set_defaults(feature=True)

    args = parser.parse_args()

    class CheckForChangesEvent(FileSystemEventHandler):
        def on_modified(self, event):
            # TODO: only parse changed files
            patterns = parser.parse_folder(args.track_folder)
            sequencer.write(patterns)

    threads = []

    parser = ParserThread()
    parser.start()
    threads.append(parser)

    time.sleep(1)

    song_name, bpm = parser.parse_song(args.track_folder)
    sequencer = SequencerThread(song_name, bpm, device=None)
    pattern = parser.parse_folder(args.track_folder)
    sequencer.write(pattern)
    sequencer.start()
    threads.append(sequencer)

    # watch dog stuff
    observer = Observer()
    event_handler = CheckForChangesEvent()
    observer.schedule(event_handler, args.track_folder)
    observer.start()

    if args.noui:
        f = ui()

        def render_tracks():
            clips = sequencer.get_running_clips()
            f.stdscr.clear()
            f.stdscr.addstr(
                0, 0,
                "Track: %s (%d BPM)" % (song_name, bpm),
                curses.color_pair(4)
            )
            for i, clip in enumerate(clips):
                f.stdscr.addstr(
                    1, 1,
                    '#'.ljust(3) + 'clip'.ljust(11) + 'pattern'.ljust(64),
                    curses.color_pair(3)
                )
                f.stdscr.addstr(i + 2, 1, clip[0])
                f.stdscr.addstr(i + 2, 4, clip[1])
                f.stdscr.addstr(i + 2, 14, clip[2], curses.color_pair(2))
                f.stdscr.addstr(i + 2, 14 + clip[3], " ", curses.color_pair(1))

            f.stdscr.refresh()
            scheduler.enter(0.08, 1, render_tracks, ())

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(0.08, 1, render_tracks, ())

        def signal_handler(signal, frame):
            print('quitting git-wig')
            f.quit_ui()
            # stop all tracks
            sequencer.stop_all()
            # stop all threads
            for t in threads:
                t.quit = True

            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        scheduler.run()
