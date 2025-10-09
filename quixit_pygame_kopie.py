import pygame
import sys
 
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backend = Aer.get_backend("aer_simulator")
#backend = service.backend("ibm_brisbane")


ROWS, COLS = 6, 7
CELL_SIZE = 80
RADIUS = CELL_SIZE // 2 - 5
BASE_HEIGHT = 720
BASE_WIDTH = int(BASE_HEIGHT * 16 / 9)
CELL_SIZE = BASE_HEIGHT // (ROWS + 1)
WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS + 1) * CELL_SIZE
BTN_WIDTH = 120
BTN_HEIGHT = 32
WINDOW_WIDTH = BASE_WIDTH

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

def draw_board(screen, board, measure_uses, winner_text=None, current_player=None):
    screen.fill(BG)
    gradient_height = 180
    gradient_surface = pygame.Surface((WINDOW_WIDTH, gradient_height), pygame.SRCALPHA)
    grad_color = (220, 220, 0) if current_player == "O" else (220, 0, 0)
    for y in range(gradient_height):
        alpha = int(120 * (1 - y / gradient_height))
        pygame.draw.rect(gradient_surface, grad_color + (alpha,), (0, gradient_height - y - 1, WINDOW_WIDTH, 1))
    screen.blit(gradient_surface, (0, HEIGHT - gradient_height))
    board_offset_x = (WINDOW_WIDTH - WIDTH) // 2
    for r in range(ROWS):
        for c in range(COLS):
            x = board_offset_x + c * CELL_SIZE + CELL_SIZE // 2
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
    button_rects = {}
    font_btn = pygame.font.SysFont(None, 22)
    btn_x_x = board_offset_x - BTN_WIDTH - 30
    btn_x_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_x = pygame.Rect(btn_x_x, btn_x_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(screen, (220, 120, 120), btn_x)
    text_x = font_btn.render(f"Messungen: ({3-measure_uses['X']} übrig)", True, (255, 255, 255))
    text_x_rect = text_x.get_rect(center=(btn_x.x + BTN_WIDTH//2, btn_x.y + BTN_HEIGHT + 16))
    screen.blit(text_x, text_x_rect)
    button_rects["X"] = btn_x
    btn_o_x = board_offset_x + WIDTH + 30
    btn_o_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_o = pygame.Rect(btn_o_x, btn_o_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(screen, (220, 220, 120), btn_o)
    text_o = font_btn.render(f"Messungen: ({3-measure_uses['O']} übrig)", True, (255, 255, 255))
    text_o_rect = text_o.get_rect(center=(btn_o.x + BTN_WIDTH//2, btn_o.y + BTN_HEIGHT + 16))
    screen.blit(text_o, text_o_rect)
    button_rects["O"] = btn_o
    if winner_text:
        font = pygame.font.SysFont(None, 60, bold=True)
        text = font.render(winner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH//2, 60))
        pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(40, 20))
        screen.blit(text, text_rect)
    pygame.display.flip()
    return button_rects

def measure_superpositions(board, superpos_pairs):
    for group in superpos_pairs:
        positions = group[:-1]
        player = group[-1]
        n = len(positions)
        if n == 2:
            result = qiskit_measure(2)
            if result[0] == result[1]:
                result = result[0] + ('1' if result[0] == '0' else '0')
            for idx, pos in enumerate(positions):
                r, c = pos
                board[r][c] = player if result[idx] == '0' else " "
        else:
            result = qiskit_measure(n)
            for idx, pos in enumerate(positions):
                r, c = pos
                board[r][c] = player if result[idx] == '0' else " "
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

N_SUPERPOS = 2
def qiskit_measure(n_qubits=None):
    n = n_qubits if n_qubits is not None else N_SUPERPOS
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
        qc.measure(i, i)
    job = backend.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts()
    key = list(counts.keys())[0]
    return key.zfill(n)

def main(n_superpos=2):
    turn_count = 0
    global N_SUPERPOS
    N_SUPERPOS = n_superpos
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT))
    pygame.display.set_caption("Quixit Pygame")
    board = create_board()
    current_player = "X"
    game_over = False

    superpos_count = 0
    last_superpos_cols = []
    superpos_groups = []
    superpos_temp = []
    measure_uses = {"X": 0, "O": 0}
    MAX_MEASURE = 3

    while True:
        winner_text = None
        screen.fill(BG)
        button_rects = draw_board(screen, board, measure_uses, winner_text, current_player)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                btn = button_rects[current_player]
                if btn.collidepoint(x, y) and measure_uses[current_player] < MAX_MEASURE:
                    if superpos_count > 0:
                        continue
                    measure_superpositions(board, superpos_groups)
                    apply_gravity(board)
                    measure_uses[current_player] += 1
                    x_win = check_win(board, "X")
                    o_win = check_win(board, "O")
                    if x_win and o_win:
                        winner_text = "Rot gewinnt!" if current_player == "X" else "🟡 gewinnt!"
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
                    current_player = "O" if current_player == "X" else "X"
                    draw_board(screen, board, measure_uses, winner_text, current_player)
                    continue
                board_offset_x = (WINDOW_WIDTH - WIDTH) // 2
                col = (x - board_offset_x) // CELL_SIZE
                if 0 <= col < COLS:
                    row = get_available_row(board, col)
                    if row is not None:
                        if event.button == 1:
                            if col in last_superpos_cols:
                                continue
                            last_superpos_cols.append(col)
                            board[row][col] = current_player + "?"
                            superpos_temp.append((row, col))
                            superpos_count += 1
                            turn_count += 1
                            if superpos_count == N_SUPERPOS:
                                if len(set(last_superpos_cols)) == N_SUPERPOS:
                                    superpos_groups.append(tuple(superpos_temp + [current_player]))
                                    superpos_temp = []
                                    superpos_count = 0
                                    last_superpos_cols = []
                                    current_player = "O" if current_player == "X" else "X"
                                else:
                                    r_last, c_last = superpos_temp.pop()
                                    board[r_last][c_last] = " "
                                    superpos_count -= 1
                                    last_superpos_cols.pop()
                            if turn_count % (N_SUPERPOS*2) == 0 and superpos_groups and measure_uses["X"] >= MAX_MEASURE and measure_uses["O"] >= MAX_MEASURE:
                                if superpos_temp:
                                    superpos_groups.append(tuple(superpos_temp + [current_player]))
                                    superpos_temp = []
                                    superpos_count = 0
                                    last_superpos_cols = []
                                measure_superpositions(board, superpos_groups)
                                apply_gravity(board)
            if event.type == pygame.KEYDOWN and not game_over:
                if pygame.K_1 <= event.key <= pygame.K_7:
                    col = event.key - pygame.K_1
                    if 0 <= col < COLS:
                        row = get_available_row(board, col)
                        if row is not None:
                            if col in last_superpos_cols:
                                continue
                            last_superpos_cols.append(col)
                            board[row][col] = current_player + "?"
                            superpos_temp.append((row, col))
                            superpos_count += 1
                            turn_count += 1
                            if superpos_count == N_SUPERPOS:
                                if len(set(last_superpos_cols)) == N_SUPERPOS:
                                    superpos_groups.append(tuple(superpos_temp + [current_player]))
                                    superpos_temp = []
                                    superpos_count = 0
                                    last_superpos_cols = []
                                    current_player = "O" if current_player == "X" else "X"
                                else:
                                    r_last, c_last = superpos_temp.pop()
                                    board[r_last][c_last] = " "
                                    superpos_count -= 1
                                    last_superpos_cols.pop()
                            if turn_count % (N_SUPERPOS*2) == 0 and superpos_groups and measure_uses["X"] >= MAX_MEASURE and measure_uses["O"] >= MAX_MEASURE:
                                if superpos_temp:
                                    superpos_groups.append(tuple(superpos_temp + [current_player]))
                                    superpos_temp = []
                                    superpos_count = 0
                                    last_superpos_cols = []
                                measure_superpositions(board, superpos_groups)
                                apply_gravity(board)
                if event.key == pygame.K_RETURN and measure_uses[current_player] < MAX_MEASURE:
                    if superpos_count > 0:
                        info_text = f"Setze zuerst alle {N_SUPERPOS} Superpositionssteine!"
                        continue
                    if superpos_temp:
                        superpos_groups.append(tuple(superpos_temp + [current_player]))
                        superpos_temp = []
                        superpos_count = 0
                        last_superpos_cols = []
                    measure_superpositions(board, superpos_groups)
                    apply_gravity(board)
                    measure_uses[current_player] += 1
                    x_win = check_win(board, "X")
                    o_win = check_win(board, "O")
                    if x_win and o_win:
                        winner_text = "Rot gewinnt!" if current_player == "X" else "🟡 gewinnt!"
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
                    current_player = "O" if current_player == "X" else "X"
                    draw_board(screen, board, measure_uses, winner_text, current_player)
        if check_win(board, "X"):
            winner_text = "Rot gewinnt!"
            game_over = True
        elif check_win(board, "O"):
            winner_text = "Gelb gewinnt!"
            game_over = True
        elif all(board[0][c] != " " for c in range(COLS)):
            winner_text = "Unentschieden!"
            game_over = True

        button_rects = draw_board(screen, board, measure_uses, winner_text, current_player)
        if game_over:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        import subprocess, os
                        menu_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pygame-q-c4/quixit_main.py'))
                        subprocess.Popen([sys.executable, menu_path])
                        sys.exit()
                button_rects = draw_board(screen, board, measure_uses, winner_text, current_player)
                pygame.time.wait(100)

if __name__ == "__main__":
    import sys
    n_superpos = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    main(n_superpos)