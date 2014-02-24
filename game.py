from ConfigParser import SafeConfigParser
import sys

import pygame
from pygame.constants import *


class Game(object):
    def __init__(self):
        pygame.init()

        self.inputcfg = SafeConfigParser()
        self.inputcfg.read("input.conf")
        #TODO: move screen dimensions to config
        self.display = pygame.display.set_mode((410, 350), 0, 32)

    def update(self):
        self.display.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                print event.user, ': ', event.token
            pygame.display.update()
