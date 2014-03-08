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

    def __init__(self, inputcfg):
        self.default_delay = .1
        self.inputcfg = inputcfg
        self.max_delay = self.inputcfg.get('Misc', 'max_delay')
        self.max_delay = float(self.max_delay)
        self.last_start = None

    def do(self, token):
        original = token
        try:
            if ',' in token:
                token, delay = token.split(',')
                delay = float(delay)
                delay = min(delay, self.max_delay)
            else:
                delay = self.default_delay

            #command1+command2 to do them at the same time
            commands = []
            for subcommand in token.split('+'):
                if self.inputcfg.has_option('Inputs', subcommand):
                    commands.append(self.inputcfg.get('Inputs', subcommand))

            if not commands:
                return

        except Exception, e:
            print "An exception happened while treating token %s: %s" % (original, e, )
            return

        inputs = []
        for command in commands:

            if command == self.inputcfg.get('Misc', 'startkey') and not self.check_start():
                continue  # Don't show this to NS, ever - sf
            else:
                print "Generating input: %s" % command

            if command in self.normal_commands:
                inputs.append(self.normal_commands[command])
            elif len(command) == 1 and ('a' <= command <= 'z'):
                offset = ord(command) - ord('a')
                inputs.append(0x41 + offset)
            elif len(command) == 1 and ('0' <= command <= '9'):
                offset = ord(command) - ord('0')
                inputs.append(0x30 + offset)
        self.send_commands(inputs, delay)
        #Dirty workaround: return command to get a cleaned up token in game.py
        return token

    def send_commands(self, commands, delay=None):

        for command in commands:
            win32api.keybd_event(0, win32api.MapVirtualKey(command, 0), 0, 0)

        time.sleep(delay if delay else self.default_delay)

        for command in commands:
            win32api.keybd_event(0, win32api.MapVirtualKey(command, 0), win32con.KEYEVENTF_KEYUP, 0)

    def check_start(self):

        #First time
        if self.last_start is None:
            print "Accepted start command, not going to accept any for another %s seconds" % self.inputcfg.getint(
                'Misc', 'startdelay')
            self.last_start = time.time()
            return True
        #Already pressed some time in the past
        else:
            now = time.time()
            time_difference = now - self.last_start
            print 'td = %s' % time_difference
            if int(time_difference) < self.inputcfg.getint('Misc', 'startdelay'):
                print "Rejected start command because it was already pressed %s seconds ago" % int(time_difference)
                return False
            else:
                print "Accepted start command, not going to accept any for another %s seconds" % self.inputcfg.getint(
                    'Misc', 'startdelay')
                self.last_start = time.time()
                return True
