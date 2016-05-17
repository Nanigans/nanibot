import motorctrl
import loggers

LOGGER = loggers.get_logger(__file__, loggers.get_default_level())

###############################################################
#            COMMAND     FUNCTION         
MAPPING  = {'forward'     : motorctrl.forward,
            'f'           : motorctrl.forward,
            'reverse'     : motorctrl.reverse,
            'b'           : motorctrl.reverse,
            'left'        : motorctrl.turn_left,
            'l'           : motorctrl.turn_left,
            'right'       : motorctrl.turn_right,
            'r'           : motorctrl.turn_right,
            'spin'        : motorctrl.spin,
            's'           : motorctrl.spin,    
            'stop'        : motorctrl.stop,
            'x'           : motorctrl.stop,            
            'accelerate'  : motorctrl.accelerate,
            'a'           : motorctrl.accelerate,
            'decelerate'  : motorctrl.decelerate,
            'd'           : motorctrl.decelerate,            
            'help'        : None,
            'h'           : None,
            'quit'        : None,
            'q'           : None}
#           COMMAND      FUNCTION

###############################################################

def can_dispatch(cmd):
    return MAPPING.get(cmd) != None    

###############################################################

def execute(cmd):
    if cmd == 'help' or cmd == 'h':
        LOGGER.info("FUNCTIONS: %s" % ' '.join(MAPPING.keys()))        
    elif cmd == 'quit' or cmd == 'q':
        LOGGER.info("good bye!")
        return False
    else:
        func_info = MAPPING.get(cmd)

        if func_info == None:
            LOGGER.error("Unknown command %s" % cmd)            
        else:
            func = func_info
            if func != None:
                func()
                
    return True