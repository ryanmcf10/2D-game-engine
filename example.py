#! /usr/bin/python3.5

"""
EXAMPLE USE OF MY 2D GAME ENGINE
Uses maps, npc info, and sprite sheets from the '/data' folder


Requires Python 3+, PyGame, PyTMX, PyScroll
"""

import pygame
from pygame.locals import *

import overworld

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

STARTING_MAP = 'map1.tmx'

def main():
    #initialize pygame create a display window, create the game clock
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    GAMECLOCK = pygame.time.Clock()
    
    #load the starting map as the first overworld
    GAME = overworld.Overworld(STARTING_MAP, screensize=DISPLAYSURF.get_size())
    dt = .01
    
    while True:      
        
        #get events (keys used for movement, events used for all other events)
        keys = pygame.key.get_pressed()
        events =  pygame.event.get()
                    
        #handle the events in the event queue
        for event in events:
            GAME.handle_interaction(event)

        #handle movement based on the keys map1
        GAME.handle_movement(keys)
        
        #update the map, draw it to a surface, and display it on the display window
        GAME.update(dt)
        GAME.draw(DISPLAYSURF)
        pygame.display.flip()
        
        #tick the game clock
        dt = GAMECLOCK.tick()/1000.
        
        #get the current FPS and set it as the caption
        fps = GAMECLOCK.get_fps()
        pygame.display.set_caption('Test: ' + str(fps))
    
if __name__ == '__main__':
    main()
        