This directory contains main executable programs that accomplish specific tasks, or missions.  Only one mission program should be executed at a time.  The launched mission program will launch all subprocesses and threads it requires to accomplish its task. 

E.g., Running simple motor driver test with do_simple_scripted_route.py
1. rover1/missions $ "workon rover1" (activate virtual environment where all necessary packages are installed)
2. power on moter controller (cycle kill switch if it was already on)
3. rover1/missions $ "sudo python do_simple_scripted_route.py" (execute mission program)
