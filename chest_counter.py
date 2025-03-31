#!/usr/bin/env python3

from automate import Automator
from datetime import datetime, timezone, timedelta
import time
import re
import json
import math

qualities = {
    "godlike": (255, 160, 0),
    "ascendant": (255, 0, 0),
    "legendary": (255, 80, 0),
    "epic": (160, 80, 255),
    "rare": (0, 128, 255),
    "uncommon": (0, 255, 0),
    "common": (255, 255, 255),
    "poor": (128, 128, 128)
}

def hue(v):
    total = sum(v)
    return tuple(x / total for x in v)

def dist(a, b):
    result = 0
    for x, y in zip(a, b):
        result += (x - y) ** 2
    return math.sqrt(result)

def find_quality(v):
    best = None
    best_dist = None
    h = hue(v)
    for quality, reference in qualities.items():
        current = dist(h, hue(reference))
        if best is None or current < best_dist:
            best = quality
            best_dist = current
    return best

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
        quality = find_quality(a.mean(-586, 0, -578, 8))
        hours = 0
        minutes = 0
        match = re.search(r"(\d+)h", expiry)
        if match is not None:
            hours = 19 - int(match.group(1))
        match = re.search(r"(\d+)m", expiry)
        if match is not None:
            minutes = 60 - int(match.group(1))
        origin_time = datetime.now(timezone.utc) - timedelta(hours = hours, minutes = minutes)
        print(json.dumps({
            "timestamp": origin_time.isoformat(),
            "author": author,
            "kind": kind,
            "quality": quality,
            "source": source
        }))
        a.click()
        a.move(200, 0)
        time.sleep(0.1)

a = Automator()
while True:
    if not open_chests(a):
        a.restart_game()
