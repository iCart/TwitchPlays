import win32api
import time

import win32con


class WindowsInterface(object):
    #key: human name, value: win32 virtual key value
    normal_commands = {
        'up': win32con.VK_UP,
        'down': win32con.VK_DOWN,
        'left': win32con.VK_LEFT,
        'right': win32con.VK_RIGHT,
        'enter': win32con.VK_RETURN,
        'space': win32con.VK_SPACE
    }

    special_commands = {}

    def __init__(self, inputcfg):
        self.default_delay = .1
        self.inputcfg = inputcfg
        self.max_delay = self.inputcfg.get('Misc', 'max_delay')
        self.max_delay = float(self.max_delay)

    def do(self, token):

        try:
            if ',' in token:
                token, delay = token.split(',')
                delay = float(delay)
                delay = min(delay, self.max_delay)
            else:
                delay = self.default_delay

            command = self.inputcfg.get('Inputs', token)

        except Exception, e:
            # Ignore non-existing commands
            return

        if command in self.normal_commands:
            self.send_command(self.normal_commands[command], delay)
        elif len(command) == 1 and ('a' <= command <= 'z'):
            offset = ord(command) - ord('a')
            self.send_command(0x41 + offset, delay)
        elif len(command) == 1 and ('0' <= command <= '9'):
            offset = ord(command) - ord('0')
            self.send_command(0x30 + offset, delay)
        elif command in self.special_commands:
            self.special_commands[command]()
        #Dirty workaround: return command to get a cleaned up token in game.py
        return command

    def send_command(self, command, delay=None):

        win32api.keybd_event(0, win32api.MapVirtualKey(command, 0), 0, 0)
        time.sleep(delay if delay else self.default_delay)
        win32api.keybd_event(0, win32api.MapVirtualKey(command, 0), win32con.KEYEVENTF_KEYUP, 0)
