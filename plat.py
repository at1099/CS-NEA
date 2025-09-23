import pygame
import constants as c

#Plat class used to create platform objects
class Plat():
    def __init__(self, x, y, width, height, colour, passThrough):
        #Attributes
        #x (horizontal) and y (vertical) track poisition of the platform
        self.x = x
        self.y = y
        #width and height store the size of the player so that it can be drawn correctly onto the screen
        self.width = width
        self.height = height
        #colour stores the colour of the platform
        self.colour = colour
        #passThrough stores whether the platform can be passed through or not
        self.passThrough = passThrough
        #collisionbox is used for checking for collisions and drawing the platform
        self.collisionbox = pygame.Rect(x, y, width, height)

    def Update(self):
        #Updates the collisionbox incase the platform has moved or changed size
        self.collisionbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def Draw(self, win):
        #Draws the platform onto the window
        pygame.draw.rect(win, self.colour, self.collisionbox)

