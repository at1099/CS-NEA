class Stack:
  def __init__(self, maxSize):
    #Attributes
    #data stores the objects which are pushed onto the stack
    self.data = []
    #top keeps a track of the index of the item ontop of the stack 
    self.top = -1
    #mode stores the type of object of each item in data
    self.mode = []
    #maxSize is set when the stack is created, it is the maximum number of items that can be on the stack
    self.maxSize = maxSize

  def GetData(self):
    #Used to get an array of the data
    return self.data

  def SetData(self, index, data):
    #Used to set the item at a certain index to the inputted data
    (self.data)[index] = data

  def AddData(self, data, mode):
    #Appends data to the top of the stack along with its type (mode)
    self.data.append(data)
    self.mode.append(mode)
    
  def GetTop(self):
    #Returns the top item on the stack
    return self.top

  def SetTop(self, top):
    #Sets the top item on the stack to a different piece of data
    self.top = top

  def SetSize(self, size):
    #Changes the max size of the stack
    self.maxSize += size

  def IsEmpty(self):
    #Checks if the stack is empty
    return len(self.data) <= 0

  def IsFull(self):
    #Checks if the stack is full (maxSize has been reached)
    if len(self.data) >= self.maxSize:
      return True

  def Push(self, newData, newMode):
    #Checks if the stack is full
    if self.IsFull():
      print("Error, stack full")
    #If not the data and its mode is added to the top of the stack and the top is set to the index of this piece of data aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    else:
      self.AddData(newData, newMode)
      self.SetTop(len(self.data)-1)

  def Pop(self):
    #Sets the node that is going to be removed as the top of the stack
    currentNode = self.GetTop()
    #Checks if the stack is empty
    if self.IsEmpty():
        print("ERROR")
        return "error, stack empty"
    #If not the data and mode is popped from the top of the stack and the top is set to the next item's index
    else:
      self.data.pop(currentNode)
      self.mode.pop(currentNode)
      self.SetTop(int(self.GetTop())-1)

  def Peek(self):
    #Used to view the top item on the stack
    return self.GetData()[self.GetTop()] 