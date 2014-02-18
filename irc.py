import socket
from ConfigParser import SafeConfigParser

from interface import WindowsInterface


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
            print bytes_in,
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

def main():
    config = SafeConfigParser()
    config.read("twitch.conf")

    bot = TwitchIRCBot(config, WindowsInterface())
    bot.connect()
    bot.start_consuming()


if __name__ == "__main__":
    main()
