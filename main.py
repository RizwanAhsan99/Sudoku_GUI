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
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
play_button = pygame.image.load("play_button.png")
play_button = pygame.transform.smoothscale(play_button, (40, 40))
pause_button = pygame.image.load("pause_button.png")
pause_button = pygame.transform.smoothscale(pause_button, (40, 40))

#Sound
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.play(-1)

#Colors
WHITE = (245, 245, 245)
RED = (255, 94, 94)
GREEN = (0, 212, 14)
BLUE = (191, 218, 255)
GREY = (191, 191, 191)
BLACK = (0, 0, 0)
BUTTON = (16, 187, 235)


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
        self.text = pygame.font.SysFont("calibri", 60)
        self.keypressed = 0
        self.selected = False
        self.xPos = None
        self.yPos = None
        self.click = False
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
            pygame.draw.rect(self.win, BLUE, (self.xPos, self.yPos, self.cellSize, self.cellSize))

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
                if board[i][j] != 0:
                    value = self.text.render(str(board[i][j]), 1, BLACK)
                    #draws a grey rect around the grid containing numbers when the initial board is passed
                    if board == self.initialBoard:
                        pygame.draw.rect(win, GREY, (self.x + x_change, self.y + y_change, self.cellSize, self.cellSize))
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
        if self.mouseOnGrid():
            if self.initialBoard[self.mousePosition()[0]][self.mousePosition()[1]] == 0:
                if self.keypressed:
                    self.editedBoard[self.mousePosition()[0]][self.mousePosition()[1]] = self.keypressed
                    xPosition = (self.mousePosition()[1] * self.cellSize) + self.x
                    yPosition = (self.mousePosition()[0] * self.cellSize) + self.y
                    keyInput = self.text.render(str(self.keypressed), 1, BLACK)
                    win.blit(keyInput, (xPosition + 19, yPosition + 10))

    def deleteSelected(self):
        """
        The selected grid is changed to 0
        """
        number = self.mousePosition()
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
                pygame.time.delay(20)

                if self.solver():
                    return True

                self.editedBoard[row][col] = 0
                pygame.draw.rect(win, WHITE, (x, y, self.cellSize, self.cellSize))
                pygame.draw.rect(win, RED, (x, y, self.cellSize, self.cellSize), 5)
                board.displayNumbers(win, board.editedBoard)  # Displays the edited board after input
                board.drawBoard()
                pygame.display.update()
                pygame.time.delay(20)

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

    def checkInputIfCorrect(self):
        """
        checks the player input with the solved boardChecker list
        """
        row, col = self.mousePosition()
        if self.editedBoard[row][col] != self.boardChecker[row][col]:
            if self.editedBoard[row][col] != 0:
                pygame.draw.rect(win, RED, (self.xPos, self.yPos, self.cellSize, self.cellSize), 4)

    def inputBoxes(self, win):
        text = pygame.font.SysFont("calibri", 30, 1)
        newGame = text.render("NEW GAME", 1, BLACK)

        pygame.draw.rect(win, BUTTON, (self.x + 25, 160, 160, 40))
        pygame.draw.rect(win, BLACK, (self.x + 25, 160, 160, 40), 3)
        pygame.draw.rect(win, BUTTON, (self.x + self.gridSize - 105, 160, 105, 40))
        pygame.draw.rect(win, BLACK, (self.x + self.gridSize - 105, 160, 105, 40), 3)
        win.blit(newGame, (self.x + 32, 166))

        if self.click:
            win.blit(play_button, (self.x + self.gridSize - 159, 160))
        else:
            win.blit(pause_button, (self.x + self.gridSize - 159, 160))


def reDrawGameWindow(win):
    win.fill(WHITE)
    if board.mousePos:
        board.highlightSelected()
        if showError:
            board.checkInputIfCorrect()
        if board.keypressed:
            board.insertNumber(win)

    board.displayNumbers(win, board.initialBoard) #Displays the initial board
    board.displayNumbers(win, board.editedBoard) #Displays the edited board after input
    board.drawBoard()
    board.inputBoxes(win)
    text = pygame.font.SysFont("calibri", 30, 1)
    value = text.render(time_format(play_time), 1, BLACK)
    win.blit(value, (board.x + board.gridSize - 80, 166))
    pygame.display.update()

def time_format(secs):
    sec = secs % 60
    minute = secs // 60
    hour = minute // 60

    formatted = str(minute) + " : " + str(sec)
    return formatted


board = Board(win, 50, 220, 630)
board.editCheckerBoard()
spacePressed = showError = isSolved = False
cPressed = mouseClicked = 0
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
                if board.mousePos[0] > board.x + board.gridSize - 159 and board.mousePos[0] < board.x + board.gridSize - 124:
                    if board.mousePos[1] > 160 and board.mousePos[1] < 200:
                        if mouseClicked % 2 == 0:
                            board.click = True
                        else:
                            board.click = False
                        mouseClicked += 1

            if event.button == 2:
                pass

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

                    board.solver()
                    spacePressed = True
                    isSolved = True

                if event.key == pygame.K_c:
                    cPressed += 1

                    if cPressed % 2 == 0:
                        showError = False
                    else:
                        showError = True

            if not spacePressed:
                if event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    if board.mouseOnGrid():
                        board.deleteSelected()

    if board.keypressed != 0:
        board.selected = True

    reDrawGameWindow(win)
    board.keypressed = 0

pygame.quit()
