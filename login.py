#!/usr/bin/env python3

from automate import Automator
import time
import json
import argparse

def login(a, username, password):
    if not a.await_samples("next", 10):
        return False
    a.click(30, -180)
    time.sleep(2)
    if not a.await_samples("email", 2):
        return False
    a.click()
    time.sleep(0.1)
    a.write(username)
    a.tab()
    time.sleep(0.1)
    a.write(password)
    time.sleep(0.1)
    if not a.await_samples("login_finish", 2):
        return False
    a.click()
    return True

def speedup(a):
    if a.await_samples("carter_march", 2):
        a.click(190, 8)
        if not a.await_samples("speedup", 2):
            return True
        for _ in range(6):
            a.click(360, 36)
        time.sleep(1.5)
        return True
    return False

parser = argparse.ArgumentParser()
parser.add_argument("credentials", help = "credentials json file")
parser.add_argument("-w", "--worldmap", action = "store_true", default = False, help = "start to worldmap")
args = parser.parse_args()

with open(args.credentials) as f:
    credentials = json.load(f)
    username = credentials["username"]
    password = credentials["password"]

a = Automator()
while not login(a, username, password):
    a.refresh()
    time.sleep(1)
time.sleep(3)
while not a.start_game(worldmap = args.worldmap):
    a.refresh()
    time.sleep(3)
