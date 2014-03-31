import socket
from ConfigParser import SafeConfigParser
import traceback

import pygame

from gui import CommandsGUI


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
        self.socket = None
        self.readbuffer = ""
        with open('blacklist') as blackfile:
            self.blacklist = blackfile.readlines()

    def connect(self):
        print "Connecting..."
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.setblocking(0)

        print "Sending Connection info"
        self.socket.send("PASS %s\r\n" % self.oauth)  # Send the token before the username, for some reason

        # Send the rest of the login data and join the channel
        self.socket.send("NICK %s\r\n" % self.nickname)
        self.socket.send("USER %s %s :%s\r\n" % (self.ident, self.host, self.real_name))
        self.socket.send("JOIN %s\r\n" % self.channel)

    def consume(self):
        try:
            bytes_in = self.socket.recv(1024)
        except socket.error, e:
            errno, msg = e.args
            if errno != 10035:
                print "Socket error during read: %s" % e
                print " [X] Connection lost, reconnecting"
                self.socket.close()
                self.connect()
        else:
            # print bytes_in,
            if bytes_in == '':
                print " [X] Received empty string, did i lose my connection? Reconnecting"
                self.socket.close()
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
                    self.socket.sendall(answer)
                else:
                    self.consume_line(line)

    def consume_line(self, line):
        prefix, command, args = self.parsemsg(line)
        if command == 'PRIVMSG':
            #Prefix looks like user!user@user.twitch.tv, so grab the firs instance
            if '!' in prefix:
                user = prefix.split('!')[0]
                if user != 'jtv':  # Ignore jtv, he's a jerk
                    tokens = args[1] if len(args) >= 1 else ''
                    if tokens:
                        for blacktoken in self.blacklist:
                            if blacktoken.strip().lower() in tokens:
                                print "Banning user %s for saying %s" % (user, blacktoken)
                                return self.ban(user)
                    self.consume_tokens(user, tokens)
            else:
                print "Invalid prefix %s in line %s" % (prefix, line, )
        elif command == 'PING':
            self.socket.send('PONG %s' % args)
        elif command == "JOIN":
            if args:
                user = prefix.split('!')[0].strip().strip('#')
                for blacktoken in self.blacklist:
                    if blacktoken.strip().lower() in user.lower():
                        print "Banning user %s because it contains %s" % (user, blacktoken)
                        return self.ban(user)  # Breaks the loop

    def consume_tokens(self, user, tokens):
        try:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 1, user=user, tokens=tokens))
        except Exception, e:
            print " [X] Error processing tokens %s: %s" % (tokens, e, )

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

    def ban(self, user):
        self.socket.sendall(".ban %s" % user)


def main():
    # fmt = "%(asctime)s: %(message)s"
    # logging.basicConfig(filename='twitch.log', level=logging.DEBUG, format=fmt)

    config = SafeConfigParser()
    config.read("twitch.conf")

    game = CommandsGUI()

    bot = TwitchIRCBot(config)
    bot.connect()

    while True:
        bot.consume()
        game.update()


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print traceback.format_exc()
        print "Woops, something went wrong, please send me a screenshot of this error up there"
        print "Then press enter to close the program"
        raw_input()
