#!/usr/bin/env python3

from automate import Automator
import json
import time
import pyautogui
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("troops", help = "troop selection JSON file")
args = parser.parse_args()

troops_file = args.troops
with open(troops_file) as f:
    troops = json.load(f)

a = Automator(scale = 0.5)
timeout = 8
start = None
entered = dict()
done = False
if not a.await_samples("battle", 2):
    exit(1)
while not done:
    if start is None:
        start = time.time()
    done = True
    for name in troops:
        if name not in entered:
            if a.find("units/" + name):
                a.click(100, 7)
                time.sleep(0.02)
                a.write(troops[name])
                time.sleep(0.02)
                entered[name] = True
                start = time.time()
            else:
                done = False
    if not done:
        if time.time() > start + timeout:
            exit(1)
        time.sleep(0.1)
        pyautogui.scroll(-4)
        time.sleep(0.1)
        a.update()
