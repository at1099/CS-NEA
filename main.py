from re import X
import pygame, sys
import os
import math as m
import time
import socket
from pygame.locals import QUIT
from player import Player, OnlineObject, Knight, Archer, Arrow
from button import Button
from plat import Plat
from stack import Stack
import constants as c
from network import Network
import random
#Creates the window which everything is drawn onto
win = pygame.display.set_mode((c.width, c.height),pygame.RESIZABLE)
width = c.width
height = c.height

#Initialises Pygame and captions the window
pygame.init()
pygame.display.set_caption("Client")

#A function to change text into usesable objecys
def ProcessObject(attributeList):
    name = None 
    SP = None
    #This match function is used to compare the first item on each line of the file to find out what type of object needs to be created
    #The rest of the data is then inputted as attributes and the spawn point (SP) is set if the object is a player
    match attributeList[0]: 
        case 'Knight': 
            name = Knight(int(attributeList[1]),int(attributeList[2]),int(attributeList[3]),int(attributeList[4]),(int(attributeList[5]),int(attributeList[6]),int(attributeList[7])))
            SP = (int(attributeList[1]),int(attributeList[2]))
        case 'Archer':
            name = Archer(int(attributeList[1]),int(attributeList[2]),int(attributeList[3]),int(attributeList[4]),(int(attributeList[5]),int(attributeList[6]),int(attributeList[7])))
            SP = (int(attributeList[1]),int(attributeList[2]))
        case 'Platform': 
            name = Plat(int(attributeList[1]),int(attributeList[2]),int(attributeList[3]),int(attributeList[4]),(int(attributeList[5]),int(attributeList[6]),int(attributeList[7])), attributeList[8])
    return name, SP

def LoadLevel(LevelNumber):
    objList = []
    playerSPList = []
    #Opens the text file relating to the selected level
    with open ("Level"+LevelNumber+".txt", "r") as Level:
        #Reads the file data and stores each line as an item in the array Lines
        Lines = Level.readlines()
        #Iterates through each item in Lines and runs ProcessObject() on it to transfer text into objects
        for i in range(len(Lines)):
            Line = str(Lines[i]).split(".")
            newObj, SP = ProcessObject(Line)
            #Adds new objects and data to the correct Array
            playerSPList.append(SP)
            objList.append(newObj)
    return objList, playerSPList

#Used to draw everything onto the screen each frame
def RedrawWindow(playerList, platList, arrowList):
    #Background needs to be redrawn so that the old images are no longer on the screen, the bakcground covers them up
    win.fill("Light Blue")
    #Draws all the platforms on the screen
    for i in range(len(platList)):
        platList[i].Draw(win)
    #Draws any existing arrows onto the screen
    for arrow in arrowList:
        arrow.Draw(win)

    #Draws the current frame for each player on the screen
    for i in range(len(playerList)):
        try:
            #Finds the current frame
            frame = playerList[i].currentAnim[playerList[i].currentFrame]
            #Finds the position to draw it on the screen
            position = (playerList[i].x+playerList[i].imageDisplacement[0],playerList[i].y+playerList[i].imageDisplacement[1])
            #Draws it
            win.blit(frame, position)
        #If there is an issue finding the frame, such as game lag
        except:
            #Resets the player's current frame because most likely the frame number has become to high
            playerList[i].currentFrame = 0
            #Finds the current frame
            frame = playerList[i].currentAnim[playerList[i].currentFrame]
            #Finds the position to draw it on the screen
            position = (playerList[i].x+playerList[i].imageDisplacement[0],playerList[i].y+playerList[i].imageDisplacement[1])
            #Draws it
            win.blit(frame, position)

    #Recreates the scores for each player incase they have changed
    scoreText1 = GetFont(75).render(str(playerList[0].score), True, "Blue")
    scoreRect1 = scoreText1.get_rect(topleft=(300, 50))
    scoreText2 = GetFont(75).render(str(playerList[1].score), True, "Red")
    scoreRect2 = scoreText2.get_rect(topleft=(800, 50))

    #Redraws the scores for each player
    win.blit(scoreText1, scoreRect1)
    win.blit(scoreText2, scoreRect2)

    #Updates the screen
    pygame.display.update()

#Run when the player opens the settings menu
def SettingsMenu(playerList):
    #run is used to stop the while loop if it is set to False
    run = True
    #Creates all of the text and buttons that appear on the screen
    Text1 = pygame.font.Font(None, 100).render("Settings", True, "White")
    Rect1 = Text1.get_rect(midleft=(550, 100))
    p1Button = Button(pygame.image.load("Menu/Play Rect.png"), (300, 400), "Player 1 Keybinds", GetFont(50), "Green", "White")
    p2Button = Button(pygame.image.load("Menu/Play Rect.png"), (1100, 400), "Player 2 Keybinds", GetFont(50), "Green", "White")
    quitButton = Button(pygame.image.load("Menu/Play Rect.png"), (700, 700), "Quit", GetFont(50), "Green", "White")

    while run == True:
        #Keeps a track of the position of the mouse pointer on the screen
        MousePos = pygame.mouse.get_pos()

        #Draws the text and buttons onto the screen
        win.blit(c.BG, (0, 0))
        win.blit(Text1, Rect1)
        for button in [p1Button, p2Button, quitButton]:
            button.Update(win)
            button.ChangeColour(MousePos)
        
        #Uses Pygame's event handler
        for event in pygame.event.get():
            #Checks if left click is pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                #If it is over any of the buttons, it opens the appropriate part of the settings menu
                if p1Button.CheckInput(MousePos):
                    playerList[0].ChangeKeybinds(win, 1)
                elif p2Button.CheckInput(MousePos):
                    playerList[1].ChangeKeybinds(win, 2)

                #Goes back to main menu 
                elif quitButton.CheckInput(MousePos):
                    MainMenu()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False
        #Updates the screen
        pygame.display.update()

#A function used to get the player's keybinds from a file
def GetKeybinds(numLines, player):
    keybindList = []
    #Opens file in read mode
    with open ("Player"+str(player)+"Keybinds.txt", "r") as Keybinds:
        #Stores each line in the file as an item in the array Lines
        Lines = Keybinds.readlines()
        #Iterates through Lines and adds each line to keybindList which will be returned to the Play() gameloop
        for i in range(numLines):
            keybindList.append(int(Lines[i]))
    return keybindList

#Main function for the offline gamemode
def Play(levelNum):
    #Define variables which are used in the gameloop
    clock = pygame.time.Clock()
    arrowList = []
    arrow = None
    run = True
    playerList = []
    platList = []

    #Uses LoadLevel() to turn file data into an array of objects and an array of player spawn points
    objList, playerSPList = LoadLevel(str(levelNum))

    #Iterate through objList and add platforms to platList
    for i in range(len(objList)-2):
        platList.append(objList[i+2])

    #Iterates through players
    for i in range(2):
        #Loads players animations
        objList[i].LoadAnims()
        #Adds players to playerList
        playerList.append(objList[i])
        #Gets keybinds and inputs them to their appropriate place in the dictionary
        keybindList = GetKeybinds(7, i+1)
        playerList[i].Keybinds = {
            "left":keybindList[0],
            "right":keybindList[1],
            "up":keybindList[2],
            "down":keybindList[3],
            "attackLight":keybindList[4],
            "attackHeavy":keybindList[5],
            "dash":keybindList[6]
            }

    #Gameloop
    while run:
        #Sets clock speed to allow the while loop to run 60 times per second (this is so that players dont move faster or slower depending on computing power)
        clock.tick(60)

        #Runs Move() function for each player
        arrow = playerList[0].Move(playerList[1], arrowList)
        arrow = playerList[1].Move(playerList[0], arrowList)

        #Checks if player is dead
        for i in range(2):
            isDead = playerList[i].DeathCheck()
            if i == 0:
                deadPlayer = 0
                alivePlayer = 1
            elif i == 1:
                deadPlayer = 1
                alivePlayer = 0
            #If so it resets the dead player to their spawn point and adds score to the other player
            if isDead:
                playerList[alivePlayer].score += 1
                playerList[deadPlayer].x = playerSPList[deadPlayer][0]
                playerList[deadPlayer].y = playerSPList[deadPlayer][1]
                playerList[deadPlayer].vel_x = 0
                playerList[deadPlayer].vel_y = 0
                isDead = False
                playerList[deadPlayer].damageTaken = 0

            #Runs Gravity(), cooldown and collision checks on each player
            playerList[i].Gravity()
            playerList[i].IsDashingCooldownCheck()
            playerList[i].DashCooldownCheck()
            playerList[i].CanAttackCheck()
            playerList[i].OnGroundCheck(platList)
            playerList[i].HitHead(platList)

        #Uses Pygame event handler to check for actions because the actions below should only be performed once before a cooldown is required
        for event in pygame.event.get():
            #Jump check for each player 
            if event.type == pygame.KEYDOWN and event.key == playerList[0].Keybinds["up"] and playerList[0].numJumps >= 1:
                playerList[0].vel_y = -16
                if playerList[0].vel_x != 0:
                    playerList[0].vel_x += (playerList[0].vel_x)/2
                playerList[0].numJumps -= 1
                playerList[0].isJumping = True
                if not playerList[0].isJumping:
                    playerList[0].currentFrame = 0
            if event.type == pygame.KEYDOWN and event.key == playerList[1].Keybinds["up"]  and playerList[1].numJumps >= 1:
                playerList[1].vel_y = -16
                if playerList[1].vel_x != 0:
                    playerList[1].vel_x += (playerList[1].vel_x)/2
                playerList[1].numJumps -= 1
                playerList[1].isJumping = True
                if not playerList[1].isJumping:
                    playerList[1].currentFrame = 0
            #Dash check for each player
            if event.type == pygame.KEYDOWN and event.key == playerList[0].Keybinds["dash"]:
                playerList[0].DashCooldownCheck()
                if playerList[0].canDash == True:
                    playerList[0].vel_x = 18*playerList[0].currentDir
                    playerList[0].isDashing = True
                    playerList[0].canDash = False
            if event.type == pygame.KEYDOWN and event.key == playerList[1].Keybinds["dash"]:
                playerList[1].DashCooldownCheck()
                if playerList[1].canDash == True:
                    playerList[1].vel_x = 18*playerList[1].currentDir
                    playerList[1].isDashing = True
                    playerList[1].canDash = False
            #Light attack check for each player
            if event.type == pygame.KEYDOWN and event.key == playerList[0].Keybinds["attackLight"] and playerList[0].isLightAttacking == False and playerList[0].isHeavyAttacking == False and playerList[0].canLightAttack == True:
                playerList[0].isLightAttacking = True
                playerList[0].canLightAttack = False
                if not playerList[0].isJumping:
                    playerList[0].currentFrame = 0
                playerList[1].isAttacked = False
            if event.type == pygame.KEYDOWN and event.key == playerList[1].Keybinds["attackLight"] and playerList[1].isLightAttacking == False and playerList[1].isHeavyAttacking == False and playerList[1].canLightAttack == True:
                playerList[1].isLightAttacking = True
                playerList[1].canLightAttack = False
                if not playerList[1].isJumping:
                    playerList[1].currentFrame = 0
                playerList[0].isAttacked = False
            #Heavy attack check for each player
            if event.type == pygame.KEYDOWN and event.key == playerList[0].Keybinds["attackHeavy"] and playerList[0].isLightAttacking == False and playerList[0].isHeavyAttacking == False and playerList[0].canHeavyAttack == True:
                playerList[0].isHeavyAttacking = True
                playerList[0].canHeavyAttack = False
                if not playerList[0].isJumping:
                    playerList[0].currentFrame = 0
                playerList[1].isAttacked = False
            if event.type == pygame.KEYDOWN and event.key == playerList[1].Keybinds["attackHeavy"]  and playerList[1].isLightAttacking == False and playerList[1].isHeavyAttacking == False and playerList[1].canHeavyAttack == True:
                playerList[1].isHeavyAttacking = True
                playerList[1].canHeavyAttack = False
                if not playerList[1].isJumping:
                    playerList[1].currentFrame = 0
                playerList[0].isAttacked = False
            #Check to see if settings menu has been opened
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                SettingsMenu(playerList)
                
        #Runs RedrawWindow() to redraw the screen
        RedrawWindow(playerList, platList, arrowList)

        #Iterates through each arrow in the arrowList
        for i in range(len(arrowList)):
            #Tries to check if the arrow is off the screen or has collided with an enemy player
            try:
                if (arrowList[i].x >= c.width + arrowList[i].width or arrowList[i].x < 0-(arrowList[i].width) or arrowList[i].y > c.height or arrowList[i].y < 0) or (arrowList[i].hasHit):
                    arrowList[i].firedBy.isFiringArrow = False
                    del arrowList[i]
            except:
                continue
        #Applies gravity and movement to each arrow in arrowList
        for arrow in arrowList:
            arrow.Gravity()
            arrow.Move(arrowList)

#Main function for the online gamemode
def PlayOnline(levelNum):
    #Define variables which are used in the gameloop
    clock = pygame.time.Clock()
    arrowList = []
    arrow = None
    run = True
    playerList = []
    platList = []

    #Uses LoadLevel() to turn file data into an array of objects and an array of player spawn points
    objList, playerSPList = LoadLevel(str(levelNum))

    #Iterate through objList and add platforms to platList
    for i in range(len(objList)-2):
        platList.append(objList[i+2])

    #Iterates through players
    for i in range(2):
        #Loads players animations
        objList[i].LoadAnims()
        #Adds players to playerList
        playerList.append(objList[i])
        #Gets keybinds and inputs them to their appropriate place in the dictionary
        keybindList = GetKeybinds(7, i+1)
        playerList[i].Keybinds = {
            "left":keybindList[0],
            "right":keybindList[1],
            "up":keybindList[2],
            "down":keybindList[3],
            "attackLight":keybindList[4],
            "attackHeavy":keybindList[5],
            "dash":keybindList[6]
            }

    #Creates a new socket to use
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #Binds the socket to the same port that the server is broadcasting its IP address and port of game server on
    try:
        udp_socket.bind(('', 37020))
    except:
        #There can be two clients that join so there is a second udp socket incase both clients try to join at the same time
        try:
            udp_socket.bind(('', 37021))
        #If binding to both ports fails (there is already a client connected), client returns to main menu
        except:
            MainMenu()
    
    #Saves data received from server broadcasts
    data, addr = udp_socket.recvfrom(1024)
    #Decodes data so that it is transmitted safely
    serverInfo = data.decode()
    serverIP, serverPort = serverInfo.split(':')
    serverPort = int(serverPort)
    n = Network(serverIP)
    #Defines the default data to be sent, this will be changed later
    data = OnlineObject(300, 300, 0, 0, 1, False, False, False, False, False, False, False, [0,0,0,0,0,0,0,0,0,0], 0)
    #Gameloop
    while run:
        #Sets clock speed to allow the while loop to run 60 times per second (this is so that players dont move faster or slower depending on computing power)
        clock.tick(60)

        #Sets the current player and otherPlayer, this allows the program to know which player the user can control and which player's data to send to the server
        if data.player == 0:
            data.player = 1
            player = data.player
            otherPlayer = 0

        elif data.player == 1:
            data.player = 0
            player = data.player
            otherPlayer = 1

        #Uses the makObject function to make an OnlineObject to send to hold the data that is sent to the server using the .send() function
        data = n.Send(playerList[player].MakeObject(player, playerList[otherPlayer]))

        #Tries to update the other player in the current scene
        try:
            arrow = data.UpdateObject(playerList[otherPlayer], arrowList, playerList[player])
        #For the except statement to occur, there must have been an error with receiving data such as the other client leaving 
        except:
            MainMenu()

        #Moves the active player on this client
        arrow = playerList[player].Move(playerList[otherPlayer], arrowList)
        #Checks if the other player has been attacked
        playerList[otherPlayer].CheckAttacked(playerList[player], arrowList)
        #Checks if the active player is dead
        isDead = playerList[player].DeathCheck()
        #If true then the other player has score added and the dead player has coordinates reset
        if isDead:
            playerList[otherPlayer].score += 1
            playerList[player].x = playerSPList[player][0]
            playerList[player].y = playerSPList[player][1]
            playerList[player].vel_x = 0
            playerList[player].vel_y = 0
            playerList[player].damageTaken = 0
            isDead = False

        #Runs Gravity(), cooldown and collision checks on each player
        for i in range(2):
            playerList[i].Gravity()
            playerList[i].IsDashingCooldownCheck()
            playerList[i].DashCooldownCheck()
            playerList[i].CanAttackCheck()
            playerList[i].OnGroundCheck(platList)
            playerList[i].HitHead(platList)

        #Uses Pygame event handler to check for actions because the actions below should only be performed once before a cooldown is required
        for event in pygame.event.get():
            #Jump check for active player
            if event.type == pygame.KEYDOWN and event.key == playerList[player].Keybinds["up"] and playerList[player].numJumps >= 1:
                playerList[player].vel_y = -16
                if playerList[player].vel_x != 0:
                    playerList[player].vel_x += (playerList[player].vel_x)/2
                playerList[player].numJumps -= 1
                playerList[player].isJumping = True
                playerList[player].currentFrame = 0
            #Dash check for each player
            if event.type == pygame.KEYDOWN and event.key == playerList[player].Keybinds["dash"]:
                playerList[player].DashCooldownCheck()
                if playerList[player].canDash == True:
                    playerList[player].vel_x = 16*playerList[player].currentDir
                    playerList[player].isDashing = True
                    playerList[player].canDash = False
            #Light attack check for active player
            if event.type == pygame.KEYDOWN and event.key == playerList[player].Keybinds["attackLight"] and playerList[player].isLightAttacking == False and playerList[player].isHeavyAttacking == False and playerList[player].canLightAttack == True:
                playerList[player].isLightAttacking = True
                playerList[player].canLightAttack = False
                playerList[otherPlayer].isAttacked = False
                if not playerList[player].isJumping:
                    playerList[player].currentFrame = 0
            #Heavy attack check for active player
            if event.type == pygame.KEYDOWN and event.key == playerList[player].Keybinds["attackHeavy"] and playerList[player].isLightAttacking == False and playerList[player].isHeavyAttacking == False and playerList[player].canHeavyAttack == True:
                playerList[player].isHeavyAttacking = True
                playerList[player].canHeavyAttack = False
                playerList[otherPlayer].isAttacked = False
                if not playerList[player].isJumping:
                    playerList[player].currentFrame = 0

            #Takes user to settings menu if escape key is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                SettingsMenu(playerList)
        #Runs RedrawWindow()
        RedrawWindow(playerList, platList, arrowList)

        #Iterates through each arrow in the arrowList
        for i in range(len(arrowList)):
            #Tries to check if the arrow is off the screen or has collided with an enemy player
            if (arrowList[i].x >= c.width + arrowList[i].width or arrowList[i].x < 0-(arrowList[i].width) or arrowList[i].y > c.height or arrowList[i].y < 0) or (arrowList[i].hasHit):
                arrowList[i].firedBy.isFiringArrow = False
                del arrowList[i]
        #Applies gravity and movement to each arrow in arrowList
        for arrow in arrowList:
            arrow.Gravity()
            arrow.Move(arrowList)

        
def LevelSelect(numList, mode):
    #Initialising variables used to draw text and create buttons to be drawn on the screen
    levelList = []
    halfLen = len(numList)//2
    Text1 = GetFont(75).render("Select one of the saved levels to play:", True, "White")
    Rect1 = Text1.get_rect(topleft=(75, 150))

    #count used to find out how many levels there are
    count = 1
    count2 = 1

    #Iterates through the first half of the levels and creates buttons for them, this will be the top row on the screen
    for i in range(len(numList)-halfLen):
        levelList.append(Button(None, (100*(count), 300), str(numList[i]), GetFont(75), "Yellow", "Light Blue"))
        count += 1
    #Iterates through the second half of the levels and creates buttons for them, this will be the bottom row on the screen
    for i in range(halfLen):
        levelList.append(Button(None, (100*(count2), 450), str(numList[i+(len(numList)-halfLen)]), GetFont(75), "Yellow", "Light Blue"))
        count2 += 1

    #Loop which runs when in the level selector
    while True:
        #Draws background and text onto the screen
        win.blit(c.BG, (0, 0))
        win.blit(Text1, Rect1)

        #Keeps a track of the position of the mouse pointer on the screen
        MousePos = pygame.mouse.get_pos()

        #Iterates through all the buttons representing each level
        for i in range(len(levelList)):
            #Runs the ChangeColour() and Update() functions on each button
            levelList[i].ChangeColour(MousePos)
            levelList[i].Update(win)

            #Using Pygame's event handler
            for event in pygame.event.get():
                #Iterates through each of the buttons and checks if it has been pressed by the user    
                for i in range(len(levelList)):
                    if event.type == pygame.MOUSEBUTTONDOWN and levelList[i].CheckInput(MousePos):
                        #Runs the correct gameloop depending if the user has selected online or offline and inputs the level number into this function
                        if mode == "offline":
                            Play(numList[i])
                        elif mode == "online":
                            PlayOnline(numList[i])
        #Updates the screen
        pygame.display.update()
    
#Uses built in Pygame function to get the requested font size
def GetFont(size):
    return pygame.font.Font(None, size)

#Function used to save the user's created level to a file
def WriteToFile(Stack, LevelNumber):
    #Checks if the file already exists with data inside and if so, overwrites the old data with new data
    if os.path.exists("Level"+LevelNumber+".txt"):
        os.remove("Level"+LevelNumber+".txt")

    #Sets the default spawn points incase the user hasnt set any
    SPPosList = ["300.200","800.200"]
    #Iterates through Stack
    for i in range(Stack.GetTop()+1):
        #If the type of data in this position in the stack is a spawn point, the program sets the corresponding element in the SPPosList to the value
        if Stack.mode[i] == "SP1":
            SPPosList[0] = ""
            for j in range(2):
                SPPosList[0] += str(Stack.data[i][j])
                if j != 1:
                    SPPosList[0]+= "."            
        if Stack.mode[i] == "SP2":
            SPPosList[1] = ""
            for j in range(2):
                SPPosList[1] += str(Stack.data[i][j])
                if j != 1:
                    SPPosList[1]+= "."

    #Opens the level corresponding with the user's selection
    with open("Level"+LevelNumber+".txt", "a") as Level:
        #Writes the default level data into the file
        Level.write("Knight."+str(SPPosList[0])+".57.60.0.0.255 \n")
        Level.write("Archer."+str(SPPosList[1])+".57.60.0.0.0 \n")
        Level.write("Platform.300.600.700.25.0.255.0.False \n")

    #Iterates through all elements in Stack
    for i in range(Stack.GetTop()+1):
        #Opens the level corresponding with the user's selection
        with open("Level"+LevelNumber+".txt", "a") as Level:
            curLine = Stack.GetData()[i]
            #If the element in Stack is a platform, its data is written into the file
            if Stack.mode[i] == "PLAT":
                for j in range(9):
                    try:
                        Level.write(str(curLine[j]))
                    except:
                        Level.write("None")
                    if j != 8:
                        Level.write(".")
                #Writes a new line
                Level.write("\n")

def AddLevelChoice(LevelElements):
    #Creates all the text that appears on the screen and their Pygame rect objects
    levelList = []
    Text1 = GetFont(75).render("Save the Level you have just created, either:", True, "White")
    Rect1 = Text1.get_rect(topleft=(75, 150))
    Text2 = GetFont(75).render("Replace an existing level save:", True, "White")
    Rect2 = Text1.get_rect(topleft=(75, 250))
    Text3 = GetFont(75).render("Or save your data into a new, empty level:", True, "White")
    Rect3 = Text3.get_rect(topleft=(75, 450))

    #Counts used to keep a track of the number of levels with data in
    count = 1
    count2 = 1

    #Iterates through all possible levels that could have data saved in them
    for i in range(20):
        #Creates the buttons for all levels which already have data
        if os.path.isfile("Level"+str(i+1)+".txt"):
            levelList.append(Button(None, (100*(count), 400), str(i+1), GetFont(75), "Yellow", "Light Blue"))
            count += 1
        #Creates the buttons for all levels which do not have data
        else:
            levelList.append(Button(None, (100*(count2), 600), str(i+1), GetFont(75), "Yellow", "Light Blue"))
            count2 += 1

    #Loops whilst the user is in this menu
    while True:
        #Draws background and text onto screen
        win.blit(c.BG, (0, 0))
        win.blit(Text1, Rect1)
        win.blit(Text2, Rect2)
        win.blit(Text3, Rect3)

        #Keeps track of mouse pointer's position on the screen
        MousePos = pygame.mouse.get_pos()

        #Iterates through all the buttons representing each level
        for i in range(len(levelList)):
            #Runs the ChangeColour() and Update() functions on each button
            levelList[i].ChangeColour(MousePos)
            levelList[i].Update(win)

            #Using Pygame's event handler
            for event in pygame.event.get():   
                #Iterates through each of the buttons and checks if it has been pressed by the user 
                for i in range(len(levelList)):
                    if event.type == pygame.MOUSEBUTTONDOWN and levelList[i].CheckInput(MousePos):
                        #If it has it runs WriteToFile() on the data and takes user to the main menu
                        WriteToFile(LevelElements, str(i+1))
                        MainMenu()
        pygame.display.update()


def LevelEditor():
    #Initialises the variables that will be used to edit the levels
    numClicks = 1
    mode = None
    LevelElements = Stack(15)
    platSelected = False
    platCount = 1
    platList = []
    SPcount = [0,0]
    SP1Selected = False
    SP2Selected = False

    #Creates the big platform at the bottom because this must be in every level and adds it to platList
    bigPlat = Plat(300, 600, 700, 25, (0, 255, 0), True)
    platList.append(bigPlat)

    #Loads the images behind buttons, these are the same images used in the menu and help the user see the buttons more easily
    buttonImage = pygame.image.load("Menu/Play Rect.png")
    #These images are then scaled to the correct size for the screen
    buttonImageScaled = pygame.transform.scale(buttonImage, (buttonImage.get_size()[0]*0.85, buttonImage.get_size()[1]*0.75))
    buttonImage2 = pygame.image.load("Menu/Level Editor Rect.png")
    buttonImage2Scaled = pygame.transform.scale(buttonImage2, (buttonImage2.get_size()[0]*0.78, buttonImage2.get_size()[1]*0.75))
    
    #Creates all the buttons and text for the screen
    LEBack = Button(None, (1230, 70), "BACK", GetFont(75), "Black", "Green")
    PlatformButton = Button(buttonImageScaled, (1180, 700), "PLATFORM", GetFont(75), "Black", "Green")
    spawnPointButtonP1 = Button(buttonImage2Scaled, (270, 700), "SPAWN POINT P1", GetFont(75), "Black", "Green")
    spawnPointButtonP2 = Button(buttonImage2Scaled, (760, 700), "SPAWN POINT P2", GetFont(75), "Black", "Green")
    Instr1Text = GetFont(25).render("LEFT CLICK to select an option", True, "Black")
    Instr1Rect = Instr1Text.get_rect(topleft=(60, 35))
    Instr2Text = GetFont(25).render("SPACE to choose where to place", True, "Black")
    Instr2Rect = Instr2Text.get_rect(topleft=(60, 55))
    Instr3Text = GetFont(25).render("ENTER once youve finished", True, "Black")
    Instr3Rect = Instr3Text.get_rect(topleft=(60, 75))

    #Main loop that repeats whilst the user is in this mode
    while True:
        #Keeps a track of the mouse pointer's current position
        EditMousePos = pygame.mouse.get_pos()

        #Fills the background with light blue and draws all the text onto the screen
        win.fill("Light Blue")
        win.blit(Instr1Text, Instr1Rect)
        win.blit(Instr2Text, Instr2Rect)
        win.blit(Instr3Text, Instr3Rect)

        #Runs ChangeColour() and Update() on each button on the screen
        for button in [LEBack, PlatformButton, spawnPointButtonP1, spawnPointButtonP2]:
            button.ChangeColour(EditMousePos)
            button.Update(win)

        #Using Pygame's events manager
        for event in pygame.event.get():
            #If the user selects the platform button and the user's numClicks is greater than or equal to 1 (does not have anything selected)
            if event.type == pygame.MOUSEBUTTONDOWN and PlatformButton.CheckInput(EditMousePos) and pygame.mouse.get_pressed()[0] and numClicks >= 1 and LevelElements.IsFull != True:
                #numClicks is set to 0 because the user has an item selected
                numClicks = 0
                #The mode (what the user has selected) is set to PLAT and a platform is created so that the user can see where they are putting the platform
                mode = "PLAT"
                plat = Plat(EditMousePos[0], EditMousePos[1], 200, 15, (0, 255, 0), True)
                platList.append(plat)
                #platCount keeps a track of how many platforms are on the screen and platSelected is set to True
                platCount += 1
                platSelected = True

            #If the user selects spawn point 1 button, they have not got anything else selected and there is not already a spawn point 1
            elif event.type == pygame.MOUSEBUTTONDOWN and spawnPointButtonP1.CheckInput(EditMousePos) and pygame.mouse.get_pressed()[0] and numClicks >= 1 and SPcount[0] == 0:
                #numClicks is reset to 0, showing the user has something selected
                numClicks = 0
                #The mode is set to SP1 meaning the user has the spawn point 1 button selected
                mode = "SP1"
                #and the spawn point count is increased by one to make sure multiple spawn points are not created for one character
                SPcount[0] += 1
                SP1Selected = True
                #A rect object is created to represent the spawn point
                SP1 = pygame.Rect(EditMousePos[0], EditMousePos[1], 20, 20)
            
            #If the user selects spawn point 1 button, they have not got anything else selected and there is not already a spawn point
            elif event.type == pygame.MOUSEBUTTONDOWN and spawnPointButtonP2.CheckInput(EditMousePos) and pygame.mouse.get_pressed()[0] and numClicks >= 1 and SPcount[1] == 0:
                #numClicks is reset to 0, showing the user has something selected
                numClicks = 0
                #The mode is set to SP2 meaning the user has the spawn point 2 button selected
                mode = "SP2"
                #and the spawn point count is increased by one to make sure multiple spawn points are not created for one character
                SPcount[1] += 1
                SP2Selected = True
                #A rect object is created to represent the spawn point
                SP2 = pygame.Rect(EditMousePos[0], EditMousePos[1], 20, 20)
                
            #If space is pressed and the current mode is PLAT, the platform should be placed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and numClicks == 0 and mode == "PLAT":
                #The platform is no longer selected
                platSelected = False
                #The platform does not follow the mouse pointer anymore and is locked in place
                curPlatPos = EditMousePos
                #An object for the platform is created and pushed onto the stack
                obj = ["Platform", curPlatPos[0], curPlatPos[1], 200, 15, 0, 255, 0, True]
                LevelElements.Push(obj, mode)
                #numCLicks is reset to 1 so the user can select something else
                numClicks = 1

            #If space is pressed and the current mode is SP1, the spawn point should be placed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and numClicks == 0 and mode == "SP1":
                #The spawn point is no longer selected
                SP1Selected = False
                #The spawn point does not follow the mouse pointer anymore and is locked in place
                curSpawnPos = EditMousePos
                #A tuple is created for the spawn point and pushed onto the stack
                LevelElements.Push(curSpawnPos, mode)
                #numCLicks is reset to 1 so the user can select something else
                numClicks = 1

            #If space is pressed and the current mode is SP2, the spawn point should be placed
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and numClicks == 0 and mode == "SP2":
                #The spawn point is no longer selected
                SP2Selected = False
                #The spawn point does not follow the mouse pointer anymore and is locked in place
                curSpawnPos = EditMousePos
                #A tuple is created for the spawn point and pushed onto the stack
                LevelElements.Push(curSpawnPos, mode)
                #numCLicks is reset to 1 so the user can select something else
                numClicks = 1

            #If r is pressed and the stack is not empty then the last action should be undone
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and LevelElements.GetTop() >= 0:
                #If the element ontop of the stack is a platform the last item in platList is deleted and 1 is subtracted from platCount 
                if LevelElements.mode[LevelElements.GetTop()] == "PLAT":
                    del platList[platCount-1]
                    platCount -= 1
                
                #If the element ontop of the stack is a spawn point 1, SP1 is set to None and there are no spawn point 1s now
                elif LevelElements.mode[LevelElements.GetTop()] == "SP1":
                    SP1 = None
                    SPcount[0] = 0

                #If the element ontop of the stack is a spawn point 2, SP2 is set to None and there are no spawn point 2s now
                elif LevelElements.mode[LevelElements.GetTop()] == "SP2":
                    SP2 = None
                    SPcount[1] = 0

                #The element ontop of the stack is popper off
                LevelElements.Pop()

            #If escape is pressed the user is taken to the main menu
            if event.type == pygame.MOUSEBUTTONDOWN and LEBack.CheckInput(EditMousePos) or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                MainMenu()

            #If the return key is pressed, AddLevelChoice() is run
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                AddLevelChoice(LevelElements)

        #Whilst the user has a platform selected, the platform will follow the user's mouse pointer
        if platSelected == True:
            plat.x = EditMousePos[0]
            plat.y = EditMousePos[1]
            plat.Update()
        
        #Every platform in platList is drawn onto the screen
        for plat in platList:
            plat.Draw(win)

        #Whilst the user has a spawn point selected, the spawn point will follow the user's mouse pointer
        if SPcount[0] == 1:
            if SP1Selected == True:
                SP1 = pygame.Rect(EditMousePos[0], EditMousePos[1], 20, 20)
            #It is then drawn on the screen
            pygame.draw.rect(win, (255, 0, 0), SP1)
        
        #Whilst the user has a spawn point selected, the spawn point will follow the user's mouse pointer
        if SPcount[1] == 1:
            if SP2Selected == True:
                SP2 = pygame.Rect(EditMousePos[0], EditMousePos[1], 20, 20)
            #It is then drawn on the screen
            pygame.draw.rect(win, (0, 0, 255), SP2)

        #The screen is then updated
        pygame.display.update()

def MainMenu():
    pygame.display.set_caption("Menu")

    #The buttons to take the user to each part of the game and title text are then created
    PlayButton = Button(pygame.image.load("Menu/Play Rect.png"), (640, 250), "PLAY LOCAL", GetFont(75), "green", "White")
    PlayOnlineButton = Button(pygame.image.load("Menu/Level Editor Rect.png"), (640, 375), "PLAY ONLINE", GetFont(75), "green", "White")
    LevelEditButton = Button(pygame.image.load("Menu/Level Editor Rect.png"), (640, 500), "EDIT LEVEL", GetFont(75), "green", "White")
    OptionsButton = Button(pygame.image.load("Menu/Options Rect.png"), (640, 625), "OPTIONS", GetFont(75), "green", "White")
    QuitButton = Button(pygame.image.load("Menu/Quit Rect.png"), (640, 750), "QUIT", GetFont(75), "green", "White")
    MenuText = GetFont(100).render("MAIN MENU", True, "#b68f40")
    MenuRect = MenuText.get_rect(center=(640, 100))
    numList = []

    #Loop that tuns whilst the user is in the main menu
    while True:
        #Keeps track of the current position of the user's mouse pointer
        MenuMousePos = pygame.mouse.get_pos()

        #Draws the text and background onto the screen
        win.blit(c.BG, (0, 0))
        win.blit(MenuText, MenuRect)

        #Runs ChangeColour() and Update() on each button in the scene
        for button in [PlayButton, PlayOnlineButton, LevelEditButton, OptionsButton, QuitButton]:
            button.ChangeColour(MenuMousePos)
            button.Update(win)

        #Using Pygame's event handler
        for event in pygame.event.get():
            #If the user presses quit, the program is closed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #If the user presses left click
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
                #If the button selected is the play button, the program checks that a level exists and then runs LevelSelect()
                if PlayButton.CheckInput(MenuMousePos):
                    for i in range(20):
                        if os.path.isfile("Level"+str(i+1)+".txt"):
                            numList.append(i+1)
                    LevelSelect(numList, "offline")

                #If the button selected is the play online button, the program checks that a level exists and then runs LevelSelect() 
                if PlayOnlineButton.CheckInput(MenuMousePos):
                    for i in range(20):
                        if os.path.isfile("Level"+str(i+1)+".txt"):
                            numList.append(i+1)
                    LevelSelect(numList, "online")
                
                #If the button selected is the options button, the program opens the settings menu
                if OptionsButton.CheckInput(MenuMousePos):
                    SettingsMenu(None)

                #If the button selected is the level editor button, the program opens the level editor menu
                if LevelEditButton.CheckInput(MenuMousePos):
                    LevelEditor()
                
                #If the quit button is pressed, the program closes
                if QuitButton.CheckInput(MenuMousePos):
                    pygame.quit()
                    sys.exit()

        #The screen is updated
        pygame.display.update()         

#The MainMenu() is run first to start the program
MainMenu()