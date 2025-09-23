import pygame

#the values that stay constant throughout the script so that they can eaily be accessed from any script
GRAVITY = 0.6
NORMALCONTACTFORCE = -0.6
FRICTION = 0.25
BG = pygame.image.load("Menu/Background.png")
width = 1382
height = 864
animCooldown = 150
dashCooldown = 2000
isDashingCooldown = 1100
maxSpeed = 6
maxSlowSpeed = 3
acceleration = 1.5