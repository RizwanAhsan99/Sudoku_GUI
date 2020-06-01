from boards import *

#prints the board with the stylized formatting
def show_board(board):
    horizontal = True
    print(" -----------------------")
    
    for row in range(len(board)):
        for col in range(len(board[0])):
            if row % 3 == 0 and row != 0 and horizontal:
                print("|-------|-------|-------|")
                horizontal = False
            
            if col == 0:
                print("| ", end = "")
                
            if col % 3 == 0 and col != 0:
                print("| " + str(board[row][col]) + " ", end = "")
            elif col == 8:
                print(str(board[row][col]) + " |")
            else:
                print(board[row][col], end = " ")
            
            if row == 5 and col == 8:
                horizontal = True

    return " -----------------------"

def isEmpty(board):
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 0:
                return [row, col]
    
    return False

def correct(board, num, row, col):
    #check row
    for i in range(len(board)):
        if board[row][i] == num and i != col:
            return False

    #check column
    for i in range(len(board)):
        if board[i][col] == num and i != row:
            return False
                
    #check small grid
    ridx = row // 3
    cidx = col // 3
    for i in range(ridx*3, (ridx*3)+3):
        for j in range(cidx*3, (cidx*3)+3):
            if board[i][j] == num and i != row and j != col:
                return False

    return True

#backtracking algorithm implemented
def main(board):
    value = isEmpty(board)

    if value:
        row, col = value
    else:
        return True
    
    for num in range(1, 10):
        if correct(board, num, row, col):
            board[row][col] = num

            if main(board):
                return True
            
            board[row][col] = 0
        
    return False

board = select_board()
print("\nThe board before being solved.")
print(show_board(board))
main(board)
print("\nThe board after being solved!")
print(show_board(board))