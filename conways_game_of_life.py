import pygame, sys, numpy as np
import math
#from pygame.locals import *

''' 
 The universe of the Game of Life is an infinite two-dimensional orthogonal grid of square cells, 
 each of which is in one of two possible states, alive or dead. Every cell interacts with its eight neighbours,
 which are the cells that are horizontally, vertically, or diagonally adjacent. At each step in time, 
 the following transitions occur:
 
    Any live cell with fewer than two live neighbors dies, as if caused by under-population.
    Any live cell with two or three live neighbors lives on to the next generation.
    Any live cell with more than three live neighbors dies, as if by overcrowding.
    Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction.
    
 The initial pattern constitutes the seed of the system. The first generation is created by applying the above rules 
 simultaneously to every cell in the seed births and deaths occur simultaneously, and the discrete moment at which this 
 happens is sometimes called a tick (in other words, each generation is a pure function of the preceding one). 
 The rules continue to be applied repeatedly to create further generations.
'''

FPS = 10
GRIDWIDTH = 1280
GRIDHEIGHT = 960
PANELWIDTH = 240
WINDOWWIDTH = GRIDWIDTH + PANELWIDTH
WINDOWHEIGHT = GRIDHEIGHT 
CELLSIZE = 20
assert GRIDWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert GRIDHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(GRIDWIDTH / CELLSIZE) # CELLWIDTH/HEIGHT is the width of the window in cells
CELLHEIGHT = int(GRIDHEIGHT / CELLSIZE)
XCENTER = CELLWIDTH / 2
YCENTER = CELLHEIGHT / 2

#                 R   G   B
BLACK         = ( 0,  0,  0)
ACTIVE_GREEN  = ( 0,255,  0)
DARKGREEN     = ( 0,155,  0)
INACTIVEGREEN = ( 0, 55,  0)
DARKGRAY      = (40, 40, 40)
BGCOLOR       = BLACK

TEXTCOLOR = ACTIVE_GREEN
TILECOLOR = BGCOLOR

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT
    # variables for the screen buttons
    global START_ACT, START_ACT_RECT, STOP_ACT, STOP_ACT_RECT, CLEAR_ACT, CLEAR_ACT_RECT, QUIT, QUIT_RECT
    global START_INACT, START_INACT_RECT, STOP_INACT, STOP_INACT_RECT, CLEAR_INACT, CLEAR_INACT_RECT
    global BLINKER_BUTTON_RECT, BEACON_BUTTON_RECT, BLINKER_BUTTON_RECT, BEACON_BUTTON_RECT, DIRTY_PUFFER_BUTTON_RECT
    global TOAD_BUTTON_RECT, GLIDER_BUTTON_RECT, LWSS_BUTTON_RECT, CLEAN_PUFFER_BUTTON_RECT, C5_SPACESHIP_BUTTON_RECT
    global GLIDER_GUN_BUTTON_RECT, PULSAR_BUTTON_RECT
           
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((GRIDWIDTH + PANELWIDTH, GRIDHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('c_gol')
    
    # Store the option buttons and their rectangles in OPTIONS.
    START_ACT, START_ACT_RECT = makeText('Start', TEXTCOLOR, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 120)
    START_INACT, START_INACT_RECT = makeText('Start', INACTIVEGREEN, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 120)
    STOP_ACT,  STOP_ACT_RECT  = makeText('Stop',  TEXTCOLOR, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 90)
    STOP_INACT,  STOP_INACT_RECT  = makeText('Stop',  INACTIVEGREEN, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 90)
    CLEAR_ACT, CLEAR_ACT_RECT = makeText('Clear', TEXTCOLOR, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 60)
    CLEAR_INACT, CLEAR_INACT_RECT = makeText('Clear', INACTIVEGREEN, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 60)
    QUIT,  QUIT_RECT  = makeText('Quit',  TEXTCOLOR, TILECOLOR, GRIDWIDTH + 80, GRIDHEIGHT - 30)
   
    startActive = True
    stopActive = False
    clearActive = False
  
    # get and set the initial state
    initialState = np.arange(CELLWIDTH*CELLHEIGHT)
    initialState.shape = (CELLWIDTH, CELLHEIGHT)
    initialState[:] = False
    previousState = initialState
    currentState = initialState
    for i in range(initialState.shape[0]):
        for j in range(initialState.shape[1]):
            if initialState[i][j] == True:
                setOneCell( i, j, 'on')
                   
    #run the main game loop
    running = False
    while True:
        for event in pygame.event.get(): # event handling loop
            if event.type == 6: #MOUSEBUTTONUP:
                x,y = math.floor(event.pos[0]/CELLSIZE), math.floor(event.pos[1]/CELLSIZE)
                if QUIT_RECT.collidepoint(event.pos): # user clicked Clear
                    terminate()
                if running == True:
                    if stopActive and STOP_ACT_RECT.collidepoint(event.pos): # user clicked Stop
                        running = False
                        startActive = True
                        stopActive = False
                        clearActive = True
                elif running == False:
                    currentState = checkForCreationButtonClick(event.pos, previousState)
                    previousState = currentState
                    if startActive and START_ACT_RECT.collidepoint(event.pos): # user clicked Start
                        running = True            
                        startActive = False
                        stopActive = True
                        clearActive = False
                    elif clearActive and CLEAR_ACT_RECT.collidepoint(event.pos): # user clicked Clear
                        previousState[:] = False
                        currentState[:] = False
                        running = False
                        startActive = True
                        stopActive = False                
                                                
                    # handle a click inside the simulation window
                    elif x < CELLWIDTH and y < CELLHEIGHT:
                        if currentState[x][y] == False:
                            setOneCell(x,y, 'on')
                            currentState[x][y] = True
                            previousState[x][y] = True
                        elif currentState[x][y] == True:
                            setOneCell(x,y, 'off')
                            currentState[x][y] = False
                            previousState[x][y] = False
        
        # run the next iteration        
        if running == True:
            currentState = iterate(previousState)
            previousState[:] = currentState
        
        # set the display
        for i in range(currentState.shape[0]):
            for j in range(currentState.shape[1]):
                if currentState[i][j] == True:
                    setOneCell(i, j, 'on')
                else:
                    setOneCell(i, j,'off')
               
        # draw the grid and update the display
        if startActive:
            DISPLAYSURF.blit(START_ACT, START_ACT_RECT)
        else:
            DISPLAYSURF.blit(START_INACT, START_INACT_RECT)
            
        if stopActive:
            DISPLAYSURF.blit(STOP_ACT, STOP_ACT_RECT)
        else:
            DISPLAYSURF.blit(STOP_INACT, STOP_INACT_RECT)

        if clearActive:
            DISPLAYSURF.blit(CLEAR_ACT, CLEAR_ACT_RECT)
        else:
            DISPLAYSURF.blit(CLEAR_INACT, CLEAR_INACT_RECT)
            
        # always display the quit button
        DISPLAYSURF.blit(QUIT, QUIT_RECT)
        
        # display buttons to add shapes
        displayCreationButtons()
               
        # update the display
        drawGrid()         
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def getNumLiveNeighbors(x, y, currArray):
    retVal = 0
    for i in range(x-1, x+2): # range() excludes the last element
        for j in range(y-1, y+2):
            if currArray[i%CELLWIDTH][j%CELLHEIGHT] == True and not (i%CELLWIDTH == x and j%CELLHEIGHT == y):
                retVal += 1
    return retVal

def iterate(prevCellArray):
    currCellArray = np.arange(CELLWIDTH*CELLHEIGHT)
    currCellArray.shape = (CELLWIDTH, CELLHEIGHT)
    # set all cells to be inactive
    currCellArray[:] = False
            
    for i in range(prevCellArray.shape[0]):
        for j in range(prevCellArray.shape[1]):
            if prevCellArray[i][j] == True:
                numLiveNeighbors = getNumLiveNeighbors(i,j, prevCellArray)
                if numLiveNeighbors < 2:
                    currCellArray[i][j] = False # under population
                if numLiveNeighbors == 2 or numLiveNeighbors == 3:
                    currCellArray[i][j] = True # healthy population
                if numLiveNeighbors > 3:
                    currCellArray[i][j] = False # overcrowding

                # need to check dead neighbors of every live cell
                for k in range(i-1,i+2): # range() is exclusive
                    for l in range(j-1,j+2):
                        if getNumLiveNeighbors(k%CELLWIDTH,l%CELLHEIGHT, prevCellArray) == 3:
                            currCellArray[k%CELLWIDTH][l%CELLHEIGHT] = True  # reproduction
                                 
    return currCellArray
    
def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (GRIDWIDTH - 200, GRIDHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)
    
def checkForCreationButtonClick(pos, previousState):
    if BLINKER_BUTTON_RECT.collidepoint(pos):
        previousState = createBlinker(XCENTER, YCENTER)
    elif BEACON_BUTTON_RECT.collidepoint(pos):
        previousState = createBeacon(XCENTER, YCENTER)
    elif DIRTY_PUFFER_BUTTON_RECT.collidepoint(pos):
        previousState = createDirtyPuffer(XCENTER, YCENTER)
    elif TOAD_BUTTON_RECT.collidepoint(pos):
        previousState = createToad(XCENTER, YCENTER)
    elif GLIDER_BUTTON_RECT.collidepoint(pos):
        previousState = createGlider(XCENTER, YCENTER)
    elif LWSS_BUTTON_RECT.collidepoint(pos):
        previousState = createLWSS(XCENTER, YCENTER)
    elif CLEAN_PUFFER_BUTTON_RECT.collidepoint(pos):
        previousState = createCleanPuffer(XCENTER, YCENTER)
    elif C5_SPACESHIP_BUTTON_RECT.collidepoint(pos):
        previousState = createC5spaceship(XCENTER, YCENTER)
    elif GLIDER_GUN_BUTTON_RECT.collidepoint(pos):
        previousState = createGliderGun(XCENTER, YCENTER)
    elif PULSAR_BUTTON_RECT.collidepoint(pos):
        previousState = createPulsar(XCENTER, YCENTER)
    
    return previousState


def terminate():
    pygame.quit()
    sys.exit()
       
def setOneCell(x, y, state):
    newRect = pygame.Rect(x*CELLSIZE, y*CELLSIZE, CELLSIZE, CELLSIZE)
    if state == 'on':
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, newRect)
    elif state == 'off':
        pygame.draw.rect(DISPLAYSURF, BGCOLOR, newRect)

def drawGrid():
    for x in range(0, GRIDWIDTH+1, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, GRIDHEIGHT))
    for y in range(0, GRIDHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (GRIDWIDTH, y))

def displayCreationButtons():
    BUTTON_SPACING = 10
    BUTTON_COL1_X = GRIDWIDTH + BUTTON_SPACING # x-position of first button in each row
    BUTTON_COL2_X = BUTTON_COL1_X + 50 + BUTTON_SPACING
    BUTTON_COL3_X = BUTTON_COL2_X + 50 + BUTTON_SPACING 
    
    BUTTON_ROW1_Y = 20 # y-position of top of first button row
    BUTTON_ROW2_Y = BUTTON_ROW1_Y + 50 + BUTTON_SPACING 
    BUTTON_ROW3_Y = BUTTON_ROW2_Y + 50 + BUTTON_SPACING 
    BUTTON_ROW4_Y = BUTTON_ROW3_Y + 50 + BUTTON_SPACING
    BUTTON_ROW5_Y = BUTTON_ROW4_Y + 50 + BUTTON_SPACING
    BUTTON_ROW6_Y = BUTTON_ROW5_Y + 50 + BUTTON_SPACING
    
    # set button positions
    BLINKER_BUTTON_POSITION = (BUTTON_COL1_X, BUTTON_ROW1_Y)
    BEACON_BUTTON_POSITION = (BUTTON_COL2_X, BUTTON_ROW1_Y)
    DIRTY_PUFFER_BUTTON_POSITION = (BUTTON_COL3_X, BUTTON_ROW1_Y)
    TOAD_BUTTON_POSITION = (BUTTON_COL1_X, BUTTON_ROW2_Y)
    GLIDER_BUTTON_POSITION = (BUTTON_COL2_X, BUTTON_ROW2_Y)
    LWSS_BUTTON_POSITION = (BUTTON_COL1_X, BUTTON_ROW3_Y)
    CLEAN_PUFFER_POSITION = (BUTTON_COL2_X, BUTTON_ROW3_Y)
    C5_SPACESHIP_POSITION = (BUTTON_COL1_X, BUTTON_ROW4_Y)
    GLIDER_GUN_POSITION = (BUTTON_COL1_X, BUTTON_ROW5_Y)
    PULSAR_POSITION = (BUTTON_COL1_X, BUTTON_ROW6_Y)
    
    # Blinker
    global BLINKER_BUTTON, BLINKER_BUTTON_RECT
    BLINKER_BUTTON_RECT = pygame.Rect(0, 0, 50, 50) # using actual size of .png
    BLINKER_BUTTON = pygame.image.load('BlinkerButton.png')
    BLINKER_BUTTON_RECT.topleft = BLINKER_BUTTON_POSITION
    DISPLAYSURF.blit(BLINKER_BUTTON, BLINKER_BUTTON_RECT)
    
    # Beacon
    global BEACON_BUTTON, BEACON_BUTTON_RECT
    BEACON_BUTTON_RECT = pygame.Rect(0, 0, 50, 50) # using actual size of .png
    BEACON_BUTTON = pygame.image.load('Beacon.png')
    BEACON_BUTTON_RECT.topleft = BEACON_BUTTON_POSITION  
    DISPLAYSURF.blit(BEACON_BUTTON, BEACON_BUTTON_RECT)
    
    # DirtyPuffer (50 x 141)
    global DIRTY_PUFFER_BUTTON, DIRTY_PUFFER_BUTTON_RECT
    DIRTY_PUFFER_BUTTON_RECT = pygame.Rect(0, 0, 50, 141) # using actual size of .png
    DIRTY_PUFFER_BUTTON = pygame.image.load('DirtyPuffer.png')
    DIRTY_PUFFER_BUTTON_RECT.topleft = DIRTY_PUFFER_BUTTON_POSITION 
    DISPLAYSURF.blit(DIRTY_PUFFER_BUTTON, DIRTY_PUFFER_BUTTON_RECT)
    
    # Toad (50 x 34)
    global TOAD_BUTTON, TOAD_BUTTON_RECT
    TOAD_BUTTON_RECT = pygame.Rect(0, 0, 50, 34) # using actual size of .png
    TOAD_BUTTON = pygame.image.load('Toad.png')
    TOAD_BUTTON_RECT.topleft = TOAD_BUTTON_POSITION 
    DISPLAYSURF.blit(TOAD_BUTTON, TOAD_BUTTON_RECT)
    
    # Glider (50 x 50)
    global GLIDER_BUTTON, GLIDER_BUTTON_RECT
    GLIDER_BUTTON_RECT = pygame.Rect(0, 0, 50, 50) # using actual size of .png
    GLIDER_BUTTON = pygame.image.load('Glider.png')
    GLIDER_BUTTON_RECT.topleft = GLIDER_BUTTON_POSITION
    DISPLAYSURF.blit(GLIDER_BUTTON, GLIDER_BUTTON_RECT)
    
    # Light Weight SpaceShip (50 x 43)
    global LWSS_BUTTON, LWSS_BUTTON_RECT
    LWSS_BUTTON_RECT = pygame.Rect(0, 0, 50, 43) # using actual size of .png
    LWSS_BUTTON = pygame.image.load('LWSS.png')
    LWSS_BUTTON_RECT.topleft = LWSS_BUTTON_POSITION
    DISPLAYSURF.blit(LWSS_BUTTON, LWSS_BUTTON_RECT)

    # CleanPuffer (55 x 50)
    global CLEAN_PUFFER_BUTTON, CLEAN_PUFFER_BUTTON_RECT
    CLEAN_PUFFER_BUTTON_RECT = pygame.Rect(0, 0, 55, 50) # using actual size of .png
    CLEAN_PUFFER_BUTTON = pygame.image.load('CleanPuffer.png')
    CLEAN_PUFFER_BUTTON_RECT.topleft = CLEAN_PUFFER_POSITION 
    DISPLAYSURF.blit(CLEAN_PUFFER_BUTTON, CLEAN_PUFFER_BUTTON_RECT)
   
    # c5_spaceship (150 x 52)
    global C5_SPACESHIP_BUTTON, C5_SPACESHIP_BUTTON_RECT
    C5_SPACESHIP_BUTTON_RECT = pygame.Rect(0, 0, 150, 52) # using actual size of .png
    C5_SPACESHIP_BUTTON = pygame.image.load('c5_spaceship.png')
    C5_SPACESHIP_BUTTON_RECT.topleft = C5_SPACESHIP_POSITION 
    DISPLAYSURF.blit(C5_SPACESHIP_BUTTON, C5_SPACESHIP_BUTTON_RECT)
    
    # GliderGun (172 x 50)
    global GLIDER_GUN_BUTTON, GLIDER_GUN_BUTTON_RECT
    GLIDER_GUN_BUTTON_RECT = pygame.Rect(0, 0, 172, 50) # using actual size of .png
    GLIDER_GUN_BUTTON = pygame.image.load('GliderGun.png')
    GLIDER_GUN_BUTTON_RECT.topleft = GLIDER_GUN_POSITION 
    DISPLAYSURF.blit(GLIDER_GUN_BUTTON, GLIDER_GUN_BUTTON_RECT)
    
    # Pulsar (150 x 150)
    global PULSAR_BUTTON, PULSAR_BUTTON_RECT
    PULSAR_BUTTON_RECT = pygame.Rect(0, 0, 150, 150) # using actual size of .png
    PULSAR_BUTTON = pygame.image.load('Pulsar.png')
    PULSAR_BUTTON_RECT.topleft = PULSAR_POSITION 
    DISPLAYSURF.blit(PULSAR_BUTTON, PULSAR_BUTTON_RECT)

def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)
            

def createBlinker(xCenter, yCenter):
    # test a blinker
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    retArray[xCenter][yCenter] = True
    retArray[xCenter][yCenter-1] = True
    retArray[xCenter][yCenter+1] = True
    return retArray
    
def createBeacon(xCenter, yCenter):
    # test a blinker
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    retArray[xCenter][yCenter] = True
    retArray[xCenter+1][yCenter] = True
    retArray[xCenter][yCenter+1] = True
    retArray[xCenter+1][yCenter+1] = True
    retArray[xCenter-1][yCenter-1] = True
    retArray[xCenter-2][yCenter-1] = True
    retArray[xCenter-1][yCenter-2] = True
    retArray[xCenter-2][yCenter-2] = True
    
    return retArray
    
def createToad(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    retArray[xCenter][yCenter] = True
    retArray[xCenter+1][yCenter] = True
    retArray[xCenter-1][yCenter] = True
    retArray[xCenter][yCenter-1] = True
    retArray[xCenter+1][yCenter-1] = True
    retArray[xCenter+2][yCenter-1] = True
    
    return retArray

def createDirtyPuffer(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    # top part
    retArray[xCenter][yCenter-6] = True
    retArray[xCenter-1][yCenter-6] = True
    retArray[xCenter+1][yCenter-6] = True
    retArray[xCenter+2][yCenter-6] = True
    retArray[xCenter-2][yCenter-7] = True
    retArray[xCenter+2][yCenter-7] = True
    retArray[xCenter+2][yCenter-8] = True
    retArray[xCenter+1][yCenter-9] = True
    # middle part
    retArray[xCenter][yCenter] = True
    retArray[xCenter][yCenter+1] = True
    retArray[xCenter][yCenter-1] = True
    retArray[xCenter-1][yCenter+2] = True
    retArray[xCenter-1][yCenter-1] = True
    retArray[xCenter-2][yCenter-2] = True
    # bottom part
    retArray[xCenter][yCenter+8] = True
    retArray[xCenter-1][yCenter+8] = True
    retArray[xCenter+1][yCenter+8] = True
    retArray[xCenter+2][yCenter+8] = True
    retArray[xCenter+2][yCenter+7] = True
    retArray[xCenter+2][yCenter+6] = True
    retArray[xCenter+1][yCenter+5] = True
    retArray[xCenter-2][yCenter+7] = True
    
    return retArray

def createGlider(xCenter, yCenter):
    # test a blinker
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    retArray[xCenter-1][yCenter-1] = True
    retArray[xCenter][yCenter] = True
    retArray[xCenter+1][yCenter] = True
    retArray[xCenter][yCenter+1] = True
    retArray[xCenter-1][yCenter+1] = True
    return retArray

def createLWSS(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    
    retArray[xCenter][yCenter] = True
    retArray[xCenter-1][yCenter] = True
    retArray[xCenter-2][yCenter-1] = True
    retArray[xCenter+1][yCenter] = True
    retArray[xCenter+2][yCenter] = True
    retArray[xCenter+2][yCenter-1] = True
    retArray[xCenter+2][yCenter-2] = True
    retArray[xCenter+1][yCenter-3] = True
    retArray[xCenter-2][yCenter-3] = True    
    return retArray

def createCleanPuffer(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    # bottom part
    retArray[xCenter][yCenter] = True
    retArray[xCenter][yCenter+1] = True
    retArray[xCenter+1][yCenter+1] = True
    retArray[xCenter-1][yCenter+2] = True
    retArray[xCenter][yCenter+2] = True
    retArray[xCenter+1][yCenter+2] = True
    retArray[xCenter+2][yCenter+2] = True
    retArray[xCenter-1][yCenter+3] = True
    retArray[xCenter][yCenter+3] = True
    retArray[xCenter+2][yCenter+3] = True
    retArray[xCenter+3][yCenter+3] = True
    retArray[xCenter+1][yCenter+4] = True
    retArray[xCenter+2][yCenter+4] = True
    # top part
    retArray[xCenter-2][yCenter-1] = True
    retArray[xCenter+2][yCenter-1] = True
    retArray[xCenter-6][yCenter-2] = True
    retArray[xCenter-5][yCenter-2] = True
    retArray[xCenter-3][yCenter-2] = True
    retArray[xCenter+3][yCenter-2] = True
    retArray[xCenter-4][yCenter-3] = True
    retArray[xCenter-3][yCenter-3] = True
    retArray[xCenter+3][yCenter-3] = True
    retArray[xCenter-2][yCenter-4] = True
    retArray[xCenter-1][yCenter-4] = True
    retArray[xCenter][yCenter-4] = True
    retArray[xCenter+1][yCenter-4] = True
    retArray[xCenter+2][yCenter-4] = True
    retArray[xCenter+3][yCenter-4] = True
    
    return retArray
    
def createC5spaceship(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    # middle piece
    retArray[xCenter-1][yCenter] = True
    retArray[xCenter-1][yCenter-1] = True
    retArray[xCenter-1][yCenter+1] = True
    retArray[xCenter+1][yCenter] = True
    retArray[xCenter+1][yCenter-1] = True
    retArray[xCenter+1][yCenter+1] = True
    # left piece
    retArray[xCenter-2][yCenter-3] = True
    retArray[xCenter-3][yCenter-3] = True
    retArray[xCenter-4][yCenter-4] = True
    retArray[xCenter-5][yCenter-3] = True
    retArray[xCenter-5][yCenter-2] = True
    retArray[xCenter-6][yCenter-2] = True
    retArray[xCenter-7][yCenter-2] = True
    retArray[xCenter-7][yCenter-1] = True
    retArray[xCenter-7][yCenter-3] = True
    retArray[xCenter-8][yCenter] = True
    retArray[xCenter-8][yCenter+2] = True
    retArray[xCenter-8][yCenter+3] = True
    retArray[xCenter-9][yCenter] = True
    retArray[xCenter-9][yCenter+2] = True
    retArray[xCenter-9][yCenter-1] = True
    retArray[xCenter-9][yCenter-2] = True
    retArray[xCenter-9][yCenter-3] = True
    retArray[xCenter-10][yCenter-3] = True
    retArray[xCenter-11][yCenter-2] = True
    retArray[xCenter-11][yCenter+1] = True
    retArray[xCenter-11][yCenter+2] = True
    retArray[xCenter-12][yCenter-2] = True
    retArray[xCenter-12][yCenter+1] = True
    retArray[xCenter-12][yCenter+2] = True
    retArray[xCenter-13][yCenter-1] = True
    retArray[xCenter-13][yCenter-2] = True
    # right piece
    retArray[xCenter+2][yCenter-3] = True
    retArray[xCenter+3][yCenter-3] = True
    retArray[xCenter+4][yCenter-4] = True
    retArray[xCenter+5][yCenter-3] = True
    retArray[xCenter+5][yCenter-2] = True
    retArray[xCenter+6][yCenter-2] = True
    retArray[xCenter+7][yCenter-2] = True
    retArray[xCenter+7][yCenter-1] = True
    retArray[xCenter+7][yCenter-3] = True
    retArray[xCenter+8][yCenter] = True
    retArray[xCenter+8][yCenter+2] = True
    retArray[xCenter+8][yCenter+3] = True
    retArray[xCenter+9][yCenter] = True
    retArray[xCenter+9][yCenter+2] = True
    retArray[xCenter+9][yCenter-1] = True
    retArray[xCenter+9][yCenter-2] = True
    retArray[xCenter+9][yCenter-3] = True
    retArray[xCenter+10][yCenter-3] = True
    retArray[xCenter+11][yCenter-2] = True
    retArray[xCenter+11][yCenter+1] = True
    retArray[xCenter+11][yCenter+2] = True
    retArray[xCenter+12][yCenter-2] = True
    retArray[xCenter+12][yCenter+1] = True
    retArray[xCenter+12][yCenter+2] = True
    retArray[xCenter+13][yCenter-1] = True
    retArray[xCenter+13][yCenter-2] = True
    
    return retArray

def createGliderGun(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    # left side
    retArray[xCenter][yCenter] = True
    retArray[xCenter+1][yCenter-2] = True
    retArray[xCenter+1][yCenter+2] = True
    retArray[xCenter+2][yCenter] = True
    retArray[xCenter+2][yCenter-1] = True
    retArray[xCenter+2][yCenter+1] = True
    retArray[xCenter+3][yCenter] = True
    retArray[xCenter-1][yCenter+3] = True
    retArray[xCenter-1][yCenter-3] = True
    retArray[xCenter-2][yCenter+3] = True
    retArray[xCenter-2][yCenter-3] = True
    retArray[xCenter-3][yCenter-2] = True
    retArray[xCenter-3][yCenter+2] = True
    retArray[xCenter-4][yCenter] = True
    retArray[xCenter-4][yCenter-1] = True
    retArray[xCenter-4][yCenter+1] = True
    retArray[xCenter-13][yCenter] = True
    retArray[xCenter-13][yCenter-1] = True
    retArray[xCenter-14][yCenter] = True
    retArray[xCenter-14][yCenter-1] = True
    #right side
    retArray[xCenter+6][yCenter-1] = True
    retArray[xCenter+6][yCenter-2] = True
    retArray[xCenter+6][yCenter-3] = True
    retArray[xCenter+7][yCenter-1] = True
    retArray[xCenter+7][yCenter-2] = True
    retArray[xCenter+7][yCenter-3] = True
    retArray[xCenter+8][yCenter-4] = True
    retArray[xCenter+8][yCenter] = True
    retArray[xCenter+10][yCenter-4] = True
    retArray[xCenter+10][yCenter-5] = True
    retArray[xCenter+10][yCenter] = True
    retArray[xCenter+10][yCenter+1] = True
    retArray[xCenter+20][yCenter-2] = True
    retArray[xCenter+20][yCenter-3] = True
    retArray[xCenter+21][yCenter-2] = True
    retArray[xCenter+21][yCenter-3] = True
    
    return retArray

def createPulsar(xCenter, yCenter):
    retArray = np.arange(CELLWIDTH*CELLHEIGHT)
    retArray.shape = (CELLWIDTH, CELLHEIGHT)
    # left side
    retArray[xCenter-1][yCenter-2] = True
    retArray[xCenter-1][yCenter-3] = True
    retArray[xCenter-1][yCenter+2] = True
    retArray[xCenter-1][yCenter+3] = True
    retArray[xCenter-2][yCenter-1] = True
    retArray[xCenter-2][yCenter-3] = True
    retArray[xCenter-2][yCenter-5] = True
    retArray[xCenter-2][yCenter+1] = True
    retArray[xCenter-2][yCenter+3] = True
    retArray[xCenter-2][yCenter+5] = True
    retArray[xCenter-3][yCenter-1] = True
    retArray[xCenter-3][yCenter-2] = True
    retArray[xCenter-3][yCenter-5] = True
    retArray[xCenter-3][yCenter-6] = True
    retArray[xCenter-3][yCenter-7] = True
    retArray[xCenter-3][yCenter+1] = True
    retArray[xCenter-3][yCenter+2] = True
    retArray[xCenter-3][yCenter+5] = True
    retArray[xCenter-3][yCenter+6] = True
    retArray[xCenter-3][yCenter+7] = True
    retArray[xCenter-5][yCenter-2] = True
    retArray[xCenter-5][yCenter-3] = True
    retArray[xCenter-5][yCenter+2] = True
    retArray[xCenter-5][yCenter+3] = True
    retArray[xCenter-6][yCenter-3] = True
    retArray[xCenter-6][yCenter+3] = True
    retArray[xCenter-7][yCenter-3] = True
    retArray[xCenter-7][yCenter+3] = True
    # right side
    retArray[xCenter+1][yCenter-2] = True
    retArray[xCenter+1][yCenter-3] = True
    retArray[xCenter+1][yCenter+2] = True
    retArray[xCenter+1][yCenter+3] = True
    retArray[xCenter+2][yCenter-1] = True
    retArray[xCenter+2][yCenter-3] = True
    retArray[xCenter+2][yCenter-5] = True
    retArray[xCenter+2][yCenter+1] = True
    retArray[xCenter+2][yCenter+3] = True
    retArray[xCenter+2][yCenter+5] = True
    retArray[xCenter+3][yCenter-1] = True
    retArray[xCenter+3][yCenter-2] = True
    retArray[xCenter+3][yCenter-5] = True
    retArray[xCenter+3][yCenter-6] = True
    retArray[xCenter+3][yCenter-7] = True
    retArray[xCenter+3][yCenter+1] = True
    retArray[xCenter+3][yCenter+2] = True
    retArray[xCenter+3][yCenter+5] = True
    retArray[xCenter+3][yCenter+6] = True
    retArray[xCenter+3][yCenter+7] = True
    retArray[xCenter+5][yCenter-2] = True
    retArray[xCenter+5][yCenter-3] = True
    retArray[xCenter+5][yCenter+2] = True
    retArray[xCenter+5][yCenter+3] = True
    retArray[xCenter+6][yCenter-3] = True
    retArray[xCenter+6][yCenter+3] = True
    retArray[xCenter+7][yCenter-3] = True
    retArray[xCenter+7][yCenter+3] = True
    
    return retArray        


            
if __name__ == '__main__':
    main()
