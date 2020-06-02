#No importance just to ignore warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

##################      CODE STARTS HERE      #####################
import pygame
from boards import *
pygame.init()

win = pygame.display.set_mode((730, 900))
pygame.display.set_caption("SUDOKU")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

#sound
pygame.mixer.music.load("bg_music.mp3")
pygame.mixer.music.play(-1)

#Colors
WHITE = (245, 245, 245)
RED = (255, 94, 94)
GREEN = (0, 212, 14)
BLUE = (191, 218, 255)
GREY = (191, 191, 191)
BLACK = (0, 0, 0)


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
        :return: tuple or boolean
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
        :return: blue rect around the grid selected
        """
        if self.mouseOnGrid():
            self.xPos = (self.mousePosition()[1] * self.cellSize) + self.x
            self.yPos = (self.mousePosition()[0] * self.cellSize) + self.y
            pygame.draw.rect(self.win, BLUE, (self.xPos, self.yPos, self.cellSize, self.cellSize))

    def displayNumbers(self, win, board):
        y_change = 0
        x_change = 0

        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    value = self.text.render(str(board[i][j]), 1, BLACK)
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
        :return: number in the grid
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
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    return (row, col)

        return False

    def checkCorrect(self,board, num, row, col):
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

    def checkIfCorrect(self):
        row, col = self.mousePosition()
        if self.editedBoard[row][col] != self.boardChecker[row][col]:
            if self.editedBoard[row][col] != 0:
                pygame.draw.rect(win, RED, (self.xPos, self.yPos, self.cellSize, self.cellSize), 4)

def reDrawGameWindow(win):
    win.fill(WHITE)
    if board.mousePos:
        board.highlightSelected()
        if showError:
            board.checkIfCorrect()
        if board.keypressed:
            board.insertNumber(win)

    board.displayNumbers(win, board.initialBoard) #Displays the initial board
    board.displayNumbers(win, board.editedBoard) #Displays the edited board after input
    board.drawBoard()
    pygame.display.update()


board = Board(win, 50, 220, 630)
board.editCheckerBoard()
spacePressed = showError = isSolved = False
cPressed = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            board.mousePos = pygame.mouse.get_pos()

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
