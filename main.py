#No importance just to ignore warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

##################      CODE STARTS HERE      #####################
import pygame
import time
from boards import *
pygame.init()

#Window, title and icons
win = pygame.display.set_mode((730, 900))
pygame.display.set_caption("SUDOKU")
icon = pygame.image.load("images/icon.png")
pygame.display.set_icon(icon)
play_button = pygame.image.load("images/play_button.png")
pause_button = pygame.image.load("images/pause_button.png")
tick_filled = pygame.image.load("images/tick_filled.png")
tick_empty = pygame.image.load("images/tick_empty.png")
#scale the icons to appropriate width, height
play_button = pygame.transform.smoothscale(play_button, (40, 40))
pause_button = pygame.transform.smoothscale(pause_button, (40, 40))
tick_filled = pygame.transform.smoothscale(tick_filled, (35, 33))
tick_empty = pygame.transform.smoothscale(tick_empty, (35, 33))

#Sound
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.play(-1)

#Colors
WHITE = (245, 245, 245)
RED = (255, 94, 94)
GREEN = (0, 212, 14)
LIGHTBLUE = (191, 218, 255)
GREY = (191, 191, 191)
BLACK = (0, 0, 0)
BLUE = (16, 187, 235)
ORANGE = (255, 220, 145)


class Board():
    def __init__(self, win, x, y, gridSize):
        self.win = win
        self.x = x
        self.y = y
        self.gridSize = gridSize
        self.cellSize = self.gridSize / 9
        self.mousePos = None
        self.initialBoard = select_board()
        self.editedBoard = [[0 for x in range(9)] for x in range(9)] #Creates a dummy board with all 0's
        self.boardChecker = [[0 for x in range(9)] for x in range(9)]
        self.noteBoard = [[0 for x in range(9)] for x in range(9)]
        self.text = pygame.font.SysFont("calibri", 60)
        self.noteText = pygame.font.SysFont("calibri", 30)
        self.keypressed = 0
        self.selected = False
        self.xPos = None
        self.yPos = None
        self.click = False
        self.notes = False

    def generateIdenticalBoards(self):
        #Creates another identical non-aliased initial board
        for i in range(9):
            for j in range(9):
                self.editedBoard[i][j] = self.initialBoard[i][j]
                self.boardChecker[i][j] = self.initialBoard[i][j]

    def drawBoard(self):
        """
        Draws the entire sudoku board on the game window
        """
        #Draws the board outline
        pygame.draw.rect(self.win, BLACK, (self.x, self.y, self.gridSize, self.gridSize), 3)

        #Draws the inbetween lines
        posChange = 0
        for i in range(9):
            if i % 3 == 0 and i != 0:
                lineWidth = 3
            else:
                lineWidth = 1
            #Draws horizontal
            pygame.draw.line(self.win, BLACK, (self.x, self.y + posChange), (self.x + self.gridSize, self.y + posChange), lineWidth)
            #Draws vertical
            pygame.draw.line(self.win, BLACK, (self.x + posChange, self.y), (self.x + posChange, self.y + self.gridSize), lineWidth)

            posChange += 70

    def mouseOnGrid(self):
        """
        Gets the mouse position when pressed inside the grid
        :return: tuple or bool
        """
        if self.mousePos[0] > self.x and self.mousePos[0] < self.x + self.gridSize:
            if self.mousePos[1] > self.y and self.mousePos[1] < self.y + self.gridSize:
                return (self.mousePos[0] - self.x, self.mousePos[1] - self.y)

        return False

    def mousePosition(self):
        """
        :return: tuple containing the index of grid selected by mouse press
        """
        if self.mouseOnGrid():
            y = int(self.mouseOnGrid()[0] // self.cellSize)
            x = int(self.mouseOnGrid()[1] // self.cellSize)
            return (x, y)

    def highlightSelected(self):
        """
        Takes input of the mouse to return the width, height of mouse inside grid
        :return: rect around the grid selected
        """
        if self.mouseOnGrid():
            self.xPos = (self.mousePosition()[1] * self.cellSize) + self.x
            self.yPos = (self.mousePosition()[0] * self.cellSize) + self.y
            if self.notes:
                pygame.draw.rect(self.win, ORANGE, (self.xPos, self.yPos, self.cellSize, self.cellSize))
            else:
                pygame.draw.rect(self.win, LIGHTBLUE, (self.xPos, self.yPos, self.cellSize, self.cellSize))

    def displayNumbers(self, win, board):
        """
        takes the passed in board list and draws number on the window
        :param win: win
        :param board: list of lists
        :return: numbers on board
        """
        y_change = 0
        x_change = 0

        for i in range(9):
            for j in range(9):
                value = self.text.render(str(board[i][j]), 1, BLACK)
                noteValue = self.noteText.render(str(self.noteBoard[i][j]), 1, BLACK)

                #when note button is not clicked
                if board[i][j] != 0 and not self.notes:
                    #draws a grey rect around the grid containing numbers when the initial board is passed
                    if board == self.initialBoard:
                        pygame.draw.rect(win, GREY, (self.x + x_change, self.y + y_change, self.cellSize, self.cellSize))
                    win.blit(value, (self.x + x_change + 19, self.y + y_change + 10))

                #when note button is clicked
                if self.notes:
                    if board == self.initialBoard and board[i][j] != 0:
                        pygame.draw.rect(win, GREY, (self.x + x_change, self.y + y_change, self.cellSize, self.cellSize))
                        win.blit(value, (self.x + x_change + 19, self.y + y_change + 10))
                    if self.noteBoard[i][j] != 0 and self.editedBoard[i][j] == 0:
                        win.blit(noteValue, (self.x + x_change + 10, self.y + y_change + 8))
                    if board == self.editedBoard and board[i][j] != 0:
                        win.blit(value, (self.x + x_change + 19, self.y + y_change + 10))

                x_change += 70

            x_change = 0
            y_change += 70

    def insertNumber(self, win):
        """
        Inserts number 1-9 in the edited board
        :param win: win
        :return: int
        """
        global isSolved, pause_time, play_time
        if self.mouseOnGrid():
            if self.initialBoard[self.mousePosition()[0]][self.mousePosition()[1]] == 0:
                if self.keypressed:
                    if self.notes:
                        self.noteBoard[self.mousePosition()[0]][self.mousePosition()[1]] = self.keypressed
                    else:
                        self.editedBoard[self.mousePosition()[0]][self.mousePosition()[1]] = self.keypressed

                    xPosition = (self.mousePosition()[1] * self.cellSize) + self.x
                    yPosition = (self.mousePosition()[0] * self.cellSize) + self.y
                    keyInput = self.text.render(str(self.keypressed), 1, BLACK)
                    noteInput = self.noteText.render(str(self.keypressed), 1, BLACK)

                    if self.notes and not isSolved:
                        win.blit(noteInput, (xPosition + 10, yPosition + 8))
                    else:
                        win.blit(keyInput, (xPosition + 19, yPosition + 10))

        #when the board is solved keeps track of the time
        if 0 not in self.editedBoard:
            pause_time = play_time

    def deleteSelected(self):
        """
        The selected grid is changed to 0
        """
        number = self.mousePosition()
        if self.notes:
            self.noteBoard[number[0]][number[1]] = 0
        else:
            self.editedBoard[number[0]][number[1]] = 0

    def isEmpty(self, board):
        """
        checks for empty space in board as 0 and returns the index as tuple else returns false
        :param board: list of lists
        :return: tuple or bool
        """
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return (row, col)

        return False

    def checkCorrect(self,board, num, row, col):
        """
        checks the inputed number with row, column and smaller grid
        :param board: list of lists
        :param num: int
        :param row: int
        :param col: int
        :return: bool
        """
        # check row
        for i in range(9):
            if board[row][i] == num and i != col:
                return False

        # check column
        for i in range(9):
            if board[i][col] == num and i != row:
                return False

        # check small grid
        ridx = row // 3
        cidx = col // 3
        for i in range(ridx * 3, (ridx * 3) + 3):
            for j in range(cidx * 3, (cidx * 3) + 3):
                if board[i][j] == num and i != row and j != col:
                    return False

        return True

    def solver(self):
        """
        implement the backtracking algorithm to solve the board
        :return: solved sudoku board
        """
        value = self.isEmpty(self.editedBoard)

        if value:
            row, col = value
        else:
            return True

        for num in range(1, 10):
            if self.checkCorrect(self.editedBoard, num, row, col):
                self.editedBoard[row][col] = num
                x = (col * self.cellSize) + self.x
                y = (row * self.cellSize) + self.y
                pygame.draw.rect(win, GREEN, (x, y, self.cellSize, self.cellSize), 5)
                board.displayNumbers(win, board.editedBoard)  # Displays the edited board after input
                board.drawBoard()
                pygame.display.update()
                pygame.time.delay(30)

                if self.solver():
                    return True

                self.editedBoard[row][col] = 0
                pygame.draw.rect(win, WHITE, (x, y, self.cellSize, self.cellSize))
                pygame.draw.rect(win, RED, (x, y, self.cellSize, self.cellSize), 5)
                board.displayNumbers(win, board.editedBoard)  # Displays the edited board after input
                board.drawBoard()
                pygame.display.update()
                pygame.time.delay(30)

        return False

    def editCheckerBoard(self):
        """
        solves the boardChecker list and used to compare with the player input
        """
        value = self.isEmpty(self.boardChecker)

        if value:
            row, col = value
        else:
            return True

        for num in range(1, 10):
            if self.checkCorrect(self.boardChecker, num, row, col):
                self.boardChecker[row][col] = num

                if self.editCheckerBoard():
                    return True

                self.boardChecker[row][col] = 0

        return False

    def checkError(self):
        """
        checks if the player input is wrong
        """
        if self.mouseOnGrid() and not self.notes:
            row, col = self.mousePosition()
            if self.editedBoard[row][col] != self.boardChecker[row][col]:
                if self.editedBoard[row][col] != 0:
                    pygame.draw.rect(win, RED, (self.xPos + 2, self.yPos + 2, self.cellSize - 4, self.cellSize - 4), 6)

    def inputBoxes(self, win):
        """
        draws the new game button and play/pause button and timer boxes
        :param win: win
        """
        global isSolved, finished
        text = pygame.font.SysFont("calibri", 30, 1)
        newGame = text.render("NEW GAME", 1, BLACK)
        note = text.render("NOTES", 1, BLACK)

        #New game button
        pygame.draw.rect(win, BLUE, (self.x, 160, 160, 40))
        pygame.draw.rect(win, BLACK, (self.x, 160, 160, 40), 3)
        win.blit(newGame, (self.x + 7, 166))

        #Timer box
        pygame.draw.rect(win, BLUE, (self.x + self.gridSize - 105, 160, 105, 40))
        pygame.draw.rect(win, BLACK, (self.x + self.gridSize - 105, 160, 105, 40), 3)

        #Note button
        pygame.draw.rect(win, BLUE, (self.x + 240, 160, 160, 40))
        pygame.draw.rect(win, BLACK, (self.x + 240, 160, 160, 40), 3)
        win.blit(note, (self.x + 255, 166))

        if self.notes and not isSolved:
            win.blit(tick_filled, (self.x + 350, 163))
        else:
            win.blit(tick_empty, (self.x + 350, 163))

        if self.click:
            win.blit(play_button, (self.x + self.gridSize - 159, 160))
        elif finished:
            win.blit(play_button, (self.x + self.gridSize - 159, 160))
        else:
            win.blit(pause_button, (self.x + self.gridSize - 159, 160))

    def newGame(self):
        """
        creates a new game with different board
        """
        global start
        self.initialBoard = select_board()
        self.generateIdenticalBoards()
        self.editCheckerBoard()
        self.notes = False
        #resets the timer
        start = time.time()

###################################################################################

def reDrawGameWindow(win):
    win.fill(WHITE)
    if board.mousePos:
        #highlights the selected cell
        board.highlightSelected()
        #checks for error
        board.checkError()
        if board.keypressed:
            #inserts number in editedBoard
            if not paused:
                board.insertNumber(win)

    board.displayNumbers(win, board.initialBoard) #Displays the initial board
    board.displayNumbers(win, board.editedBoard) #Displays the edited board after input
    #draws the entire board
    board.drawBoard()
    #draws the buttons and timer boxes
    board.inputBoxes(win)
    #blits the timer
    text = pygame.font.SysFont("calibri", 30, 1)
    time_value = text.render(time_format(play_time), 1, BLACK)
    if paused or spacePressed or finished:
        pause_value = text.render(time_format(pause_time), 1, BLACK)
        win.blit(pause_value, (board.x + board.gridSize - 85, 166))
    else:
        win.blit(time_value, (board.x + board.gridSize - 85, 166))
    #draws the info section at the top
    infoBoard(win)
    pygame.display.update()

def time_format(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    formatted = str(minute) + ": " + str(sec)
    return formatted

def pause():
    global pause_start
    pause_start = time.time()

def unpause():
   global start, pause_start
   pause_duration = time.time() - pause_start
   start += pause_duration

def infoBoard(win):
    pygame.draw.rect(win, BLUE, (board.x, 15, board.gridSize, 130))
    pygame.draw.rect(win, BLACK, (board.x, 15, board.gridSize, 130), 3)
    text = pygame.font.SysFont("arial", 22, 1)
    info1 = text.render("> Normal Sudoku rules apply.", 1, BLACK)
    info2 = text.render('> Left click on cells to input numbers, press "Notes" to take notes.', 1, BLACK)
    info3 = text.render('> Press "Delete" or "Backspace" key to remove an input.', 1, BLACK)
    info4 = text.render('> Press "New Game" button to start a new sudoku game.', 1, BLACK)
    info5 = text.render('> PRESS "SPACE" TO WITNESS THE BOARD SOLVE ITSELF!', 1, BLACK)
    win.blit(info1, (board.x + 7, 17))
    win.blit(info2, (board.x + 7, 42))
    win.blit(info3, (board.x + 7, 67))
    win.blit(info4, (board.x + 7, 92))
    win.blit(info5, (board.x + 7, 117))

###################################################################################

board = Board(win, 50, 220, 630)
board.generateIdenticalBoards()
board.editCheckerBoard()
spacePressed = isSolved = paused = finished = False
mouseClicked = notesClicked = 0
pause_start = 0
start = time.time()
running = True
while running:
    play_time = round(time.time() - start)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.mousePos = pygame.mouse.get_pos()

                #for play/pause button
                if not finished:
                    if board.mousePos[0] > board.x + board.gridSize - 159 and board.mousePos[0] < board.x + board.gridSize - 124:
                        if board.mousePos[1] > 160 and board.mousePos[1] < 200:
                            if mouseClicked % 2 == 0:
                                board.click = paused = True
                                pause_time = play_time
                                pause()
                            else:
                                board.click = paused = False
                                unpause()
                                pygame.time.delay(150)
                            mouseClicked += 1

                #for new game button
                if board.mousePos[0] > board.x and board.mousePos[0] < board.x + 160:
                    if board.mousePos[1] > 160 and board.mousePos[1] < 200:
                        board.newGame()
                        spacePressed = isSolved = False
                        notesClicked = 0
                        board.noteBoard = [[0 for x in range(9)] for x in range(9)]

                #for notes button
                if board.mousePos[0] > board.x + 240 and board.mousePos[0] < board.x + 400:
                    if board.mousePos[1] > 160 and board.mousePos[1] < 200:
                        if not isSolved:
                            if notesClicked % 2 == 0:
                                board.notes = True
                            else:
                                board.notes = False
                            notesClicked += 1

        if event.type == pygame.KEYDOWN:
            if not isSolved:
                if event.key == pygame.K_1:
                    board.keypressed = 1
                if event.key == pygame.K_2:
                    board.keypressed = 2
                if event.key == pygame.K_3:
                    board.keypressed = 3
                if event.key == pygame.K_4:
                    board.keypressed = 4
                if event.key == pygame.K_5:
                    board.keypressed = 5
                if event.key == pygame.K_6:
                    board.keypressed = 6
                if event.key == pygame.K_7:
                    board.keypressed = 7
                if event.key == pygame.K_8:
                    board.keypressed = 8
                if event.key == pygame.K_9:
                    board.keypressed = 9

                if event.key == pygame.K_SPACE:
                    # resets all previous inputs
                    for i in range(9):
                        for j in range(9):
                            board.editedBoard[i][j] = board.initialBoard[i][j]

                    board.notes = False
                    reDrawGameWindow(win)
                    board.solver()
                    spacePressed = isSolved = finished = True
                    board.notes = False
                    pause_time = play_time

            if not spacePressed:
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    if board.mouseOnGrid():
                        board.deleteSelected()

    if board.keypressed != 0:
        board.selected = True

    if board.editedBoard == board.boardChecker:
        finished = True
    else:
        finished = False

    reDrawGameWindow(win)
    board.keypressed = 0

pygame.quit()
