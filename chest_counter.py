#!/usr/bin/env python3

from automate import Automator
from datetime import datetime, timezone, timedelta
import time
import re

def sanitize(s):
    return re.sub(r"[^a-zA-Z0-9 -]", "", s)

def open_chests(a):
    if not a.await_samples("clan", 2):
        return False
    a.click()
    if not a.await_samples(["gifts", "gifts_selected"], 2):
        return False
    a.click()
    while True:
        if not a.await_samples("open", 2):
            if a.await_samples("hand", 1):
                a.click()
            return True
        kind = sanitize(a.read(-560, -66, -140, -40))
        author = a.read(-518, -40, -140, -16)
        source = sanitize(a.read(-510, -20, -140, 4))
        expiry = re.sub(r"[^hm0-9]", "", a.read(-40, -42, 60, -18))
        hours = 0
        minutes = 0
        match = re.search(r"(\d+)h", expiry)
        if match is not None:
            hours = 19 - int(match.group(1))
        match = re.search(r"(\d+)m", expiry)
        if match is not None:
            minutes = 60 - int(match.group(1))
        # TODO: send/store this somewhere
        print([datetime.now(timezone.utc) - timedelta(hours = hours, minutes = minutes), author, kind, source])
        a.click()
        a.move(200, 0)
        time.sleep(0.1)

a = Automator()
while True:
    if not open_chests(a):
        a.restart_game()
