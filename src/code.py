#!/usr/bin/env python3
# (c) 2023 Andriy Kolisnyk andreyk72@yahoo.com
# Drift Lights project - CirquitPython code for PIMORONI TINY RP2040 Board
# Analyses RC car throttle signal and does 3 goups of leds management, for Head Light, Brake Light and Marker Light
# The leds are driven by external N-Channel MOSFET Driver
# Requires external library adafruit_intertool to be put to the /lib folder on the device
#

import board
import pwmio
import digitalio
import time
from adafruit_itertools import chain, cycle, repeat
#from adafruit_motor import servo
import pulseio
#from enum import Enum
import keypad



#th_sim = pwmio.PWMOut(board.GP6, frequency = 333)  # throttle  signal simulation
#servo = servo.Servo(th_sim)






class RunMode:
    Off = 1
    FailSafe = 2
    Parked = 3
    Accelerate = 4
    Brake = 5
    Reverse = 6
    Forward = 7
    seq = {Off: "Off", FailSafe: "FailSafe", Parked : "Parked",
       Accelerate: "Accelerate", Brake: "Brake", Reverse: "Reverse", Forward: "Forward"}
    def __init__(self):
        self.iterator = iter(RunMode.seq)
    def __iter__(self):
        return self.iterator

class LedType:
    HeadLight = 1
    BrakeLight = 2
    MarkerLight = 3
    Test = 4
    seq = {HeadLight: "HeadLight", BrakeLight: "BrakeLight",
        MarkerLight: "MarkerLight", Test: "Test"}
#
#

# invert counters!! 0 is full brightness!
c_min_value = 0  # min pwm value - min brightness
c_marker_value = 16384 # marker light default value
brake_marker_value  =  int(c_marker_value / 2.0)
c_max_value = 65535  # max pwm value - full brightness
c_period = 6553 #13106  # 0.5 seconds

raice_range = range(c_min_value, c_max_value , c_period)
marker_range = range(c_marker_value, c_max_value, c_period)
brake_marker_range = range(brake_marker_value, c_max_value, c_period)
accelerate_range = range(c_marker_value, c_max_value, c_period)

test_range = range(0,65500,327) # 20 sec period



def get_led_config(led_type, run_mode):
    # two dimensional dictionary matrix containing iterators for each light type and run mode

    led_config = { LedType.HeadLight:
               {RunMode.Off: repeat(c_min_value),
                RunMode.FailSafe: cycle(chain(raice_range, repeat(c_max_value, 3), reversed(raice_range), repeat(c_min_value, 3))),
                RunMode.Parked: repeat(c_min_value),
                RunMode.Accelerate: chain(accelerate_range, repeat(c_max_value)),
                RunMode.Brake: repeat(brake_marker_value),
                RunMode.Reverse: repeat(brake_marker_value),
                RunMode.Forward: repeat(c_marker_value)
                },
               LedType.BrakeLight:
               {
                 RunMode.Off: repeat(c_min_value),
                 RunMode.FailSafe: cycle(chain(raice_range, repeat(c_max_value, 3), reversed(raice_range), repeat(c_min_value, 3))) ,
                 RunMode.Parked: repeat(brake_marker_value),
                 RunMode.Accelerate: repeat(brake_marker_value),
                 RunMode.Brake: chain(brake_marker_range, repeat(c_max_value, 3), reversed(brake_marker_range)),
                 RunMode.Reverse: cycle(chain(repeat(c_max_value, 4), repeat(c_min_value, 4))),
                 RunMode.Forward: repeat(brake_marker_value)
               },
               LedType.MarkerLight:
               {
                   RunMode.Off: repeat(c_min_value),
                   RunMode.FailSafe: cycle(chain(raice_range, repeat(c_max_value, 3), reversed(raice_range), repeat(c_min_value, 3))) ,
                   RunMode.Parked: repeat(c_marker_value),
                   RunMode.Accelerate: repeat(c_marker_value),
                   RunMode.Brake: repeat(c_marker_value),
                   RunMode.Reverse: repeat(c_marker_value),
                   RunMode.Forward: repeat(c_marker_value)
               },
               LedType.Test:
                {
                   RunMode.Off: cycle(chain(test_range, reversed(test_range))),
                   RunMode.FailSafe: repeat(16384),
                   RunMode.Parked: repeat(8192),
                   RunMode.Accelerate: repeat(65535),
                   RunMode.Brake: repeat(48000),
                   RunMode.Reverse: repeat(32768),
                   RunMode.Forward: repeat(4096)
                }

    } # led_config
    return led_config[led_type][run_mode]

class LedRenderer:
    def __init__(self, board_pin, led_type):
        self.led_pin  = pwmio.PWMOut(board_pin, frequency = 100)
        self.iterator = repeat(c_min_value)
        self.run_mode = RunMode.Off
        self.led_type = led_type
        self.cur_value = 0


    def __iter__(self):
        return self.iterator
    def __next__(self):
        self.led_pin.duty_cycle = next(self.iterator)
        self.cur_value = self.led_pin.duty_cycle
        return self.led_pin.duty_cycle
    def set_mode(self, mode):
        if self.run_mode == mode:
           return
        self.run_mode = mode
        #transcient switch implementation
        it = get_led_config(self.led_type, mode)
        target = next(it)
        step = int((target - self.cur_value)/ 5.0) # half a second transition
        if step == 0 : # the difference is too small
            self.iterator = chain(repeat(target, 1) , it)
        else:
            self.iterator = chain(range(self.cur_value, target, step), it)
        print("LedRenderer.set_mode:", self)
    def __str__(self):
        return f"LedType:{LedType.seq[self.led_type]}; RunMode:{RunMode.seq[self.run_mode]}; DutyCycle:{self.led_pin.duty_cycle};"






led_array = [LedRenderer(board.GP6, LedType.HeadLight),
            LedRenderer(board.GP4, LedType.MarkerLight),
             LedRenderer(board.GP5, LedType.BrakeLight)]




print(board.board_id)


sleep = 0.05 # 10 times per second main cycle

#angle_range = range(90,180)  # from 90 to 180 degrees, imitate positive throttle (0-90 is brake force)
#angle_iter = cycle(chain(angle_range, reversed(angle_range)))

keys = keypad.Keys((board.USER_SW, ), value_when_pressed = False, pull = False)

run_mode = RunMode()
mode_iter = cycle(run_mode)
#cur_mode = RunMode.Off
while True:
    m = next(mode_iter)
    print("InitMode:", m)
    if m == RunMode.Off:
        break

def set_led_mode(mode):
    for l in led_array:
        l.set_mode(mode)
        #print(l)

def get_led_mode():
    return led_array[0].run_mode

def check_mode():
    global cur_mode, mode_iter
    event = keys.events.get()
    if event:
        if event.released:
#            cur_mode = next(mode_iter)
#            set_led_mode(cur_mode)
            print("Key released, Runmode {} activated.".format(RunMode.seq[cur_mode]))



ticks = 11
debug_ticks = ticks

def debug_leds():
    global debug_ticks
    debug_ticks = debug_ticks - 1
    if debug_ticks == 0:
        for l in led_array:
            print(l)
        print('\n')
        debug_ticks = ticks





#pwm in
th_size = 14
th_read = pulseio.PulseIn(board.GP7, maxlen = th_size, idle_state = True)  # throttle signal reading is here
parking_count = 0
failsafe_count = 0
failsafe_threshold = 30 # no signal in 1.5 sec -> failsafe
filtered = []
read_error = 0
th_threshold = 5

prev_avg = 0.0

###
### Main Loop
###
while True:
    time.sleep(sleep)

    #check_mode()

# render leds
    for led in led_array:
        try:
            next(led)
        except StopIteration:
            # Only Brake Light is allowed to be excepted, means we stopped brake and continue acceleration
            if led.led_type == LedType.BrakeLight:
                set_led_mode(RunMode.Forward)

#    debug_leds()
    #print(debug_ticks)
        # servo signal simulator
#    servo.angle = next(angle_iter)


# read pulses
    th_read.resume()

    if len(th_read) < th_size:
        failsafe_count += 1
        if failsafe_count > failsafe_threshold:
            set_led_mode(RunMode.FailSafe)
            failsafe_count = 0
    else:
        th_read.pause()
        failsafe_count = 0
        raise_count = 0
        fall_count = 0
        deadband = 5
        average = 0.0

        for x in range(th_size):
            if th_read[x] < 2005 and th_read[x] > 990:
                filtered.append(th_read[x])

        #print("Filtered size:", len(filtered))
        if(len(filtered) > 3): ## bad reception or corrupted signal detection, too low count of values in working range
            # remove min and max values
            filtered.remove(max(filtered)) # remves only first found occurance, not all of them!
            filtered.remove(min(filtered))
            for f in filtered:
                average = average + (f / len(filtered))
            if prev_avg == 0.0: # initial
                prev_avg = average
            if average < 1500 - deadband: # reverse riding
                set_led_mode(RunMode.Reverse)
            if average > 1500+deadband: # forward movement
                if  average  > prev_avg + th_threshold:
                    print("Acceleration detected.", " average:", average,  " prev_avg:", prev_avg)
                    set_led_mode(RunMode.Accelerate)
                elif (average < prev_avg + th_threshold) and  (average > prev_avg - th_threshold):
                    set_led_mode(RunMode.Forward)
                    print("Forward detected.", " average:", average,  " prev_avg:", prev_avg)
                elif average < prev_avg - th_threshold:
                    print("Brake detected.", " average:", average,  " prev_avg:", prev_avg)
                    set_led_mode(RunMode.Brake)
            if (average < (1500 + deadband)) and (average  > (1500 - deadband)):  # zero throttle
               parking_count = parking_count + 1
               if parking_count > 60: # zero throttle more than 3 sec
                    parking_count = 0
                    set_led_mode(RunMode.Parked)
                    print("Parking mode is detected")
            if get_led_mode() == RunMode.FailSafe: # we've got a throttle signal however leds are still in failsafe
                set_led_mode(RunMode.Parked)
            prev_avg = average
            #debug
            event = keys.events.get()
            if event:
                if event.released:
                   print("Keypress debug: th_read size:", len(filtered), "average:", average)
                   for k in range(len(filtered)):
                       print ("[{}] = {}".format(k, filtered[k]))
                   for l in led_array:
                      print("Debug:", l)


        else:
            read_error += 1
            if read_error > 10:
                print("Read Error threshold, switch to failsafe")
                set_led_mode(RunMode.FailSafe)
                read_error = 0

        th_read.clear()
        filtered.clear()
    # end of else
