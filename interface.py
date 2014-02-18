import win32api
import time

import win32con


class WindowsInterface(object):
    #These are not implemented in win32con, because why would they be, right?
    C_KEY = 0x43
    X_KEY = 0x58

    def __init__(self):
        self.commands = ["up", "down", "left", "right", "a", "b", "start", "select"]
        self.delay = .1

    def send_command(self, command):
        win32api.keybd_event(command, 0, 0, 0)
        time.sleep(self.delay)
        win32api.keybd_event(command, 0, win32con.KEYEVENTF_KEYUP, 0)

    def do(self, token):
        method = "cmd_" + token
        try:
            getattr(self, method)()
        except Exception, e:
            print "ERROR EXECUTING COMMAND:"
            print e

    def cmd_up(self):
        print "PRESSING UP"
        self.send_command(win32con.VK_UP)

    def cmd_down(self):
        print "PRESSING DOWN"
        self.send_command(win32con.VK_DOWN)

    def cmd_left(self):
        print "PRESSING LEFT"
        self.send_command(win32con.VK_LEFT)

    def cmd_right(self):
        print "PRESSING RIGHT"
        self.send_command(win32con.VK_RIGHT)

    def cmd_a(self):
        print "PRESSING A"
        self.send_command(self.X_KEY)

    def cmd_b(self):
        print "PRESSING B"
        self.send_command(self.C_KEY)

    def cmd_start(self):
        print "PRESSING START"
        self.send_command(win32con.VK_SPACE)

    def cmd_select(self):
        print "PRESSING SELECT"
        self.send_command(win32con.VK_RETURN)

