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
PINK = (255, 182, 193)
LIGHT_YELLOW = (255, 255, 179)
BG = (21, 24, 26)

def create_board():
    return [[" " for _ in range(COLS)] for _ in range(ROWS)]

def get_available_row(board, col):
    for row in reversed(range(ROWS)):
        if board[row][col] == " ":
            return row
    return None

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

def draw_board(screen, board, measure_uses, winner_text=None):
    screen.fill(BG)
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE + CELL_SIZE // 2
            y = (r+1) * CELL_SIZE + CELL_SIZE // 2
            if board[r][c] == "X":
                color = RED
            elif board[r][c] == "O":
                color = YELLOW
            elif board[r][c] == "X?":
                color = PINK
            elif board[r][c] == "O?":
                color = LIGHT_YELLOW
            else:
                color = WHITE
            pygame.draw.circle(screen, color, (x, y), RADIUS)
            pygame.draw.circle(screen, BLACK, (x, y), RADIUS, 2)
    # --- Zwei Buttons zeichnen ---
    button_rects = {}
    font_btn = pygame.font.SysFont(None, 28)
    btn_x = pygame.Rect(WIDTH//4 - 100, 10, 200, 40)
    btn_o = pygame.Rect(3*WIDTH//4 - 100, 10, 200, 40)
    pygame.draw.rect(screen, (220, 120, 120), btn_x)
    pygame.draw.rect(screen, (220, 220, 120), btn_o)
    text_x = font_btn.render(f"X messen ({3-measure_uses['X']} übrig)", True, (0, 0, 0))
    text_o = font_btn.render(f"O messen ({3-measure_uses['O']} übrig)", True, (0, 0, 0))
    screen.blit(text_x, (btn_x.x + 10, btn_x.y + 5))
    screen.blit(text_o, (btn_o.x + 10, btn_o.y + 5))
    button_rects["X"] = btn_x
    button_rects["O"] = btn_o
    # Gewinner- oder Unentschieden-Text anzeigen
    if winner_text:
        font = pygame.font.SysFont(None, 60, bold=True)
        text = font.render(winner_text, True, (255, 255, 255))
        # Hintergrundbalken zeichnen
        text_rect = text.get_rect(center=(WIDTH//2, 60))
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(40, 20))
        screen.blit(text, text_rect)
    pygame.display.flip()
    return button_rects

def measure_superpositions(board, superpos_pairs):
    for (pos1, pos2, player) in superpos_pairs:
        if random.choice([True, False]):
            # pos1 wird echt, pos2 verschwindet
            r1, c1 = pos1
            r2, c2 = pos2
            board[r1][c1] = player
            board[r2][c2] = " "
        else:
            # pos2 wird echt, pos1 verschwindet
            r1, c1 = pos1
            r2, c2 = pos2
            board[r1][c1] = " "
            board[r2][c2] = player
    superpos_pairs.clear()

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quixit Pygame")
    font = pygame.font.SysFont(None, 48)
    board = create_board()
    current_player = "X"
    game_over = False

    superpos_count = 0
    last_superpos_col = None  # NEU: Merkt sich die Spalte des ersten Steins
    superpos_pairs = []  # Liste von [(r1, c1), (r2, c2), "X" oder "O"]
    superpos_temp = []   # Zwischenspeicher für aktuellen Zug
    measure_uses = {"X": 0, "O": 0}
    MAX_MEASURE = 3

    while True:
        winner_text = None
        button_rects = draw_board(screen, board, measure_uses, winner_text)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                # --- Button-Klick prüfen ---
                btn = button_rects[current_player]
                if btn.collidepoint(x, y) and measure_uses[current_player] < MAX_MEASURE:
                    measure_superpositions(board, superpos_pairs)
                    apply_gravity(board)
                    measure_uses[current_player] += 1
                    messender_spieler = current_player  # <--- NEU
                    # Sieg-Check nach Messung:
                    x_win = check_win(board, "X")
                    o_win = check_win(board, "O")
                    if x_win and o_win:
                        winner_text = "Rot gewinnt!" if messender_spieler == "X" else "🟡 gewinnt!"
                        game_over = True
                    elif x_win:
                        winner_text = "Rot gewinnt!"
                        game_over = True
                    elif o_win:
                        winner_text = "Gelb gewinnt!"
                        game_over = True
                    elif all(board[0][c] != " " for c in range(COLS)):
                        winner_text = "Unentschieden!"
                        game_over = True
                    continue
                col = x // CELL_SIZE
                row = get_available_row(board, col)
                if row is not None:
                    if event.button == 1:
                        # Superpositionsstein setzen
                        if superpos_count == 1 and col == last_superpos_col:
                            continue
                        board[row][col] = current_player + "?"
                        superpos_temp.append((row, col))
                        superpos_count += 1
                        if superpos_count == 1:
                            last_superpos_col = col
                        if superpos_count == 2:
                            superpos_pairs.append((superpos_temp[0], superpos_temp[1], current_player))
                            superpos_temp = []
                            superpos_count = 0
                            last_superpos_col = None
                            current_player = "O" if current_player == "X" else "X"
        if check_win(board, "X"):
            winner_text = "Rot gewinnt!"
            game_over = True
        elif check_win(board, "O"):
            winner_text = "Gelb gewinnt!"
            game_over = True
        elif all(board[0][c] != " " for c in range(COLS)):
            winner_text = "Unentschieden!"
            game_over = True

        button_rects = draw_board(screen, board, measure_uses, winner_text)
        if game_over:
            pygame.time.wait(3000)
            return

if __name__ == "__main__":
    main()