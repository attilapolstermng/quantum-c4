import pygame
import sys
import random

ROWS, COLS = 6, 7
CELL_SIZE = 80
RADIUS = CELL_SIZE // 2 - 5
WIDTH, HEIGHT = COLS * CELL_SIZE, (ROWS + 1) * CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
YELLOW = (220, 220, 0)
PINK = (200, 200, 255)
BG = (21, 24, 26)

def create_board():
    return [[" " for _ in range(COLS)] for _ in range(ROWS)]

def get_available_row(board, col):
    for row in reversed(range(ROWS)):
        if board[row][col] == " ":
            return row
    return None

def apply_gravity(board):
    for c in range(COLS):
        stack = []
        for r in range(ROWS-1, -1, -1):
            if board[r][c] != " ":
                stack.append(board[r][c])
        for r in range(ROWS-1, -1, -1):
            if stack:
                board[r][c] = stack.pop(0)
            else:
                board[r][c] = " "

def check_win(board, piece):
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c+i] == piece for i in range(4)):
                return True
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r+i][c] == piece for i in range(4)):
                return True
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r+i][c+i] == piece for i in range(4)):
                return True
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r+i][c-i] == piece for i in range(4)):
                return True
    return False

def measure_superpositions(board, superpos_list):
    for (r, c) in superpos_list:
        board[r][c] = random.choice(["X", "O"])
    superpos_list.clear()
    apply_gravity(board)

def draw_board(screen, board, winner_text=None):
    screen.fill(BG)
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE + CELL_SIZE // 2
            y = (r+1) * CELL_SIZE + CELL_SIZE // 2
            if board[r][c] == "X":
                color = RED
            elif board[r][c] == "O":
                color = YELLOW
            elif board[r][c] == "?":
                color = PINK
            else:
                color = WHITE
            pygame.draw.circle(screen, color, (x, y), RADIUS)
            pygame.draw.circle(screen, BLACK, (x, y), RADIUS, 2)
    if winner_text:
        font = pygame.font.SysFont(None, 60, bold=True)
        text = font.render(winner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH//2, 60))
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(40, 20))
        screen.blit(text, text_rect)
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quantum-Duell")
    font = pygame.font.SysFont(None, 48)
    board = create_board()
    current_player = "X"
    game_over = False
    superpos_list = []
    moves_since_last_measure = 0
    MEASURE_AFTER = 3  # oder 5

    winner_text = None

    while True:
        draw_board(screen, board, winner_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col = x // CELL_SIZE
                row = get_available_row(board, col)
                if row is not None:
                    board[row][col] = "?"
                    superpos_list.append((row, col))
                    moves_since_last_measure += 1
                    if moves_since_last_measure >= MEASURE_AFTER:
                        measure_superpositions(board, superpos_list)
                        moves_since_last_measure = 0
                        # Nach Messung: Sieg prüfen
                        if check_win(board, "X"):
                            winner_text = "🔴 gewinnt!"
                            game_over = True
                        elif check_win(board, "O"):
                            winner_text = "🟡 gewinnt!"
                            game_over = True
                        elif all(board[0][c] != " " for c in range(COLS)):
                            winner_text = "Unentschieden!"
                            game_over = True
                    current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    main()