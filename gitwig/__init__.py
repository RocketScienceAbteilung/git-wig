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
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)

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

    sequencer = SequencerThread()
    pattern = parser.parse_folder(args.track_folder)
    sequencer.write(pattern)
    sequencer.start()
    threads.append(sequencer)

    # watch dog stuff
    observer = Observer()
    event_handler = CheckForChangesEvent()
    observer.schedule(event_handler, args.track_folder)
    observer.start()

    f = ui()

    def render_tracks():
        clips = sequencer.get_running_clips()
        f.stdscr.clear()
        for i, clip in enumerate(clips):
            f.stdscr.addstr(
                0, 1,
                '#'.ljust(2) + 'clip'.ljust(10) + 'pattern'.ljust(64),
                curses.color_pair(3)
            )
            f.stdscr.addstr(i + 1, 1, clip[0])
            f.stdscr.addstr(i + 1, 3, clip[1])
            f.stdscr.addstr(i + 1, 13, clip[2], curses.color_pair(2))
            f.stdscr.addstr(i + 1, 13 + clip[3], " ", curses.color_pair(1))

        f.stdscr.refresh()
        scheduler.enter(0.05, 1, render_tracks, ())

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0.05, 1, render_tracks, ())

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
