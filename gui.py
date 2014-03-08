import os
import sys
from ConfigParser import SafeConfigParser

import pygame
from pygame.constants import *

from interface import WindowsInterface


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Workaround for pyinstaller
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


class Text(object):
    def __init__(self, text, size, color, bgcolor, x, y):
        # print "Drawing ", text, ' in size ', size
        # print "In color ", color, ' with background in ', bgcolor
        # print 'In position', x, ', ', y

        fontfile = resource_path(os.path.join('.', 'FreeSansBold.ttf'))

        self.font = pygame.font.Font(fontfile, size)
        self.surface = self.font.render(text, True, color, bgcolor)
        self.rect = self.surface.get_rect()
        self.rect.topleft = x, y


class CommandsGUI(object):
    def __init__(self):
        pygame.init()

        self.inputcfg = SafeConfigParser()
        self.inputcfg.read("input.conf")
        self.n_commands = self.inputcfg.getint("gui", 'commands')

        try:
            txtcolor = self.inputcfg.get('gui', 'text').lower()
            bgcolor = self.inputcfg.get('gui', 'background').lower()
        except:
            print " [X] Could not read colors from input.conf, check your formatting"
            print " [X] Defaulting to white on black"
            txtcolor = 'white'
            bgcolor = 'black'

        self.interface = WindowsInterface(self.inputcfg)

        self.blacklist = [user.lower() for user in self.inputcfg.get('Misc', 'blacklist').split(',')]

        self.txtcolor = BLACK if txtcolor == 'black' else WHITE
        self.bgcolor = BLACK if bgcolor == 'black' else WHITE

        self.processed = []
        self.texts = []

        #TODO: move screen dimensions to config
        self.width, self.height = self.inputcfg.getint('gui', 'width'), self.inputcfg.getint('gui', 'height')
        self.display = pygame.display.set_mode((self.width, self.height), 0, 32)

        self.draw_text()
        self.update()

    def update(self):
        self.display.fill(self.bgcolor)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                accepted_tokens = []

                if event.user.lower() in self.blacklist:
                    print "Rejected command from user %s" % event.user
                    continue

                for token in event.tokens.split():
                    cmd = self.interface.do(token)
                    if cmd:
                        accepted_tokens.append(cmd)
                if accepted_tokens:
                    #Put token on top of queue, remove first one in
                    self.processed.append((event.user, ' '.join(accepted_tokens)))
                    while len(self.processed) > 10:
                        self.processed.pop(0)

        self.draw_text()
        pygame.display.update()

    def draw_text(self):
        text_height = self.height / self.n_commands

        for i, line in enumerate(reversed(self.processed)):
            txt = Text("%s: %s" % line, text_height, self.txtcolor, self.bgcolor,
                       0, self.height - (text_height * (i + 1)))
            self.display.blit(txt.surface, txt.rect)