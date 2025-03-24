#!/usr/bin/env python3

from automate import Automator
import time

crypts = ["crypts/" + name for name in ["cave", "cog", "dune", "greek", "grotto", "ice", "lava", "rune", "skull", "snake", "temple", "pyramid"]]

def crypt(a):
    if not a.await_samples("watchtower", 2):
        return False
    a.click()
    if not a.await_samples(["crypts_selected", "crypts_unselected"], 2):
        return False
    a.click()
    time.sleep(0.4)
    if not a.await_samples_multi("go_watchtower", 2):
        return False
    if not a.random_multi():
        return False
    a.click()
    if not a.await_samples_multi(crypts, 4):
        return False
    a.multi_block_color(120, 90, (48, 37, 130))
    a.multi_block_color(120, 90, (254, 74, 32))
    if not a.random_multi():
        return False
    a.click()
    a.move(400, 0)
    time.sleep(0.3)
    if not a.await_samples("carter_selected", 2):
        return False
    if not a.await_samples("explore", 2):
        return False
    a.click(0, 10)
    if not a.await_samples("carter_march", 2):
        return False
    return True

def speedup(a):
    if a.await_samples("carter_march", 2):
        a.click(190, 8)
        if not a.await_samples("speedup", 2):
            return True
        for _ in range(6):
            a.click(360, 36)
        time.sleep(2)
        return True
    return False

a = Automator()
fails = 0
last_restart = time.time()
while True:
    if fails >= 10 or time.time() > last_restart + 900:
        a.restart_game(True)
        last_restart = time.time()
        fails = 0
    if not speedup(a):
        if crypt(a):
            fails = 0
        else:
            fails += 1
