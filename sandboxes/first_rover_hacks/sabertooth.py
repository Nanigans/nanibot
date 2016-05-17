import serial
import loggers
from Tkinter import sys

######################################################################################################
#
# Sabertooth Simplified Serial Mode
# Because Sabertooth controls two motors with one 8 byte character, when operating in Simplified
# Serial mode, each motor has 7 bits of resolution. 
# Sending a character between 1 and 127 will control motor 1. 
# 1 is full reverse, 64 is stop and 127 is full forward. 
# Sending a character between 128 and 255 will control motor 2. 
# 128 is full reverse, 192 is stop and 255 is full forward.
# Character 0 (hex 0x00) is a special case. Sending this character will shut down both motors.
#
######################################################################################################

LOGGER     		= loggers.get_logger(__file__, loggers.get_default_level())
 
conn 			= None			# The serial communication connection object			
speedRange 		= range(0, 65)	# Requests for speed changes to either channel must be in this range

STOPALL_COMMAND = 0 			# This command will stop both motors,

FULLREVERSE_M1  = 1
FULLSTOP_M1		= 64
FULLFORWARD_M1  = 127

FULLREVERSE_M2  = 128
FULLSTOP_M2		= 192
FULLFORWARD_M2  = 255

SPEED_RANGE		= 63

# ===========================================================
			
def _writebyte(val):
	LOGGER.debug(val)
	conn.write(chr(val&0xFF))	

# ===========================================================

# Map x and y (from the joystick GUI) to the proper motor speeds
#     (0, 0) _____________________ (range, 0)
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
# 			|					  |
#           |_____________________|
# (0, range)                       (range, range)
def convertToMotorSpeeds(x, y, range):
	# Positive is forward, negative is backwards
	forwardSpeed = range / 2 - y
	# Positive is right, negative is left
	turnSpeed = (x - range / 2) / float(range / 2)

	m1Speed = FULLSTOP_M1 + round(SPEED_RANGE * forwardSpeed / (range / 2))
	m2Speed = FULLSTOP_M2 + round(SPEED_RANGE * forwardSpeed / (range / 2))
	
	if turnSpeed > 0:
		m2Speed -= round((m2Speed - FULLSTOP_M2) * abs(turnSpeed * 2))
	else:
		m1Speed -= round((m1Speed - FULLSTOP_M1) * abs(turnSpeed * 2))

	# _writebyte(m1Speed)
	# _writebyte(m2Speed)

	return m1Speed, m2Speed

# ===========================================================
# Forward

def forwardM1(speed):
	assert(speed in speedRange)
	_writebyte(min(FULLFORWARD_M1, FULLSTOP_M1 + speed))

def forwardM2(speed):	
	assert(speed in speedRange)
	_writebyte(min(FULLFORWARD_M2, FULLSTOP_M2 + speed))

# ===========================================================
# Reverse

def reverseM1(speed):
	assert(speed in speedRange)
	_writebyte(max(FULLREVERSE_M1, (FULLSTOP_M1 - speed)))

def reverseM2(speed):
	assert(speed in speedRange)		
	_writebyte(min(FULLFORWARD_M2, (FULLSTOP_M2 - speed)))

# ===========================================================
# Stop both motors
# use this when Chalson's navigation algorithms send the rover dangerously close to the Charles River's edge

def STOPALL():
	global STOPALL_COMMAND
	_writebyte(STOPALL_COMMAND)

# ===========================================================
# Open serial connection
		
def startup(comport, rate):
	global conn
	conn = serial.Serial(comport, baudrate=rate)

# ===========================================================
# Close serial connection

def shutdown():
	global conn
	conn.close()

