import socket
from ConfigParser import SafeConfigParser

import pygame

from game import Game


class TwitchIRCBot(object):
    def __init__(self, config):
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
        self.readbuffer = ""

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)

        self.socket.send("PASS %s\r\n" % self.oauth)  # Send the token before the username, for some reason

        # Send the rest of the login data and join the channel
        self.socket.send("NICK %s\r\n" % self.nickname)
        self.socket.send("USER %s %s bla :%s\r\n" % (self.ident, self.host, self.real_name))
        self.socket.send("JOIN %s\r\n" % self.channel)

    def stop(self):
        self.stop = True

    def start_consuming(self):
        self.readbuffer = ""
        while not self.stop:
            self.consume()

    def consume(self):
        #TODO: better line parsing
        try:
            bytes_in = self.socket.recv(16)
        except socket.error, e:
            errno, msg = e.args
            if errno != 10035:
                raise
        else:
            # print bytes_in,
            if bytes_in == '':
                self.connect()
            self.readbuffer += bytes_in
            # Split the buffer into lines
            lines = self.readbuffer.split('\r\n')
            # Pop leftovers back on the buffer
            if self.readbuffer.endswith('\r\n'):
                self.readbuffer = ""
            else:
                self.readbuffer = lines[-1]
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
        prefix, command, args = self.parsemsg(line)
        if command == 'PRIVMSG':
            #Prefix looks like user!user@user.twitch.tv, so grab the firs instance
            if '!' in prefix:
                user = prefix.split('!')[0]
                tokens = args[1] if len(args) >= 1 else ''
                for token in tokens.split():
                    self.consume_token(user, token)
            else:
                print "Invalid prefix %s in line %s" % (prefix, line, )
        elif command == 'PING':
            self.socket.send('PONG %s' % args)

    def consume_token(self, user, token):
        try:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, user=user, token=token))
        except Exception, e:
            print "Error processing token %s: %s" % (token, e, )

    def parsemsg(self, s):
        """Breaks a message from an IRC server into its prefix, command, and arguments.
        Shamelessly ripped from twisted's IRC implementation
        """
        prefix = ''
        trailing = []
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
        command = args.pop(0)
        return prefix, command, args


def main():
    config = SafeConfigParser()
    config.read("twitch.conf")

    game = Game()

    bot = TwitchIRCBot(config)
    bot.connect()

    while True:
        bot.consume()
        game.update()


if __name__ == "__main__":
    main()
