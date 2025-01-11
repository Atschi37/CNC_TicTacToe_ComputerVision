import Recognise_Game
import threading

game = Recognise_Game.TicTacToe()

def is_winner(board, player):
    # Check rows for a win
    for i, row in enumerate(board):
        if all([cell == player for cell in row]):
            return True, f"Row {i}"
    # Check columns for a win
    for col in range(3):
        if all([board[row][col] == player for row in range(3)]):
            return True, f"Column {col}"
    # Check diagonals for a win
    if all([board[i][i] == player for i in range(3)]):
        return True, "Main diagonal"
    if all([board[i][2-i] == player for i in range(3)]):
        return True, "Anti-diagonal"
    return False, None

def minimax(board, depth, is_maximizing):
    winner, _ = is_winner(board, 'T')
    if winner:
        return 1
    winner, _ = is_winner(board, 'O')
    if winner:
        return -1
    if all([cell != '_' for row in board for cell in row]):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == '_':
                    board[i][j] = 'T'
                    score = minimax(board, depth + 1, False)
                    board[i][j] = '_'
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == '_':
                    board[i][j] = 'O'
                    score = minimax(board, depth + 1, True)
                    board[i][j] = '_'
                    best_score = min(score, best_score)
        return best_score

def find_best_move(board):
    best_move = None
    best_score = -float('inf')
    for i in range(3):
        for j in range(3):
            if board[i][j] == '_':
                board[i][j] = 'T'
                score = minimax(board, 0, False)
                board[i][j] = '_'
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    return best_move

def start_game():
    game.main()

threading.Thread(target=start_game).start()
print("Game started in a separate thread.")
while True:
    input("Press Enter to get current board.")
    current_board = game.get_current_board()
    print(current_board)
    winner, win_type = is_winner(current_board, 'T')
    if winner:
        print(f"'T' wins! {win_type}")
    else:
        winner, win_type = is_winner(current_board, 'O')
        if winner:
            print(f"'O' wins! {win_type}")
        else:
            best_move = find_best_move(current_board)
            print(f"Best move for 'T' is: {best_move}")
