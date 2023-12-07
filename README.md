# DriftLights
CirquitPython implementation for RC Drift Car Led Light system based on throttle RC PWM signal analysis. The software can detect such modes as Failsafe (no RC signal or RC reading error), Parked (Zero throttle), Forward, Backward (reverse) car movement, Acceleration and Brake. On each of these mode it can independently control 3 channels of LED lights - Heading Light, Brake Light and Marker Light. All channels support smooth transitions and can be easily programmed to desired light patterns.

The software is designed for Pimoroni Tiny 2040 board, however can be used on another boards on RP2040 processors. The electrical schematics is included in the project. 

The software depends on Adafruit itertools library which must be installed in /lib folder on the flash drive of the board. It is a part of [Adafruit_CircuitPython_Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle#:~:text=Insights-,Adafruit_CircuitPython_Bundle,-Public)

## Installatoin
1. Install CirquitPython on your board. Instruction can be found on Release Notes for the release you selected on the [CirquitPython for Tiny 2040 page](https://circuitpython.org/board/pimoroni_tiny2040/)
2. Download [Adafruit_CircuitPython_Bundle] and unpack it and copy adafruit_itertools folder to /lib on your board flash drive
3. Copy the code.py file to the root of the board flash drive. From this point the program starts woring.

## Debug and Troubleshooting
You can connect serial console via USB serial link to see log messages. You can use MUEditor software that can special editing mode for CirquitPython and built in serial console.
Pressing Boot button will dump some debug information on console, this will allow you to trim/adjust your throttle signal. Works only there's a valid PWM available. Does not work on Failsafe.

