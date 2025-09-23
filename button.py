import constants as c

#Button class is used to create button objects used in main.py
class Button():
    def __init__(self, image, pos, text_input, font, base_colour, hover_colour):
        #Attributes
        #Image is the background of the button if one is inputted
        self.image = image
        #The position of the button on the screen
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        #The font of the text on the button
        self.font = font
        #The normal colour that the button will be if the user is not hovering over it
        self.base_colour = base_colour
        #The colour of the button when the user is hovering over it
        self.hovering_colour = hover_colour
        #The text, as a string, that should appear on the button
        self.text_input = text_input
        #The text as a useable Pygame object
        self.text = self.font.render(self.text_input, True, self.base_colour)
        #Checks if the image is None so that the text can be set to the image instead
        if self.image is None:
              self.image = self.text
        #The rect that stores the position and can be used to check collisions with the button's image
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        #The rect that stores the position and can be used to check collisions with the button's text
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    #Update is used to draw the button onto the screen
    def Update(self, win):
        #Draws the image onto the screen if it exists (because this needs to be behind the text)
        if self.image is not None:
            win.blit(self.image, self.rect)
        #Draws the text onto the screen
        win.blit(self.text, self.text_rect)

    def CheckInput(self, position):
        #Used to check if the inputted coordinates of the mouse pointer is inside the button's area
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def ChangeColour(self, position):
        #Checks if the mouse pointer is inside the area and if so, changes the text colour to the hovering colour 
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_colour)
        else:
            self.text = self.font.render(self.text_input, True, self.base_colour)

