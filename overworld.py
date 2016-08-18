import sys
import os.path

import pygame
from pygame.locals import *
from pytmx.util_pygame import load_pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

import json

import character
import dialogboxes

#set up some constants
RESOURCES_DIR = 'data'
ZOOM_LEVEL = 1.5
PLAYER_MOVE_SPEED = 100 #pixels per second
RUN_MULTIPLIER = 2.0 #increases movement speed when holding left shift


# make loading maps a little easier
def get_map(filename):
    return os.path.join(RESOURCES_DIR, 'maps', filename)


class Overworld(object):
    """
    THE OVERWORLD
    
    The main view of the overworld.   Displays the portion of the map that is currently in view and the player character.
    The overworld is responsible for movement of the character and detecting collisions in the overworld.
    
    ATTRIBUTES
    -----------------------------------------------------------------------------------------------------------------------------------
    -filename - name of the tmx map file currently loaded
    -screensize - the size of the pygame window
    
    -map_layer - the portion of the map currently in the viewfinder
    -playercharacter - sprite of the player's character.  contains 'feet' rect used to test for collisions with the world
    -group - pyscroll group containing the map_layer and playercharacter
    
    -moving_up/down/left/right - flags to indicate whether the player is currently moving up/down/left/right
    
    -blockers - list of all rect objects that are blockers to prevent the player from moving into prohibitted areas (walls, trees, etc)
    -portals - list of all rect objects that are portals.  collison with a portal results in a new map being loaded and initialized
    -items - list of all rect objects that are items.  items can be picked up and added to the playercharacter's inventory
    -npcs - list of all npc characters.  can be interacted with, resulting in conversations
    -signs - list of all sign objects. can be interacted with, resulting in message being displayed
    ------------------------------------------------------------------------------------------------------------------------------------
    
    METHODS
    ------------------------------------------------------------------------------------------------------------------------------------
    -draw(surface) - draws the portion of the map currently in view and sprites to a pygame surface
    -update(dt) - updates the position of sprites and map since last called.  called every frame
    -handle_input(keyboard) - responds to keyboard input from the user.  Takes a bitmap of current keystates
    -load_new_map(mapfile) - loads and intitializes a new tmx map into the viewport
    ------------------------------------------------------------------------------------------------------------------------------------
    
    
    """
        
    def __init__(self, mapfile, screensize=(800, 800)):
        self.mapfile = mapfile
        self.filename = get_map(self.mapfile)
        self.tmx_data = load_pygame(self.filename)
        self.screensize = screensize
                
        #lists to hold world objects 
        self.blockers = list()
        self.portals = list()
        self.signs = list()
        self.items = list()
        self.npcs = list()
        self.starting_player_position = None
        
        #populate the world object lists
        self.populate_world()
        
        #create new data source for pyscroll
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        
        #create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screensize)
        self.map_layer.zoom = ZOOM_LEVEL
        
        #find the player layer on the map
        default = 0
        for layer in self.tmx_data.layers:
            if not layer.name == 'Player':
                default += 1
            elif layer.name == 'Player':
                break
                
        #create a pyscroll group.  Set default layer to layer where character will be
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=default)
        
        #create the player to place in the world
        self.playercharacter = character.Character()
        
        #position the player in the center of the map ///// will be changed
        self.playercharacter.position = self.starting_player_position
        
        #add the player to the pyscroll group
        self.group.add(self.playercharacter)
        
        for npc in self.npcs:
            self.group.add(npc)
        
        #flags to control the movement of the player character
        self.moving_up = self.moving_down = self.moving_left = self.moving_right = False
        
        #interaction info
        self.collision_type = None
        self.current_interaction = None
        self.is_interacting = False
        
        self.dialog_box = None
                
        
    def draw(self, surface):
        """
        Draws the current view to the screensize
        
        :param: surface, the main display surface of the game
        """
        #center the map/screen on the player
        self.group.center(self.playercharacter.rect.center)
        
        #draw the map and all sprites
        self.group.draw(surface)
        
        #draw dialog boxes, if any
        if self.is_interacting:
            self.dialog_box.draw(surface, (0, self.screensize[1]-self.dialog_box.height))
   
    #update the position of the sprites, map, etc
    def update(self, dt):
        """
        Update the positions of sprites, the map, etc
        
        :param: dt, the length of time (in seconds) since last updated
        """
        #start or stop the animation of the player character
        if (self.moving_up or self.moving_down or self.moving_left or self.moving_right):
            self.playercharacter.paused = False
            self.playercharacter.move_conductor.play()
        else:
            self.playercharacter.paused = True
            self.playercharacter.move_conductor.pause()
        
        #use pyscroll to update the position of sprites
        self.group.update(dt)
        
        #check if colliding with any world objects
        self.collision_type = self.get_collision_type()
        
        if self.collision_type == None:
            self.is_interacting = False
        elif self.collision_type == 'portal':
            self.load_new_map(self.current_interaction['destination'])
            
            
        if self.playercharacter.feet.collidelist(self.blockers) > -1:
            self.playercharacter.move_back(dt)
            
    
    def handle_movement(self, keyboard):
        """
        handles player movement.
        
        :param: keyboard, list of boolean values representing state of current keys
        """
            
        #run if player is holding LEFT SHIFT
        if keyboard[K_LSHIFT]:
            move_speed = RUN_MULTIPLIER*PLAYER_MOVE_SPEED
        else:
            move_speed = PLAYER_MOVE_SPEED
            
        #player movement (W A S D < ^ > v)
        if (keyboard[K_UP] or keyboard[K_w]) and not self.moving_down:
            self.playercharacter.velocity[1] = -move_speed
            self.moving_up = True
            if not (self.moving_left or self.moving_right):
                self.playercharacter.direction = 'up'
                
        elif (keyboard[K_DOWN] or keyboard[K_s]) and not self.moving_up:
            self.playercharacter.velocity[1] = move_speed
            self.moving_down = True
            if not (self.moving_left or self.moving_right):
                self.playercharacter.direction = 'down'
        else:
            self.playercharacter.velocity[1] = 0
            self.moving_up = self.moving_down = False

            
        if (keyboard[K_LEFT] or keyboard[K_a]) and not self.moving_right:
            self.playercharacter.velocity[0] = -move_speed
            self.moving_left = True
            self.playercharacter.direction = 'left'
            
        elif (keyboard[K_RIGHT] or keyboard[K_d]) and not self.moving_left:
            self.playercharacter.velocity[0] = move_speed
            self.moving_right = True
            self.playercharacter.direction = 'right'
        else:
            self.playercharacter.velocity[0] = 0
            self.moving_left = self.moving_right = False

    
    def handle_interaction(self, event):
        """
        Handle keyboard events other than movement
        
        :param: event
        """
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_SPACE:
                self.interact()

    def load_new_map(self, mapfile):
        """
        Loads a new mapfile.  Resets all overworld attributes
        
        :param: mapfile, a .tmx map file
        """
        #get the new map file and tmx data
        self.mapfile = mapfile
        self.filename = get_map(self.mapfile)
        self.tmx_data = load_pygame(self.filename)
        map_data = pyscroll.data.TiledMapData(self.tmx_data)

        #clear the old world objects and populate the new ones
        self.blockers[:] = []
        self.portals[:] = []
        self.signs[:] = []
        self.items[:] = []
        self.portals[:] = []
        self.populate_world()
        
        #create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screensize)
        self.map_layer.zoom = ZOOM_LEVEL
        
        #find the 'Player' layer on the map. if not found, playercharacter will be drawn on top of everything
        default = 0
        for layer in self.tmx_data.layers:
            if not layer.name == 'Player':
                default += 1
            elif layer.name == 'Player':
                break
        
        #create a pyscroll group.  Set default layer to layer where character will be
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=default)
        
        #position the player in the center of the map ///// will be changed
        self.playercharacter.position = self.starting_player_position
        
        #add the player to the pyscroll group
        self.group.add(self.playercharacter)
        
        #add npcs
        for npc in self.npcs:
            self.group.add(npc)
        
        #reset the movement flags
        self.moving_up = self.moving_down = self.moving_left = self.moving_right = False
        
        #interaction info
        self.collision_type = None
        self.current_interaction = None
        self.is_interacting = False
        
        self.dialog_box = None
        
    #convert objects in the tmx file into game world objects
    def populate_world(self):
        """
        Parse the mapfile and populate the world objects dictionairies
        """
        
        #load the json file containing NPC info for the current map if there is any
        try:
            npc_json_file_name = str(self.mapfile)[:-4]+'_npcs.json'
            npc_json_file_location = os.path.join(RESOURCES_DIR, 'npcs', npc_json_file_name)
            npc_json_file = open(npc_json_file_location)
            npc_json_data = json.load(npc_json_file)
        except:
            pass
        
        for object in self.tmx_data.objects:
            properties = object.__dict__
            position = pygame.Rect(object.x, object.y, object.width, object.height)
            
            #populate the blockers list.  blockers are stored as rects
            if properties['name'] == 'blocker':
                self.blockers.append(position)
                
            #populate the portals list with portals. portals are stored as dictionaries {position:rect, destination:string}
            elif properties['name'] == 'portal':            
                destination = properties['type']
                self.portals.append({'position':position,
                                     'destination':destination})
                
            #populate the signs list with signs.  signs are stored as dictionaries {position:rect, message:string}
            elif properties['name'] == 'sign':
                message = properties['type']
                self.signs.append({'position':position,
                                    'message':message})
                
            #populate the items list with items.  items are stored as dictionaries {position:rect, name:string}
            elif properties['name'] == 'item':
                name = properties['type']
                self.items.append({'position':position,
                                   'name':name})
                
            #populate the npcs list with npcs.  npcs are stored as dictionaries {position:rect, name:string}
            elif properties['name'] == 'npc':
                new_npc = character.NPC(npc_json_data[properties['type']])
                new_npc.position = position
                self.npcs.append(new_npc)
                
            elif properties['name'] == 'player':
                self.starting_player_position = position.center
                
    def interact(self):
        """
        Interact with world objects (read signs / pick up items / talk to NPCs / etc.)
        
        Sets interaction flags
        """
        
        if self.collision_type == 'sign':
            if self.is_interacting == False:
                self.is_interacting = True
                self.dialog_box = dialogboxes.Sign(self.current_interaction['message'], width=self.screensize[0], height=self.screensize[1]//4) 
            else:
                self.is_interacting = False
                
    def get_collision_type(self):
        """
        Check what interactable object the playercharacter is currently colliding with, if any.
        
        :return: collison_type, or None if not colliding with an interactable object
        """
        collision_type = None
        
        for sign in self.signs:
            if self.playercharacter.rect.colliderect(sign['position']):
                self.current_interaction = sign
                collision_type = 'sign'
                break

        for portal in self.portals:
            if self.playercharacter.rect.colliderect(portal['position']):
                self.current_interaction = portal
                collision_type = 'portal'
                break

        for item in self.items:
            if self.playercharacter.rect.colliderect(item['position']):
                self.current_interaction = item
                collision_type = 'item'
                break

                    
        return collision_type
        
        