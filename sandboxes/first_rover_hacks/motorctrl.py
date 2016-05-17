import loggers
import time
import sabertooth

DEVICE     = '/dev/ttyAMA0'
BAUD_RATE  = 2400
LOGGER     = loggers.get_logger(__file__, loggers.get_default_level())
DIRFORWARD = "F"
DIRREVERSE = "R"
RIGHTDIR   = DIRFORWARD
LEFTDIR    = DIRFORWARD
RIGHTSPEED = 0
LEFTSPEED  = 0
MAX_SPEED  = 64
MIN_SPEED  = 0

########################################################

def startup():
    LOGGER.debug("startup")
    LOGGER.debug("sabertooth.Open({0}, {1})".format(DEVICE, BAUD_RATE))    
    sabertooth.startup(DEVICE, BAUD_RATE)    
    return True

########################################################

def shutdown():    
    LOGGER.debug("shutdown")
    sabertooth.shutdown()
    return True

########################################################
# SPEED
########################################################

class speed_and_direction(object):
    def __init__(self, speed_left, direction_left, speed_right, direction_right):
        self.speed_left      = speed_left
        self.speed_right     = speed_right
        self.direction_right = direction_right
        self.direction_left  = direction_left
        
        LOGGER.debug("speed_direction before {0} {1} {2} {3}".format(self.speed_left, self.direction_left, self.speed_right, self.direction_right))
    
    def asJSON(self):
        return {'speed':     {'right': self.speed_right    , 'left': self.speed_left    },
                'direction': {'right': self.direction_right, 'left': self.direction_left}}
            
            

def get_speed_and_direction():
    global RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR
    LOGGER.debug("speed_direction {0} {1} {2} {3}".format(RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR))
    return speed_and_direction(RIGHTSPEED, RIGHTDIR, LEFTSPEED, LEFTDIR)
    

########################################################
# MOVE
########################################################

def reverse_right(speed):
    global RIGHTSPEED, RIGHTDIR
    
    RIGHTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    RIGHTDIR   = DIRREVERSE
    
    LOGGER.debug("reverse_right({0})".format(RIGHTSPEED))
    
    apival = sabertooth.reverseM1(RIGHTSPEED)
    
    LOGGER.debug("sabertooth.backwardM1({0}) == {1}".format(RIGHTSPEED, apival))
    
    return apival
    
########################################################

def reverse_left(speed):
    global LEFTSPEED, LEFTDIR
        
    LEFTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    LEFTDIR   = DIRREVERSE
    
    LOGGER.debug("reverse_left({0})".format(LEFTSPEED))

    apival = sabertooth.reverseM2(LEFTSPEED)
    
    LOGGER.debug("sabertooth.backwardM2({0}) == {1}".format(LEFTSPEED, apival))
    
    return apival

########################################################

def forward_right(speed):
    global RIGHTSPEED, RIGHTDIR
    
    RIGHTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    RIGHTDIR   = DIRFORWARD
    
    LOGGER.debug("forward_right({0})".format(RIGHTSPEED))

    apival = sabertooth.forwardM1(RIGHTSPEED)
    
    LOGGER.debug("sabertooth.forwardM1({0}) == {1}".format(RIGHTSPEED, apival))
    
    return apival

########################################################

def forward_left(speed):
    global LEFTSPEED, LEFTDIR
    
    LEFTSPEED = max(MIN_SPEED, min(MAX_SPEED, speed))
    LEFTDIR   = DIRFORWARD
    
    LOGGER.debug("forward_left({0})".format(LEFTSPEED))

    apival = sabertooth.forwardM2(LEFTSPEED)
    
    LOGGER.debug("sabertooth.forwardM2({0}) {1}".format(LEFTSPEED, apival))
    
    return apival

########################################################

def apply_speed_adjustment():
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    if RIGHTDIR == DIRFORWARD:
        forward_right(RIGHTSPEED)
    else:
        reverse_right(RIGHTSPEED)
    
    if LEFTDIR == DIRFORWARD:
        forward_left(LEFTSPEED)
    else:
        reverse_left(LEFTSPEED)

########################################################
# DIRECTIONAL HELPERS
########################################################

def is_spinning():
    global RIGHTDIR, LEFTDIR
    return RIGHTDIR != LEFTDIR

def is_reverse():
    global RIGHTDIR, LEFTDIR, DIRREVERSE
    return RIGHTDIR == DIRREVERSE and LEFTDIR == DIRREVERSE

def is_forward():
    global RIGHTDIR, LEFTDIR, DIRFORWARD
    return RIGHTDIR == DIRFORWARD and LEFTDIR == DIRFORWARD

def is_turning():
    global RIGHTSPEED, LEFTSPEED
    return RIGHTSPEED != LEFTSPEED

########################################################
# high level APIs
########################################################

def accelerate(amount=1):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    LOGGER.debug("accelerate({0})".format(amount))
    
    RIGHTSPEED = min(MAX_SPEED, RIGHTSPEED + amount)
    LEFTSPEED = min(MAX_SPEED, LEFTSPEED + amount)
    
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def decelerate(amount=1):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    
    LOGGER.debug("decelerate({0})".format(amount))
    
    RIGHTSPEED = max(MIN_SPEED, RIGHTSPEED - amount)
    LEFTSPEED = max(MIN_SPEED, LEFTSPEED - amount)
        
    apply_speed_adjustment()
    return get_speed_and_direction()

########################################################

def forward(amount=1):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    LOGGER.debug("forward")
        
    if is_forward() == False:
        stop()
   
    can_accelerate = is_turning() == False
    
    forward_right(max(RIGHTSPEED, LEFTSPEED))
    forward_left (max(RIGHTSPEED, LEFTSPEED))
    
    if can_accelerate == True:
        accelerate(amount)
    
    return get_speed_and_direction()

########################################################

def reverse(amount=1):
    global RIGHTSPEED, LEFTSPEED, RIGHTDIR, LEFTDIR
    LOGGER.debug("reverse")
    
    if is_reverse() == False:
        stop()
    
    can_accelerate = is_turning() == False
    reverse_right(max(RIGHTSPEED, LEFTSPEED))
    reverse_left (max(RIGHTSPEED, LEFTSPEED))
    
    if can_accelerate == True:
        accelerate(amount)
    
    return get_speed_and_direction()

########################################################

def stop(deceleration=50):
    global RIGHTSPEED, LEFTSPEED
    
    LOGGER.debug("stop({0})".format(deceleration))
    
    while RIGHTSPEED > MIN_SPEED or LEFTSPEED > MIN_SPEED:
        decelerate(deceleration)
        time.sleep(0.5)
    
    return get_speed_and_direction()

def stop_forward(deceleration=50):
    if is_forward():
        stop(MAX_SPEED)

def stop_reverse(deceleration=50):
    if is_reverse():
        stop(MAX_SPEED)

########################################################

def spin(clockwise=True):
    global RIGHTSPEED, LEFTSPEED
    
    LOGGER.debug("spin({0})".format(clockwise))
    
    spin_speed = max(RIGHTSPEED, LEFTSPEED)
    
    if is_spinning() == False:
        stop()
    
    if clockwise == True:
        forward_left (spin_speed)
        reverse_right(spin_speed)        
    else:
        forward_right(spin_speed)
        reverse_left (spin_speed)
    
    return get_speed_and_direction()

########################################################

def turn(sharpness,
         speed1, speed2,
         forward_turn_func,
         forward_turn_faster_func,
         forward_straighten_func,
         reverse_turn_func,
         reverse_turn_faster_func,
         reverse_straighten_func
         ):
    global RIGHTSPEED, LEFTSPEED
    LOGGER.debug("turn({0})".format(sharpness))
    
    if is_forward():
        turn_func        = forward_turn_func
        turn_faster_func = forward_turn_faster_func
        straighten_func  = forward_straighten_func
    else:
        turn_func        = reverse_turn_func
        turn_faster_func = reverse_turn_faster_func
        straighten_func  = reverse_straighten_func
    
    if speed1 == speed2:
        turn_func(max(MIN_SPEED, speed1/sharpness))
    elif speed1 < speed2:
        straighten_func()
        time.sleep(0.3)
        turn_func(max(MIN_SPEED, speed1/sharpness))
    else:
        turn_faster_func(min(MAX_SPEED, int(speed1*1.3)))        
    
    return get_speed_and_direction()

########################################################

def turn_left(sharpness=3):
    return turn(sharpness, RIGHTSPEED, LEFTSPEED, forward_left, forward_right, forward, reverse_left, reverse_right, reverse)    

########################################################

def turn_right(sharpness=3):
    return turn(sharpness, LEFTSPEED, RIGHTSPEED, forward_right, forward_left, forward, reverse_right, reverse_left, reverse)    

    