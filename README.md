# git-wig

A Git enabled pattern sequencer. It allows to create music within the scope of your Dev environment. 

## Features

* plain text based pattern sequencer
* supports drum, monophonic and polyphonic track formats
* designed to be version controlled. 
* [syntax highlighting package for atom](https://github.com/RocketScienceAbteilung/language-gwg)
* console/curses session view

## Installation

Install Python and PortMidi (on OSX)

    brew install python --framework
    brew install portmidi

Create virtualenv

    virtualenv midihack
    cd midihack
    source bin/activate


### Installing isobar fork

When installing gitwig, it will use the latest official version of isobar and
install it along with all the other dependencies. However we need to fork and
modifiy isobar a bit to run with our MIDI stack (mido instead of rtmidi).

In order to do this we uninstall isobar (if already installed) and install
it in our working directories (regular pip installs are not meant to be edited
and go somewhere inside `lib/` by default).

Clone repository (make sure you're **not inside `gitwig/`**)

    git clone git@github.com:RocketScienceAbteilung/isobar.git
    cd isobar
    pip install -e .


### Installing gitwig

Clone repository (make sure you're **not inside `isobar/`**)

    git clone git@github.com:RocketScienceAbteilung/git-wig.git gitwig
    cd gitwig
    pip install -e .

Run gitwig

    git wig

### Other utilities

    git wig-messages (dump MIDI messages)
    git wig-ports (show all MIDI ports found)

or one of the experiments

    python experiments/isobar_drumtest.py

You should end up with a virtualenv that looks like

    midihack/
     |-- (virtualenv stuff like bin/ lib/ include/)
     |-- isobar/    (installed using pip install -e .)
     `-- gitwig/    (installed using pip install -e .)

And you can now edit both isobar and gitwig.
