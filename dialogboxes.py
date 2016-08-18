import pygame
from pygame.locals import *

pygame.font.init()

BASICFONT = pygame.font.Font('freesansbold.ttf', 16)

WHITE = (255, 255, 255)
BLACK = (  0,   0,   0)
GREY  = (143, 143, 143)

OFFSET = 4 #pixels

class Sign(object):
    """
    SIGN
    Window displayed when the player reads a sign in the overworld.  Contains the message
    """
    def __init__(self, message, width=0, height=0):
        self.message = message
        self.width = width
        self.height = height
        
        
        self.sign_surface = self.build()
        self.sign_rect = self.sign_surface.get_rect()
        
    def draw(self, surface, position = (0,0)):
        surface.blit(self.sign_surface, position)
        
    def build(self):
        """
        Builds the visual representation of the sign
        
        :rtype: sign_surface PyGame Surface
        """
        message_surface = BASICFONT.render(self.message, True, WHITE)
        message_rect = message_surface.get_rect()
        
        sign_surface = pygame.Surface((self.width, self.height))
        sign_surface.fill(BLACK)
        
        grey_rect = pygame.Surface((self.width-2*OFFSET, self.height-2*OFFSET))
        grey_rect.fill(GREY)
        
        sign_surface.blit(grey_rect, (OFFSET, OFFSET))
        
        message_rect.center = (self.width//2, self.height//2)
        
        sign_surface.blit(message_surface, message_rect.topleft)
        
        return sign_surface
        