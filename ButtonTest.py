import pygame
from pygame.locals import QUIT
from button import Button
import constants as c
pygame.init()
win = pygame.display.set_mode((c.width, c.height),pygame.RESIZABLE)
def GetFont(size):
    return pygame.font.Font(None, size)

def LevelSelect():
    button1 = Button(None, (c.width/2, c.height/2), "Button", GetFont(75), "Yellow", "Light Blue")
    print("")
    while True:
        MousePos = pygame.mouse.get_pos()
        button1.Update(win)
        button1.ChangeColour(MousePos)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and button1.CheckInput(MousePos):
                    print("Button pressed! ")
        pygame.display.update()

LevelSelect()