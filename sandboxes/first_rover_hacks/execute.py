import commands
import motorctrl

if __name__ == '__main__':
    motorctrl.startup()
    while True:
        message = raw_input('Enter a command to execute: ')
        if commands.execute(message) == False:
            break;
