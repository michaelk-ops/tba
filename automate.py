import pyautogui
import pytesseract
import cv2
import numpy
import mss
import os
import time

class Automator:
    def __init__(self, scale = 1, threshold = 0.052, kill_file = os.path.expanduser("~/.tba_stop")):
        self.kill_file = kill_file
        if os.path.exists(kill_file):
            os.remove(kill_file)
        self.scale = scale
        self.threshold = threshold / scale
        self.method = cv2.TM_SQDIFF_NORMED
        self.samples = dict()
        self.image = None
        self.loc = None

    def get_sample(self, name):
        t = (name, self.scale)
        if t in self.samples:
            return self.samples[t]
        sample = cv2.imread(os.path.dirname(__file__) + "/samples/" + name + ".png")
        sample = cv2.resize(sample, (0, 0), fx = self.scale, fy = self.scale)
        self.samples[t] = sample
        return sample

    def find(self, sample, threshold = None):
        template = self.get_sample(sample)
        self.loc = None
        result = cv2.matchTemplate(self.image, template, self.method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if threshold is None:
            threshold = self.threshold
        if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            condition = min_val < threshold
            loc = min_loc
        else:
            condition = max_val > threshold
            loc = max_loc
        if condition:
            h, w, _ = template.shape
            self.loc = ((loc[0] + w / 2) / self.scale, (loc[1] + h / 2) / self.scale)
            return self.loc
        return None

    def cut(self, min_x, min_y, max_x, max_y, show = True):
        result = self.image[int(self.loc[1] + min_y):int(self.loc[1] + max_y), int(self.loc[0] + min_x):int(self.loc[0] + max_x)]
        if show:
            cv2.imwrite("test.png", result)
        return result

    def read(self, min_x, min_y, max_x, max_y):
        cut = self.cut(min_x, min_y, max_x, max_y, False)
        gray = cv2.cvtColor(cut, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        return pytesseract.image_to_string(threshold, lang = "eng", config = "--psm 7").strip()

    def click(self, xoffset = 0, yoffset = 0):
        pyautogui.click(self.loc[0] + xoffset, self.loc[1] + yoffset)

    def move(self, xoffset = 0, yoffset = 0):
        pyautogui.moveTo(self.loc[0] + xoffset, self.loc[1] + yoffset)

    def write(self, s):
        for c in str(s):
            pyautogui.write(c)
            time.sleep(0.005)

    def update(self):
        with mss.mss() as mss_instance:
            monitor = mss_instance.monitors[1]
            image = mss_instance.grab(monitor)
            image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGRA2BGR)
            image = cv2.resize(image, (0, 0), fx = self.scale, fy = self.scale)
            self.image = image

    def check_kill_file(self):
        if os.path.exists(self.kill_file):
            os.remove(self.kill_file)
            raise Exception("Killfile found")

    def loop(self, f, timeout = None):
        initial = time.time()
        while timeout is None or time.time() <= initial + timeout:
            self.check_kill_file()
            self.update()
            result = f(self)
            if result is not None:
                return result

    def await_samples(self, samples, timeout = None):
        if not isinstance(samples, list):
            samples = [samples]
        def f(a):
            for sample in samples:
                loc = a.find(sample)
                if loc is not None:
                    return loc
            return None
        return self.loop(f, timeout)

    def restart_game(self, worldmap = False):
        pyautogui.press("f5")
        time.sleep(1)
        if not self.await_samples("shop_loaded", 40):
            return False
        pyautogui.press("esc")
        if worldmap:
            if not self.await_samples("map", 3):
                return False
            self.click()
            if not self.await_samples("shop_loaded", 10):
                return False
            pyautogui.press("esc")
        return True
