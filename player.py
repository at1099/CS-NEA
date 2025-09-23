import pygame
import constants as c
from button import Button

#The arrow class, used to create arrows when a player from the Archer class shoots them
class Arrow():
    def __init__(self, x, y, vel_x, vel_y, direction, firedBy):
        #Attributes 
        #x (horizontal) and y (vertical) track poisition of the arrow
        self.x = x
        self.y = y
        #vel_x (horizontal) and vel_y (vertical) track the current velocity (speed and direction) in each of their planes
        self.vel_x = vel_x
        self.vel_y = vel_y
        #width and height store the size of the arrow so that it can be drawn correctly onto the screen
        self.width = 64
        self.height = 16
        #mass stores the mass of the arrow for use in applying gravity
        self.mass = 0.2
        #hasHit stores whether the arrow has hit an enemy so that it can deal damage and be removed from the screen
        self.hasHit = False
        #The collisionbox is a pygame rect object to use in collision detection
        self.collisionbox = pygame.Rect(x, y+24, 64, 16)
        #firedBy stores the player object of which player fired the arrow
        self.firedBy = firedBy
        #image stores the .png file of the image to be drawn on the screen for the arrow and flippedImage is to use if the arrow is facing the other direction
        self.image = pygame.image.load("Arrow/Arrow.png").convert_alpha()
        self.flippedImage = pygame.transform.flip(self.image, True, False)

    def Update(self):
        #Updates the hitbox so that it can correctly detect collisions
        self.collisionbox = pygame.Rect(self.x, self.y+24, 64, 16)

    def Draw(self, win):
        #Draws the arrow's image onto the screen and finds which way to make it face based on the arrow's velocity
        if self.vel_x > 0:
            win.blit(self.image, (self.x, self.y))
        elif self.vel_x < 0:
            win.blit(self.flippedImage, (self.x, self.y))

    def Move(self, arrowList):
        #Adds the velocity in each direction to the position so that the player moves
        self.x += self.vel_x
        self.y += self.vel_y
        self.Update()

    def Gravity(self):
        #applied gravity to the arrow so that it falls as arrows do in reality
        self.vel_y += c.GRAVITY*self.mass

class Player():
    def __init__(self, x, y, width, height, colour):
        #Attributes 
        #x (horizontal) and y (vertical) track poisition of the player
        self.x = x
        self.y = y
        #width and height store the size of the player so that it can be drawn correctly onto the screen
        self.width = width
        self.height = height
        #vel_x (horizontal) and vel_y (vertical) track the current velocity (speed and direction) in each of their planes
        self.vel_x = 0
        self.vel_y = 0
        #mass stores the mass of the player for use in applying gravity
        self.mass = 1
        #numJumps stores the current amount of times the player can jump
        self.numJumps = 2
        #currentDir stores the direction the player is facing, this is used in applying velocity to enemy players when they are hit
        self.currentDir = 1
        #damageTaken stores the total damage dealt by the other player to the current player since the last time this player was knocked off
        self.damageTaken = 0
        #Stores the total number of times this player has knocked the other player off
        self.score = 0

        #colour determines the team the player is on and the colour of the hitbox if it is drawn
        self.colour = colour
        #keybinds will be a dictionary that links names of the actions (as strings) with the pygame keycode of the current keybind
        self.Keybinds = None

        #These are collisionboxes to detect collisions with different objects in the game in different scenarios
        #collisionbox encompases the whole player and is used for checking if the player is being hit
        self.collisionbox = pygame.Rect(x, y, width, height)
        #footCollisionbox is used for standing on platforms and passing through platforms
        self.footCollisionbox = pygame.Rect(x, y+(height-5), width, 5)
        #headCollisionbox is used for checking if player is hitting head on a platform 
        self.headCollisionbox = pygame.Rect(x, y-5, width, 5)

        #Stores the current platform object the player is on if there is one
        self.currentPlat = None

        #These lastUpdates store the last time (in ms) that the player performed an action to compare with the current time to see if the player can perform the action again
        self.animLastUpdate = pygame.time.get_ticks()
        self.dashLastUpdate = pygame.time.get_ticks()
        self.isDashingLastUpdate = pygame.time.get_ticks()
        self.lightAttackLastUpdate = pygame.time.get_ticks()
        self.heavyAttackLastUpdate = pygame.time.get_ticks()

        #Boolean variables which keep a track of if the player is currently performing certain actions
        self.isAnimating = False
        self.isLightAttacking = False
        self.isHeavyAttacking = False
        self.isHoldingHeavyKey = False
        self.isAttacked = False
        self.canLightAttack = True
        self.canHeavyAttack = True
        self.isGrounded = False
        self.isPassingThrough = False
        self.isDashing = False
        self.canDash = True
        self.isJumping = False

        #These arrays store all of the .png images split up into their individual frames, each as its own element in its array
        self.idleFrames = []
        self.flippedIdleFrames = []
        self.runFrames = []
        self.flippedRunFrames = []
        self.lightAttackFrames = []
        self.heavyAttackFrames = []
        self.flippedLightAttackFrames = []
        self.flippedHeavyAttackFrames = []
        self.jumpFrames = []
        self.flippedJumpFrames = []

        #Stores the current frame that should be drawn on the screen
        self.currentFrame = 0
        #Stores the current animation that should be drawn on the screen
        self.currentAnim = self.idleFrames
        #Stores the current animation as an integer so that is can be transmitted over a server
        self.currentAnimIndex = 0

        #A dictionary which links currentAnimIndex and currentAnim for online play
        self.onlineAnims = {
            0:self.idleFrames,
            1:self.runFrames,
            2:self.lightAttackFrames,
            3:self.heavyAttackFrames,
            4:self.flippedIdleFrames,
            5:self.flippedRunFrames,
            6:self.flippedLightAttackFrames,
            7:self.flippedHeavyAttackFrames,
            8:self.jumpFrames,
            9:self.flippedJumpFrames
        }

    def GetImage(self, frameNum, orientation, sheet, width, height, scale, colour):
        #Uses width and height which are inputted to take the part of the current image which corresponds to the current frame
        image = pygame.Surface((width, height)).convert_alpha()
        #Draws this new image onto its own sheet to seperate it from the rest of the image
        image.blit(sheet, (-5,0), (frameNum*width,0, width, height))
        #Checks the direction the image should be facing to see if it needs to be flipped
        if orientation == "l":
            image = pygame.transform.flip(image, True, False)
        #Scales the image to be the correct size for the screen
        scaledImage = pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale))
        #Removes the background of the image
        scaledImage.set_colorkey(colour)

        return scaledImage

    def ChangeKeybinds(self, win, player):
        #Creates the text and pygame rect object to draw onto the screen
        Text1 = pygame.font.Font(None, 75).render("KeyBindings:", True, "White")
        Rect1 = Text1.get_rect(midleft=(100, 100))
        #buttonSelected keeps a track of whether the player has pressed any button to change their keybinds
        buttonSelected= None
        #Stores whether the while loop should continue running or end
        run = True

        while run == True:
            #keeps a track of the current position of the player's mouse on the screen
            MousePos = pygame.mouse.get_pos()

            #Lists which store the current keybind changing buttons on the screen (these are in the while loop because they could change)
            buttonList = []
            textList = []
            textRectList = []
            #Creates a button and a text object from every item in the keybind array, a text object for the key on the keyboard and a button for the name of the action
            for i in enumerate(self.Keybinds):
                buttonList.append(Button(None, (250, 150+ 75*(i[0]+1)), i[1], pygame.font.Font(None, 75), "Yellow", "Light Blue"))
                textList.append(pygame.font.Font(None, 75).render(str(pygame.key.name(self.Keybinds[i[1]])), True, "Blue"))
                textRectList.append(textList[i[0]].get_rect(midleft=(600, (150+ 75*(i[0]+1)))))

            #Draws the background on the screen
            win.blit(c.BG, (0, 0))
            #Draws all the buttons and text objects onto the screen, along with the title text
            for i in range(len(buttonList)):
                win.blit(textList[i], textRectList[i])
                buttonList[i].ChangeColour(MousePos)
                buttonList[i].Update(win)
            win.blit(Text1, Rect1)

            #Using pygame's event handler
            for event in pygame.event.get():
                #Iterates through the list of all the buttons
                for i in range(len(buttonList)):
                    #Checks if the left mouse button is being pressed and if the mouse position is inside the button's coordinates
                    if event.type == pygame.MOUSEBUTTONDOWN and buttonList[i].CheckInput(MousePos) and pygame.mouse.get_pressed()[0] and buttonSelected == None:
                        buttonSelected = buttonList[i]
                #Checks if a button has been selected and if the user has pressed a key on the keyboard
                if buttonSelected is not None and event.type == pygame.KEYDOWN:
                    #Sets the currently selected action's keybind to the key pressed
                    self.Keybinds[buttonSelected.text_input] = event.key
                    #Writes this key into the file storing the keys
                    with open ("Player"+str(player)+"Keybinds.txt", "w") as Keybinds:
                        for i in self.Keybinds:
                            Keybinds.write(str(self.Keybinds[i])+"\n")
                    buttonSelected = None
                
                #If escape key is pressed user goes back to the settings menu
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False

            #Updates the screen
            pygame.display.update()

    #For testing
    def Draw(self, win):
        if self.isDashing:
            pygame.draw.rect(win, ("Green"), self.collisionbox)
        else:
            pygame.draw.rect(win, self.colour, self.collisionbox)
        pygame.draw.rect(win, (255,0,255), self.footCollisionbox)
        pygame.draw.rect(win, (255,0,255), self.headCollisionbox)
        if isinstance (self, Archer) == True:
            if self.isFiringArrow or self.isLightAttacking:
                pygame.draw.rect(win, (255, 0, 0), self.attackCollisionBox)
        elif self.isLightAttacking or self.isHeavyAttacking:
            pygame.draw.rect(win, (255, 0, 0), self.attackCollisionBox)
    
    def Gravity(self):
        #Applies gravity to the player based on mass
        self.vel_y += c.GRAVITY*self.mass
        #Applies a counteractive force to gravity if the player is on a platform so that they do not fall through the platform
        if self.isGrounded:
            self.vel_y -= c.NORMALCONTACTFORCE*self.mass

    def OnGroundCheck(self, platList):
        #Keeps a track of the number of platforms the player is colliding with and passing through
        collideCount = 0
        passThroughCount = 0
        #Iterates through each platform
        for i in range(len(platList)):
            #Checks if the player is colliding with current platform as long as player is not passing through
            if self.footCollisionbox.colliderect(platList[i].collisionbox) and not self.isPassingThrough:
                collideCount += 1
                self.currentPlat = platList[i]
            #Checks if player is passing through platform
            if self.isPassingThrough and (self.collisionbox.colliderect(platList[i].collisionbox) or self.footCollisionbox.colliderect(platList[i].collisionbox) and platList[i].passThrough[:4] == "True"):
                passThroughCount += 1
        #if the player is colliding with any platforms, isGrounded is set to true so the normal contact force will be applied and numJumps is reset to 2
        if collideCount >= 1:
            self.isGrounded = True
            self.numJumps = 2
            #If the player is jumping up through the platform (vel_y >= 0), the player is non longer jumping and y velocity and coordinates are set to stop player being stuck in platform
            if self.vel_y >= 0:
                self.y = self.currentPlat.y - self.height
                self.vel_y = 0
                self.isJumping = False
        #If collide count is 0 then the player is either passing through a platform or in the air, so isGrounded is false and the player is not currently on any platform
        else:
            self.isGrounded = False
            self.currentPlat = None
        #If the player is passing through a platform, isPassingThrough is true
        if passThroughCount >= 1:
            self.isPassingThrough = True
        else:
            self.isPassingThrough = False

    def DeathCheck(self):
        #Checks if the player is off the bottom of the screen, if so they are dead
        return self.y > c.height + self.height*4


    def GoDown(self):
        #try,except is used incase the player is not currently on a platform
        try:
            #Player is passing through the platform if it can be passed through
            if self.currentPlat.passThrough[:4] == "True" and self.currentPlat is not None:
                self.isPassingThrough = True
                self.isGrounded = False
                self.passThroughLastUpdate = pygame.time.get_ticks()
        except:
            self.isPassingThrough = False


    def HitHead(self, platList):
        #Iterates through each platform in the scene
        for plat in platList:
            #If the platform cannot be passed through and the player's head is colliding with it, the player is kept below the platform and y velocity is set to 0
            if self.headCollisionbox.colliderect(plat.collisionbox) and plat.passThrough[:5] == "False":
                self.y = plat.y+plat.height+5
                self.vel_y = 0
            #If the side of the player is colliding with a platform that cannot be passed through, the player is kept to the side of the platform and x velocity is set to 0
            if self.collisionbox.colliderect(plat.collisionbox) and plat.passThrough[:5] == "False" and not self.footCollisionbox.colliderect(plat.collisionbox) and not self.headCollisionbox.colliderect(plat.collisionbox):
                self.vel_x = 0
                if self.x - plat.x >= 0:
                    self.x = plat.x+plat.width
                else:
                    self.x = plat.x-self.width

    def DashCooldownCheck(self):
        #Subtracts time when the player last dashed from the current time and checks if this is greater than the cooldown, if it is then the player can dash again
        currentTime = pygame.time.get_ticks()
        if currentTime - self.dashLastUpdate >= c.dashCooldown:
            self.canDash = True
            self.dashLastUpdate = currentTime
    def IsDashingCooldownCheck(self):
        #Subtracts time when the player started dashing from the current time and checks if this is greater than the cooldown, if it is then the player stops dashing
        currentTime = pygame.time.get_ticks()
        if currentTime - self.isDashingLastUpdate >= c.isDashingCooldown:
            self.isDashing = False
            self.isDashingLastUpdate = currentTime

    
    def Run(self):
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        #If the current direction is right, the animation will be running to the right
        if self.currentDir == 1:
            self.currentAnim = self.runFrames
            self.currentAnimIndex = 1
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0
                if self.currentFrame >= len(self.runFrames):
                    self.currentFrame = 0
        #If the current direction is left, the animation will be running to the left
        elif self.currentDir == -1:
            self.currentAnim = self.flippedRunFrames
            self.currentAnimIndex = 5
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0
                if self.currentFrame >= len(self.runFrames):
                    self.currentFrame = 0

    def Jump(self):
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        #If the current direction is right, the animation will be jumping to the right
        if self.currentDir == 1:
            self.currentAnim = self.jumpFrames
            self.currentAnimIndex = 8
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0
                if self.currentFrame >= len(self.jumpFrames):
                    self.currentFrame = 0
        #If the current direction is left, the animation will be jumping to the left
        elif self.currentDir == -1:
            self.currentAnim = self.flippedJumpFrames
            self.currentAnimIndex = 9
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0
                if self.currentFrame >= len(self.jumpFrames):
                    self.currentFrame = 0

    def Idle(self):
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        #If the current direction is right, the animation will be idle, facing to the right
        if self.currentDir == 1:
            self.currentAnim = self.idleFrames
            self.currentAnimIndex = 0
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                    self.currentFrame += 1
                    self.animLastUpdate = currentTime
                    #If the final frame in the animation is reached, the frame number should be reset to 0
                    if self.currentFrame >= len(self.idleFrames):
                        self.currentFrame = 0    
        #If the current direction is left, the animation will be idle, facing to the left
        elif self.currentDir == -1:
            self.currentAnim = self.flippedIdleFrames
            self.currentAnimIndex = 4
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0
                if self.currentFrame >= len(self.idleFrames):
                    self.currentFrame = 0

    def Move(self, otherPlayer, arrowList):
        #arrow defined at the start so that it can be used in comparative statements
        arrow = None
        #Shortcut because this function is used repeatedly
        keys = pygame.key.get_pressed()
        #Resets isAttacked to False when the other player has finished attacking
        if self.isAttacked and not otherPlayer.isHeavyAttacking and not otherPlayer.isLightAttacking:
            self.isAttacked = False
        #Checks if player is pressing left keybind and moves them
        if keys[self.Keybinds["left"]] and self.isAttacked == False and self.isDashing == False and self.vel_x > -c.maxSpeed:
            if not self.isHeavyAttacking:
                self.vel_x += -c.acceleration
            #Max speed (ignoring direction) is lower when player is heavy attacking to make the attacks fair and carry some risk to perform
            elif self.isHeavyAttacking and self.vel_x > -c.maxSlowSpeed:
                self.vel_x += -c.acceleration

        #Checks if player is pressing right keybind and moves them
        if keys[self.Keybinds["right"]] and self.isAttacked == False and self.isDashing == False and self.vel_x < c.maxSpeed:
            if not self.isHeavyAttacking:
                self.vel_x += c.acceleration
            #Max speed (ignoring direction) is lower when player is heavy attacking to make the attacks fair and carry some risk to perform
            elif self.isHeavyAttacking and self.vel_x < c.maxSlowSpeed:
                self.vel_x += c.acceleration

        #If player is pressing down key, program runs GoDown()
        if keys[self.Keybinds["down"]] and self.isGrounded == True:
            self.GoDown()

        #Animations are ordered by priority based on which animation should be showing if several actions are occuring at the same time
        #If player is performing a heavy attack, program runs HeavyAttack()
        if self.isHeavyAttacking == True:
            arrow = self.HeavyAttack(otherPlayer, arrowList)
        #If player is performing a light attack, program runs LightAttack()
        elif self.isLightAttacking == True:
            arrow = self.LightAttack(otherPlayer)
        #If player is jumping, program runs Jump()
        elif self.isJumping == True:
            self.Jump()
        #If player's speed (ignoring direction) is greater than 0, program runs Run()
        elif self.vel_x > 0 or self.vel_x < 0:
            self.Run()
        #If player is not moving, program runs Idle()
        elif self.vel_x == 0 or self.currentAnim == 0:
            self.currentAnim = self.idleFrames
            self.Idle()

        #If speed (ignoring direction) is greater than 0.25 (so that the player becomes stationary and does not keep moving side to side), then friction should be applied opposite to motion and currentDir should be set to direction of velocity
        if self.vel_x >= 0.25:
            self.vel_x -= c.FRICTION
            self.currentDir = 1
        elif self.vel_x <= -0.25:
            self.vel_x += c.FRICTION
            self.currentDir = -1
        else:
            self.vel_x = 0
    
        #Checks if the player is being attacked
        self.CheckAttacked(otherPlayer, arrowList)
        #Updates the player's position based on current velocity
        self.x += self.vel_x
        self.y += self.vel_y

        #Program runs Update()
        self.Update(arrowList)

        return arrow
    
    def MakeObject(self, player, otherPlayer):
        #Used for sending data to the server in this format
        return OnlineObject(self.x, self.y, otherPlayer.score, self.currentAnimIndex, self.currentDir, self.isLightAttacking, self.isHeavyAttacking, self.isGrounded, self.isJumping, self.isAttacked, self.isDashing, self.isPassingThrough, self.currentFrame, player)
    
    def KnockbackCalculator(self):
        #Uses the knockback formula if the damage taken is positive
        if self.damageTaken > 0:
            knockback = (2+(self.damageTaken)**1/4)
        else:
            knockback = 0
        return knockback

    def CheckAttacked(self, attacker, arrowList):
        #Checks if player is colliding with the enemy's attackCollisionbox and checks the player is not already attacked - because the player could then be hit multiple times by one attack - or the player is not dashing - because this should result in a dodge of attack
        if self.collisionbox.colliderect(attacker.attackCollisionBox) and self.isAttacked == False and attacker.isLightAttacking == True and self.isDashing == False:
            self.damageTaken += 15
            self.vel_x = self.KnockbackCalculator()*attacker.currentDir
            self.isAttacked = True
            attacker.isLightAttacking = False
        #Checks if the player is an Archer because the Archer's heavy attack works by firing an arrow instead of a standard attack
        if isinstance (attacker, Archer) == True:
            #Checks if player is colliding with the enemy's attackCollisionbox and checks the player is not already attacked - because the player could then be hit multiple times by one attack - or the player is not dashing - because this should result in a dodge of attack
            if self.collisionbox.colliderect(attacker.attackCollisionBox) and self.isDashing == False and attacker.isFiringArrow == True:
                self.damageTaken += 30
                self.vel_x = self.KnockbackCalculator()*attacker.currentDir
                self.isAttacked = True 
                attacker.isFiringArrow = False
                #Iterates through arrows in arrowList to check if they are colliding, if so their hasHit attribute is set to True so they will be removed from the scene
                for arrow in arrowList:
                    arrow.hasHit = True
                attacker.isHeavyAttacking = False
        #Checks if player is colliding with the enemy's attackCollisionbox and checks the player is not already attacked - because the player could then be hit multiple times by one attack - or the player is not dashing - because this should result in a dodge of attack
        if self.collisionbox.colliderect(attacker.attackCollisionBox) and self.isAttacked == False and attacker.isHeavyAttacking == True and self.isDashing == False:
            self.damageTaken += 20
            self.vel_x = self.KnockbackCalculator()*attacker.currentDir
            self.isAttacked = True
            attacker.isHeavyAttacking = False

class Knight(Player):
    def __init__(self, x, y, width, height, colour):
        super().__init__(x, y, width, height, colour)

        #Attributes which only apply to the Knight
        #imageDisplacement is how far the image needs to be moved when drawn onto the surface so that it is in the right place
        self.imageDisplacement = [-1,-16]
            
        #These are the animation images for this particular character
        self.idleAnimImage  = pygame.image.load("Knight/Animations/Idle.png").convert_alpha()
        self.runAnimImage  = pygame.image.load("Knight/Animations/Run.png").convert_alpha()
        self.attackAnimImage  = pygame.image.load("Knight/Animations/Light Attack.png").convert_alpha()
        self.heavyAttackAnimImage = pygame.image.load("Knight/Animations/Heavy Attack.png").convert_alpha()
        self.jumpAnimImage = pygame.image.load("Knight/Animations/Jump.png").convert_alpha()

        #attackCollisionbox is a pygame rect object which is where the player's attack is, this is different for each character
        self.attackCollisionBox = pygame.Rect(x, y, width, height)

        #Attack cooldown's for the Knight's attacks
        self.lightAttackCooldown = 1200
        self.heavyAttackCooldown = 3000
    
    def LoadAnims(self):
        #Each for loop calls GetImage for each individual frame to load all the standard and flipped animations
        for i in range(4):
            self.idleFrames.append(self.GetImage(i, "r", self.idleAnimImage, 67.5, 86, 0.85, (0, 0, 0)))
            self.flippedIdleFrames.append(self.GetImage(i, "l", self.idleAnimImage, 67.5, 86, 0.85, (0, 0, 0)))
        for i in range(5):
            self.runFrames.append(self.GetImage(i, "r", self.runAnimImage, 72.5, 86, 0.85, (0, 0, 0)))
            self.flippedRunFrames.append(self.GetImage(i,"l", self.runAnimImage, 72.5, 86, 0.85, (0, 0, 0)))
        for i in range(3):
            self.lightAttackFrames.append(self.GetImage(i, "r", self.attackAnimImage, 100, 86, 0.85, (0, 0, 0)))
            self.flippedLightAttackFrames.append(self.GetImage(i, "l", self.attackAnimImage, 100, 86, 0.85, (0, 0, 0)))
        for i in range(5):
            self.heavyAttackFrames.append(self.GetImage(i, "r", self.heavyAttackAnimImage, 82, 86, 0.85, (0, 0, 0)))
            self.flippedHeavyAttackFrames.append(self.GetImage(i, "l", self.heavyAttackAnimImage, 82, 86, 0.85, (0, 0, 0)))
        for i in range(6):
            self.jumpFrames.append(self.GetImage(i, "r", self.jumpAnimImage, 80, 86, 0.85, (0, 0, 0)))
            self.flippedJumpFrames.append(self.GetImage(i, "l", self.jumpAnimImage, 80, 86, 0.85, (0, 0, 0)))

    def LightAttack(self, otherPlayer):
        #If the player is attacking is checked in the Play() gameloop because it uses the pygame event manager
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        self.isLightAttacking = True
        #If the player is facing right, plays the right animation
        if self.currentDir == 1:
            self.currentAnim = self.lightAttackFrames
            self.currentAnimIndex = 2
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.lightAttackFrames):
                    self.isLightAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
        #If the player is facing left, plays the left animation
        elif self.currentDir == -1:
            self.currentAnim = self.flippedLightAttackFrames
            self.currentAnimIndex = 6
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.lightAttackFrames):
                    self.isLightAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False

    def HeavyAttack(self, otherPlayer, arrowList):
        #If the player is attacking is checked in the Play() gameloop because it uses the pygame event manager
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        self.isHeavyAttacking = True
        #If the player is facing right, plays the right animation
        if self.currentDir == 1:
            self.currentAnim = self.heavyAttackFrames
            self.currentAnimIndex = 3
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.heavyAttackFrames):
                    self.isHeavyAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
        #If the player is facing left, plays the left animation
        elif self.currentDir == -1:
            self.currentAnim = self.flippedHeavyAttackFrames
            self.currentAnimIndex = 7
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.heavyAttackFrames):
                    self.isHeavyAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
            
    def CanAttackCheck(self):
        currentTime = pygame.time.get_ticks()
        #Subtracts time of last attack from current time and compares to attack cooldown, and if it is bigger then the player can do the attack being checked (This is done for light and heavy attacks)
        if currentTime - self.lightAttackLastUpdate >= self.lightAttackCooldown:
            self.canLightAttack = True
            self.lightAttackLastUpdate = currentTime
        if currentTime - self.heavyAttackLastUpdate >= self.heavyAttackCooldown:
            self.canHeavyAttack = True
            self.heavyAttackLastUpdate = currentTime
    
    def Update(self, arrowList):
        #Updates all of the hitboxes for the Knight player, so that they are in the correct place for collision detection
        self.collisionbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.footCollisionbox = pygame.Rect(self.x, self.y+(self.height-2.5), self.width, 5)
        self.headCollisionbox = pygame.Rect(self.x, self.y-5, self.width, 5)
        self.attackCollisionBox = pygame.Rect((self.x+self.width/4)+3*self.width/4*self.currentDir, self.y, self.width/2, self.height)

class Archer(Player):
    def __init__(self, x, y, width, height, colour):
        super().__init__(x, y, width, height, colour)

        #Attributes which only apply to the Archer
        #imageDisplacement is how far the image needs to be moved when drawn onto the surface so that it is in the right place
        self.imageDisplacement = [-25,-50]

        #These are the animation images for this particular character  
        self.idleAnimImage  = pygame.image.load("Archer/Animations/Idle.png").convert_alpha()
        self.runAnimImage  = pygame.image.load("Archer/Animations/Run.png").convert_alpha()
        self.attackAnimImage  = pygame.image.load("Archer/Animations/Light Attack.png").convert_alpha()
        self.heavyAttackAnimImage = pygame.image.load("Archer/Animations/Heavy Attack.png").convert_alpha()
        self.jumpAnimImage = pygame.image.load("Archer/Animations/Jump.png").convert_alpha()

        #attackCollisionbox is a pygame rect object which is where the player's attack is, this is different for each character
        self.attackCollisionBox = pygame.Rect(x, y, width, height)

        #Attack cooldown's for the Archer's attacks
        self.lightAttackCooldown = 1400
        self.heavyAttackCooldown = 5000

        #Both of these are booleans unique to the Archer, canCreateArrow is for whether the player can shoot again and isFiringArrow is whether the player is currently firing an arrow
        self.canCreateArrow  = True
        self.isFiringArrow = False
    
    def LoadAnims(self):
        #Each for loop calls GetImage for each individual frame to load all the standard and flipped animations
        for i in range(9):
            self.idleFrames.append(self.GetImage(i, "r", self.idleAnimImage, 128, 128, 0.85, (0, 0, 0)))
            self.flippedIdleFrames.append(self.GetImage(i, "l", self.idleAnimImage, 128, 128, 0.85, (0, 0, 0)))
        for i in range(8):
            self.runFrames.append(self.GetImage(i, "r", self.runAnimImage, 128, 128, 0.85, (0, 0, 0)))
            self.flippedRunFrames.append(self.GetImage(i,"l", self.runAnimImage, 128, 128, 0.85, (0, 0, 0)))
        for i in range(5):
            self.lightAttackFrames.append(self.GetImage(i, "r", self.attackAnimImage, 128, 128, 0.85, (0, 0, 0)))
            self.flippedLightAttackFrames.append(self.GetImage(i, "l", self.attackAnimImage, 128, 128, 0.85, (0, 0, 0)))
        for i in range(14):
            self.heavyAttackFrames.append(self.GetImage(i, "r", self.heavyAttackAnimImage, 128, 128, 0.85, (0, 0, 0)))
            self.flippedHeavyAttackFrames.append(self.GetImage(i, "l", self.heavyAttackAnimImage, 128, 128, 0.85, (0, 0, 0)))
        for i in range(9):
            self.jumpFrames.append(self.GetImage(i, "r", self.jumpAnimImage, 128, 128, 0.85, (0, 0, 0)))
            self.flippedJumpFrames.append(self.GetImage(i, "l", self.jumpAnimImage, 128, 128, 0.85, (0, 0, 0)))

    def LightAttack(self, otherPlayer):
        #If the player is attacking is checked in the Play() gameloop because it uses the pygame event manager
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        self.isLightAttacking = True
        #If the player is facing right, plays the right animation
        if self.currentDir == 1:
            self.currentAnim = self.lightAttackFrames
            self.currentAnimIndex = 2
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.lightAttackFrames):
                    self.isLightAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
        #If the player is facing left, plays the left animation
        elif self.currentDir == -1:
            self.currentAnim = self.lightAttackFrames
            self.currentAnimIndex = 6
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.lightAttackFrames):
                    self.isLightAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False

    def HeavyAttack(self, otherPlayer, arrowList):
        #If the player is attacking is checked in the Play() gameloop because it uses the pygame event manager
        self.isAnimating = True
        currentTime = pygame.time.get_ticks()
        arrow = None
        self.isHeavyAttacking = True
        #If the player is facing right, plays the right animation
        if self.currentDir == 1:
            self.currentAnim = self.heavyAttackFrames
            self.currentAnimIndex = 3
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #Creates an arrow that shoots out the bow on the frame when the animation releases the bow string
                if self.canCreateArrow == True and self.currentFrame == 9:
                    arrow = Arrow(self.x, self.y, 20, -2.5, 1, self)
                    self.canCreateArrow = False
                    self.isFiringArrow = True
                    arrowList.append(arrow)
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.heavyAttackFrames):
                    self.isHeavyAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
                return arrow
        #If the player is facing left, plays the left animation
        elif self.currentDir == -1:
            self.currentAnim = self.flippedHeavyAttackFrames
            self.currentAnimIndex = 7
            #Subtracts time of last frame switch from current time and compares to animation cooldown, and if it is bigger then the next frame is set as the current frame
            if currentTime - self.animLastUpdate >= c.animCooldown:
                self.currentFrame += 1
                self.animLastUpdate = currentTime
                #Creates an arrow that shoots out the bow on the frame when the animation releases the bow string
                if self.canCreateArrow == True and self.currentFrame == 9:
                    arrow = Arrow(self.x, self.y, -20, -2.5, -1, self)
                    self.canCreateArrow = False
                    self.isFiringArrow = True
                    arrowList.append(arrow)
                #If the final frame in the animation is reached, the frame number should be reset to 0 and player is no longer attacking
                if self.currentFrame >= len(self.heavyAttackFrames):
                    self.isHeavyAttacking = False
                    self.currentFrame = 0
                    otherPlayer.isAttacked = False
                return arrow

    def CanAttackCheck(self):
        currentTime = pygame.time.get_ticks()
        #Subtracts time of last attack from current time and compares to attack cooldown, and if it is bigger then the player can do the attack being checked (This is done for light and heavy attacks)
        if currentTime - self.lightAttackLastUpdate >= self.lightAttackCooldown:
            self.canLightAttack = True
            self.lightAttackLastUpdate = currentTime
        if currentTime - self.heavyAttackLastUpdate >= self.heavyAttackCooldown:
            self.canHeavyAttack = True
            self.heavyAttackLastUpdate = currentTime
            self.canCreateArrow = True
    
    def Update(self, arrowList):
        #Updates all of the hitboxes for the Archer player, so that they are in the correct place for collision detection
        self.collisionbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.footCollisionbox = pygame.Rect(self.x, self.y+(self.height-2.5), self.width, 5)
        self.headCollisionbox = pygame.Rect(self.x, self.y-5, self.width, 5)
        #Changes attack hitbox depending on which attack the Archer is doing, if it is light it is just like the Knight but if it is heavy it should follow the arrow
        if self.isFiringArrow:
            self.attackCollisionBox = pygame.Rect(arrowList[0].x, arrowList[0].y+24, 64, 16)
        elif self.isLightAttacking == True:
            self.attackCollisionBox = pygame.Rect((self.x+self.width/4)+3*self.width/4*self.currentDir, self.y, self.width/2, self.height)
        else:
            self.attackCollisionBox = pygame.Rect(c.width*2,c.height*2, 1, 1)

#OnlineObject creates objects that act as a container for information to be transferred to the server
class OnlineObject():
    def __init__(self, x, y, score, currentAnim, currentDir, isLightAttacking, isHeavyAttacking, isGrounded, isJumping, isAttacked, isDashing, isPassingThrough, currentFrame, player):
        #All the attributes are attributes from the player which are essential to transmit so that the player on the other client does the same actions as on this client
        self.x = x
        self.y = y
        self.score = score
        self.currentAnim = currentAnim
        self.currentDir = currentDir
        self.isLightAttacking = isLightAttacking
        self.isHeavyAttacking = isHeavyAttacking
        self.isGrounded = isGrounded
        self.isJumping = isJumping
        self.isAttacked = isAttacked
        self.isDashing = isDashing
        self.isPassingThrough = isPassingThrough
        self.currentFrame = currentFrame
        self.player = player

    def UpdateObject(self, object, arrowList, otherPlayer):
        #UpdateObject changes all the attributes of the player on this client to the values transmitted from the other client
        arrow = None
        object.x = self.x
        object.y = self.y
        otherPlayer.score = self.score
        object.currentDir = self.currentDir
        object.isLightAttacking = self.isLightAttacking
        object.isHeavyAttacking = self.isHeavyAttacking
        object.isGrounded = self.isGrounded
        object.isJumping = self.isJumping
        object.isAttacked = self.isAttacked
        object.isDashing = self.isDashing
        object.isPassingThrough = self.isPassingThrough
        object.currentFrame = self.currentFrame
        object.currentAnim = object.onlineAnims[self.currentAnim]
        object.Update(arrowList)

        if object.isLightAttacking == True:
            arrow = object.LightAttack(otherPlayer)

        if object.isHeavyAttacking == True:
            arrow = object.HeavyAttack(otherPlayer, arrowList)
        return arrow