# Total Battle Automation

Total Battle is a terrible game that manipulates its players into spending as much money and time on it as possible.
This project contains some scripts intended to reduce the amount of time spent.

To maximise cross-platform applicability, the scripts are tailored to operate on the web version of the game, running in a browser such as Firefox.
Note that some browsers do not allow number inputs when for example selecting troops.
Sadly the web version of the game will crash relatively often.
To counter this, the scripts will try to refresh the game whenever they feel they got stuck.

## Crypting

The `crypt.py` script runs automatic crypting via the watchtower.
By default the script will recognise common crypts; use the `-t` flag to select rare or epic crypts.
Note that the watchtower needs to be aligned with this selection before running the script.

The script should be started with Carter selected as the only captain while the game is on the worldmap, zoomed in to the maximum 125%.
It takes a careful approach to selecting crypts.
From the watchtower screen, a random one of the visible locations is chosen.
Once the location on the map is loaded, the script will find the location of a crypt according to the `-t` flag.
It will filter out any crypts that have pre-existing blue or red lines over them in order to not steal any crypts.
It will also refuse to march on any rare crypts that are already opened.

Note that the crypt actually marched on may not be the one that was originally selected via the watchtower.
In particular, it may not be one of the same level.

## Chest Counter

This is an experimental implementation that has not been tested in production.
For each chest counted it outputs a JSON object on a single line, which can be processed by other software.
It will also regularly click the help button.
