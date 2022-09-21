#!/usr/bin/env python3.7

import board
import neopixel
import time
from math import sin, cos, tan, pi

class Pixels:

    BLACK   = (  0,   0,   0)
    RED     = (255,   0,   0)
    GREEN   = (  0, 255,   0)
    BLUE    = (  0,   0, 255)
    YELLOW  = (255, 255,   0)
    MAGENTA = (255,   0, 255)
    CYAN    = (  0, 255, 255)
    WHITE   = (255, 255, 255)

    def __init__(self):
        self.pixels = neopixel.NeoPixel(board.D18, 150, brightness=1)

    def length(self):
        return self.pixels.n

    def set_pixel(self, r, g, b, i):
        self.pixels[i] = ((r, b, g))

    def set_all_pixels(self, r, g, b):
        self.pixels.fill((r, b, g))

    def get_pixel(self, i):
        return self.pixels[i]

    def show(self):
        self.pixels.show()

    def shutdown(self):
        self.pixels.deinit()

if __name__ == "__main__":
    try:
        pixels = Pixels()
        
        while True:
            time.sleep(0.05)
            x = time.time()
            color = (
                int(127.5 * (1 + sin(x))), 
                int(127.5 * (1 + sin(x + 2 * pi / 3))), 
                int(127.5 * (1 + sin(x + 4 * pi / 3)))
            )
            pixels.set_all_pixels(*color)
            pixels.show()

    except KeyboardInterrupt:
        pixels.shutdown()
