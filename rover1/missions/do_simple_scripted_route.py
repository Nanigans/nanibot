if __name__ == '__main__' and __package__ is None:
  from os import sys, path
  sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

"""
This mission simply executes the canned driving test defined within the sabertooth_adapter module.  

It makes a lot of assumptions about the hardware configuration of the rover.

Under normal, full battery conditions the rover requires freedom of motion in a rectangular box stretching from the front of the rover to 10 feet ahead of it and 3 feet to either side of its starting position.

usage:
sudo python do_simple_scripted_root.py
"""


import peripherals.sabertooth.sabertooth_adapter as sa

spa = sa.SabertoothPacketizedAdapterGPIO()
spa.do_moving_mixed_mode_test()
