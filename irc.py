import socket
from ConfigParser import SafeConfigParser

#import win32com, win32api, win32con

from time import gmtime, strftime


class TwitchIRCBot(object):
    def __init__(self, config, interface):
        """ Inspired by https://github.com/Abysice/TwitchIRCBot/blob/master/Twitch.py.
        Connects to Twitch IRC on a channel, using the account and oauth token provided."""

        #Config
        self.host = "irc.twitch.tv"
        self.port = 6667
        self.nickname = self.ident = config.get('Twitch', 'account')
        self.oauth = config.get('Twitch', 'oauth')  # use http://twitchapps.com/tmi/ to generate
        self.real_name = config.get('Twitch', 'real_name')  # This doesn't really matter.
        self.channel = "#" + self.nickname.lower()
        self.stop = False
        self.socket = None
        self.interface = interface

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        self.socket.send("PASS %s\r\n" % self.oauth)  # Send the token before the username, for some reason

        # Send the rest of the login data and join the channel
        self.socket.send("NICK %s\r\n" % self.nickname)
        self.socket.send("USER %s %s bla :%s\r\n" % (self.ident, self.host, self.real_name))
        self.socket.send("JOIN %s\r\n" % self.channel)

    def stop(self):
        self.stop = True

    def start_consuming(self):
        readbuffer = ""
        while not self.stop:
            bytes_in = self.socket.recv(16)
            if bytes_in == '':
                raise RuntimeError("Socket connection borken")
            readbuffer += bytes_in
            # Split the buffer into lines
            lines = readbuffer.split('\r\n')
            # Pop leftovers back on the buffer
            if readbuffer.endswith('\r\n'):
                readbuffer = ""
            else:
                readbuffer = lines[-1]
                lines.pop()

            for line in lines:
                if not line:
                    continue
                elif line.startswith('PING'):
                    print "Received ping: %s" % line
                    answer = "PONG%s" % ("".join(line.split("PING")[1:]), )
                    print "Answering %s" % (answer, )
                    self.socket.send(answer)
                else:
                    self.consume_line(line)

    def consume_line(self, line):
        line = self.cleanup_line(line)
        for token in line.split(' '):
            if not token.strip():  # Ignore emptyness
                continue
            self.consume_token(token)

    def cleanup_line(self, line):
        parts = line.split(':')
        effective = "".join(parts[2:])
        return effective

    def consume_token(self, token):
        # If this is something we know about, do it
        if token.lower() in self.interface.commands:
            self.interface.do(token)


class Interface(object):
    def __init__(self):
        self.commands = ["up", "down", "left", "right", "a", "b", "start", "select"]

    def do(self, token):
        method = "cmd_" + token
        try:
            getattr(self, method)()
        except Exception, e:
            print "ERROR EXECUTING COMMAND:"
            print e

    # TODO: implement the actual sending of the command to the game window
    # TODO: move this class to another file
    def cmd_up(self):
        print "PRESSING UP"

    def cmd_down(self):
        print "PRESSING DOWN"

    def cmd_left(self):
        print "PRESSING LEFT"

    def cmd_right(self):
        print "PRESSING RIGHT"

    def cmd_a(self):
        print "PRESSING A"

    def cmd_b(self):
        print "PRESSING B"

    def cmd_start(self):
        print "PRESSING START"

    def cmd_select(self):
        print "PRESSING SELECT"


def main():
    config = SafeConfigParser()
    config.read("twitch.conf")
    bot = TwitchIRCBot(config, Interface())
    bot.connect()
    bot.start_consuming()


if __name__ == "__main__":
    main()
