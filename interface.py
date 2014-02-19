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

    special_commands = {

    }

    def __init__(self, inputcfg):
        self.default_delay = .1
        self.inputcfg = inputcfg

    def do(self, token):

        try:
            command = self.inputcfg.get('Inputs', token)
        except Exception, e:
            return

        if command in self.normal_commands:
            self.send_command(self.normal_commands[command])
        elif len(command) == 1 and ('a' < command < 'z'):
            offset = ord(command) - ord('a')
            self.send_command(0x41 + offset)
        elif len(command) == 1 and ('0' < command < '9'):
            offset = ord(command) - ord('0')
            self.send_command(0x30 + offset)
        elif command in self.special_commands:
            self.special_commands[command]()

    def send_command(self, command, delay=None):
        win32api.keybd_event(command, 0, 0, 0)
        time.sleep(delay if delay else self.default_delay)
        win32api.keybd_event(command, 0, win32con.KEYEVENTF_KEYUP, 0)

