This project is a python adaption of [PWLP](https://github.com/pixelspark/pwlp) and more details of Tommy's project can be found in [this blog post](https://pixelspark.nl/2021/over-engineering-an-rgb-led-strip-controller-lets-write-a-custom-programming-language-and-instruction-set).


## To run:

```sudo python3.7 server.py```

## Dependencies:

- RPi WS281x (`python3.7 -m pip install rpi_ws281x`)
- Adafruit-CircuitPython-NeoPixel (`python3.7 -m pip install adafruit-circuitpython-neopixel`)

## Notes:
- https://www.youtube.com/watch?v=KJupt2LIjp4


## Todo:

- fix so only one open process is created, rather than many subprocesses