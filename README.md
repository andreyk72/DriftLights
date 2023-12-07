# DriftLights
CirquitPython implementation for RC Drift Car Led Light system based on throttle RC PWM signal analysis. The software can detect such modes as Failsafe (no RC signal or RC reading error), Parked (Zero throttle), Forward, Backward (reverse) car movement, Acceleration and Brake. On each of these mode it can independently control 3 channels of LED lights - Heading Light, Brake Light and Marker Light. All channels support smooth transitions and can be easily programmed to desired light patterns.

The software is designed for Pimoroni Tiny 2040 board, however can be used on another boards on RP2040 processors. The electrical schematics is included in the project. 

The software depends on Adafruit itertools library which must be installed in /lib folder on the flash drive of the board. It is a part of [Adafruit_CircuitPython_Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle#:~:text=Insights-,Adafruit_CircuitPython_Bundle,-Public)

