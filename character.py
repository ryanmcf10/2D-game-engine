import os.path
import pygame.sprite
import pyganim

IMAGE_DISPLAY_TIME = 100

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


# make loading images a little easier
def get_image_location(filename):
    return os.path.join('data', 'npcs', 'sprites', filename)


class Character(pygame.sprite.Sprite):
    """
    CHARACTER
    The overworld representation of characters. Contains the characters spritesheet  and position.
    
    -The Player has three rects:
        1) 'rect' - used to draw the sprite at '_position'
        2) 'old_position' - the last position of the player image.  Used in case of collisions
        3) 'feet' - used to test for collisions
   
    -The 'feet' rect is used for collisions, while the 'rect' rect is used for drawing.
    
    -'feet' is 1/2 as wide as the normal 'rect', and 8 pixels tall.  This size
    allows the top of the sprite to overlap walls.

    -There is also an 'old_rect' that is used to reposition the sprite if it
    collides with level walls.
    
    -The 'position' list is used for positioning the sprite
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        sprite_sheet = get_image_location('male_sprite_model.png')
        animation_images = pyganim.getImagesFromSpriteSheet(sprite_sheet, rows=4, cols=8)

        self.image = animation_images[10]
        self.velocity = [0, 0]
        self._position = [0, 0]
        self._old_position = self.position
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * .5, 8)
        
        self.direction = DOWN
        
        #get the individual frames from the character's sprite sheet
        
        #create the animations for walking up/down/left/right.  zips a list of the images in order and the time each image is displayed
        walking_up_images = list(zip([animation_images[2],
                                           animation_images[1],
                                           animation_images[0],
                                           animation_images[2],
                                           animation_images[3],
                                           animation_images[4]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_down_images = list(zip([animation_images[10],
                                            animation_images[9],
                                            animation_images[8],
                                            animation_images[10],
                                            animation_images[11],
                                            animation_images[12]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_right_images = list(zip([animation_images[16],
                                             animation_images[17],
                                             animation_images[18],
                                             animation_images[16],
                                             animation_images[21],
                                             animation_images[22]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_left_images = list(zip([animation_images[24],
                                            animation_images[25],
                                            animation_images[26],
                                            animation_images[24],
                                            animation_images[29],
                                            animation_images[30]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_up_animation = pyganim.PygAnimation(walking_up_images)
        walking_down_animation = pyganim.PygAnimation(walking_down_images)
        walking_left_animation = pyganim.PygAnimation(walking_left_images)
        walking_right_animation = pyganim.PygAnimation(walking_right_images)
        
        self.movement_directions = {UP:walking_up_animation,
                              DOWN:walking_down_animation,
                              LEFT:walking_left_animation,
                              RIGHT:walking_right_animation}
        
        self.move_conductor = pyganim.PygConductor(self.movement_directions)
        self.move_conductor.convert_alpha()
        
        self.paused = True
        
    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    def update(self, dt):
        #update the sprite movement animation
        self.update_animation()
        
        #change the position of the sprite
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self, dt):
        """ 
        If called after an update, the sprite can move back in case of collisions
        """
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        
    def update_animation(self):
        """
        updates the current frame of the sprite animation.  
        if not currently moving, sets the image to standing still facing last direction of movement
        """
        temp_surface = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA, 32)
        temp_surface.convert_alpha()
        
        if not self.paused:
            if self.direction == UP:
                self.movement_directions[UP].blit(temp_surface)
            elif self.direction == DOWN:
                self.movement_directions[DOWN].blit(temp_surface)
            elif self.direction == LEFT:
                self.movement_directions[LEFT].blit(temp_surface)
            elif self.direction == RIGHT:
                self.movement_directions[RIGHT].blit(temp_surface)
        else:
            if self.direction == UP:
                temp_surface.blit(self.movement_directions[UP].getFrame(0), (0, 0))
            elif self.direction == DOWN:
                temp_surface.blit(self.movement_directions[DOWN].getFrame(0), (0, 0))
            elif self.direction == LEFT:
                temp_surface.blit(self.movement_directions[LEFT].getFrame(0), (0, 0))
            elif self.direction == RIGHT:
                temp_surface.blit(self.movement_directions[RIGHT].getFrame(0), (0, 0))
                
        self.image = temp_surface
        
class NPC(pygame.sprite.Sprite):
    """
    CHARACTER
    The overworld representation of characters. Contains the characters spritesheet  and position.
    
    -The Player has three rects:
        1) 'rect' - used to draw the sprite at '_position'
        2) 'old_position' - the last position of the player image.  Used in case of collisions
        3) 'feet' - used to test for collisions
   
    -The 'feet' rect is used for collisions, while the 'rect' rect is used for drawing.
    
    -'feet' is 1/2 as wide as the normal 'rect', and 8 pixels tall.  This size
    allows the top of the sprite to overlap walls.

    -There is also an 'old_rect' that is used to reposition the sprite if it
    collides with level walls.
    
    -The 'position' list is used for positioning the sprite
    """

    def __init__(self, NPC_info):
        """
        initializes a new overworld NPC
        
        :param: NPC_info, dictionary containing all relevant initialization info
        """
        
        assert (type(NPC_info) is dict), "NPC_info must be a dictionary."
        
        pygame.sprite.Sprite.__init__(self)
        
        #set the NPC's name (does not have to be unique)
        self._name = NPC_info['name']
        
        #load sprite sheet
        sprite_sheet = get_image_location(NPC_info['image_src'])
        
        #get individual frames from sprite sheet
        animation_images = pyganim.getImagesFromSpriteSheet(sprite_sheet, rows=4, cols=8)

        #set default image and create collision and position rects
        self.image = animation_images[10]
        self._position = [0, 0]
        self._old_position = self.position
        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * .5, 8)
        
        #set default direction and velocity
        
        try:
            self.direction = NPC_info['direction']
        except:
            self.direction = DOWN
            
        self.velocity = [0, 0]

        
        
        #create the animations for walking up/down/left/right.  zips a list of the images in order and the time each image is displayed
        walking_up_images = list(zip([animation_images[2],
                                           animation_images[1],
                                           animation_images[0],
                                           animation_images[2],
                                           animation_images[3],
                                           animation_images[4]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_down_images = list(zip([animation_images[10],
                                            animation_images[9],
                                            animation_images[8],
                                            animation_images[10],
                                            animation_images[11],
                                            animation_images[12]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_right_images = list(zip([animation_images[16],
                                             animation_images[17],
                                             animation_images[18],
                                             animation_images[16],
                                             animation_images[21],
                                             animation_images[22]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_left_images = list(zip([animation_images[24],
                                            animation_images[25],
                                            animation_images[26],
                                            animation_images[24],
                                            animation_images[29],
                                            animation_images[30]], [IMAGE_DISPLAY_TIME]*6))
        
        walking_up_animation = pyganim.PygAnimation(walking_up_images)
        walking_down_animation = pyganim.PygAnimation(walking_down_images)
        walking_left_animation = pyganim.PygAnimation(walking_left_images)
        walking_right_animation = pyganim.PygAnimation(walking_right_images)
        
        self.movement_directions = {UP:walking_up_animation,
                                    DOWN:walking_down_animation,
                                    LEFT:walking_left_animation,
                                    RIGHT:walking_right_animation}
        
        self.move_conductor = pyganim.PygConductor(self.movement_directions)
        self.move_conductor.convert_alpha()
        
        #initialize movement and animation info
        self.paused = True
        self.moving_up = self.moving_down = self.moving_left = self.moving_right = False
        
        try:
            direction = NPC_info['moving_direction']
            if direction == UP:
                self.moving_up = True
            elif direction == DOWN:
                self.moving_down = True
            elif direction == LEFT:
                self.moving_left = True
            elif direction == RIGHT:
                self.moving_right = True
        except:
            pass
        
        #build list of NPCs dialog lines
        if NPC_info['lines']:
            self.lines = list()
            for line in NPC_info['lines']:
                self.lines.append(line)
        
    @property
    def position(self):
        return list(self._position)

    @position.setter
    def position(self, value):
        self._position = list(value)

    def update(self, dt):
        #update the sprite movement animation
        self.update_animation()
        
        if self.moving_up:
            self.velocity[1] = -100
            self.paused = False
            self.move_conductor.play()
        elif self.moving_down:
            self.velocity[1] = 100
            self.paused = False
            self.move_conductor.play()
        elif self.moving_left:
            self.velocity[0] = -100
            self.paused = False
            self.move_conductor.play()
        elif self.moving_right:
            self.velocity[0] = 100
            self.paused = False
            self.move_conductor.play()
        else:
            self.velocity = [0, 0]
            self.paused = True
            self.move_conductor.pause()
            
        #change the position of the sprite
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = [self._position[0], self._position[1]]
        self.feet.midbottom = self.rect.midbottom

        
    def update_animation(self):
        """
        updates the current frame of the sprite animation.  
        if not currently moving, sets the image to standing still facing last direction of movement
        """
        temp_surface = pygame.Surface((self.image.get_width(), self.image.get_height()), pygame.SRCALPHA, 32)
        temp_surface.convert_alpha()
        
        if not self.paused:
            if self.direction == UP:
                self.movement_directions[UP].blit(temp_surface)
            elif self.direction == DOWN:
                self.movement_directions[DOWN].blit(temp_surface)
            elif self.direction == LEFT:
                self.movement_directions[LEFT].blit(temp_surface)
            elif self.direction == RIGHT:
                self.movement_directions[RIGHT].blit(temp_surface)
        else:
            if self.direction == UP:
                temp_surface.blit(self.movement_directions[UP].getFrame(0), (0, 0))
            elif self.direction == DOWN:
                temp_surface.blit(self.movement_directions[DOWN].getFrame(0), (0, 0))
            elif self.direction == LEFT:
                temp_surface.blit(self.movement_directions[LEFT].getFrame(0), (0, 0))
            elif self.direction == RIGHT:
                temp_surface.blit(self.movement_directions[RIGHT].getFrame(0), (0, 0))
                
        self.image = temp_surface