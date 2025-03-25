import pyautogui
from imutils.object_detection import non_max_suppression
import pytesseract
import cv2
import numpy
import mss
import os
import time
import math
import random

class Automator:
    def __init__(self, scale = 1, threshold = 0.051, kill_file = os.path.expanduser("~/.tba_stop")):
        self.kill_file = kill_file
        if os.path.exists(kill_file):
            os.remove(kill_file)
        self.scale = scale
        self.threshold = threshold / scale
        self.method = cv2.TM_SQDIFF_NORMED
        self.samples = dict()
        self.image = None
        self.loc = None
        self.multi = None

    def get_sample(self, name):
        t = (name, self.scale)
        if t in self.samples:
            return self.samples[t]
        sample = cv2.imread(os.path.dirname(__file__) + "/samples/" + name + ".png")
        sample = cv2.resize(sample, (0, 0), fx = self.scale, fy = self.scale)
        self.samples[t] = sample
        return sample

    def find(self, sample, threshold = None, set_loc = True):
        template = self.get_sample(sample)
        if set_loc:
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
            loc = ((loc[0] + w / 2) / self.scale, (loc[1] + h / 2) / self.scale)
            if set_loc:
                self.loc = loc
            return loc
        return None

    def find_multi(self, sample, threshold = None):
        template = self.get_sample(sample)
        self.multi = None
        result = cv2.matchTemplate(self.image, template, self.method)
        if threshold is None:
            threshold = self.threshold
        if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            ys, xs = numpy.where(result < threshold)
        else:
            ys, xs = numpy.where(result > threshold)
        rects = []
        for x, y in zip(xs, ys):
            rects.append((x, y, x + template.shape[:2][1], y + template.shape[:2][0]))
        h, w, _ = template.shape
        self.multi = [((loc[0] + w / 2) / self.scale, (loc[1] + h / 2) / self.scale) for loc in non_max_suppression(numpy.array(rects))]
        if self.multi:
            return self.multi
        return None

    def multi_block_color(self, width, height, color):
        multi = []
        for loc in self.multi:
            min_x = loc[0] - width // 2
            max_x = loc[0] + (width + 1) // 2
            min_y = loc[1] - height // 2
            max_y = loc[1] + (height + 1) // 2
            cutout = self.image[int(min_y):int(max_y), int(min_x):int(max_x)]
            keep = True
            for row in cutout:
                for pixel in row:
                    if (int(pixel[2]), int(pixel[1]), int(pixel[0])) == color:
                        keep = False
                        break
                if not keep:
                    break
            if keep:
                multi.append(loc)
        self.multi = multi
        return bool(self.multi)

    def random_multi(self):
        if self.multi:
            self.loc = random.choice(self.multi)
            return self.loc
        return None

    def central_multi(self):
        h, w, _ = self.image.shape
        best_loc = None
        best_dist = None
        for loc in self.multi:
            dist = math.sqrt((loc[0] / self.scale - w / 2) ** 2 + (loc[1] / self.scale - h / 2) ** 2)
            if best_loc is None or dist < best_dist:
                best_loc = loc
                best_dist = dist
        self.loc = best_loc
        return best_loc

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

    def await_samples_multi(self, samples, timeout = None):
        if not isinstance(samples, list):
            samples = [samples]
        def f(a):
            for sample in samples:
                locs = a.find_multi(sample)
                if locs is not None:
                    return locs
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
            if not self.await_samples("logo", 2):
                return False
            self.move()
        return True
