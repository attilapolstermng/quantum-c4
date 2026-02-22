import pygame
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"

def load_images(target_size):
    imgs = {}
    def load(name):
        # try assets/ first, then script directory so images can live next to the script
        candidates = [ASSETS, Path(__file__).resolve().parent]
        for d in candidates:
            p = d / name
            if p.exists():
                im = pygame.image.load(str(p)).convert_alpha()
                return pygame.transform.smoothscale(im, target_size)
        return None

    imgs['restart'] = load("restart1.png") or load("restart.png")
    imgs['home'] = load("home.png")
    imgs['measure_x'] = load("measure_x.png")
    imgs['measure_o'] = load("measure_o.png")
    return imgs

# container for loaded images (filled after pygame.init())
IMAGES = {}

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backend = Aer.get_backend("aer_simulator")
#backend = service.backend("ibm_brisbane")


ROWS, COLS = 6, 7
# base/original sizes (used to compute a single uniform scale)
ORIGINAL_CELL = 80
ORIGINAL_WIDTH = COLS * ORIGINAL_CELL     # 7 * 80 = 560
ORIGINAL_HEIGHT = (ROWS + 1) * ORIGINAL_CELL  # 7 * 80 = 560
ORIGINAL_GRADIENT_HEIGHT = 180
ORIGINAL_BTN_WIDTH = 120
ORIGINAL_BTN_HEIGHT = 32
ORIGINAL_FONT_SIZE = 22

# current (derived) sizes - initialized to originals or sensible defaults
CELL_SIZE = ORIGINAL_CELL
WIDTH = ORIGINAL_WIDTH
HEIGHT = 720
BTN_WIDTH = ORIGINAL_BTN_WIDTH
BTN_HEIGHT = ORIGINAL_BTN_HEIGHT
WINDOW_WIDTH = 1280
# small visual scale adjustments (make board area and buttons slightly smaller)
BOARD_VISUAL_SCALE = 0.95  # scale applied to the cell size for visual spacing
BTN_VISUAL_SCALE = 0.9     # scale applied to button sizes
HOLE_SCALE = 0.85         # scale applied to stone hole radius (make holes smaller)
RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))

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

def draw_board(screen, board, measure_uses, winner_text=None, current_player=None, player_names=None):
    screen.fill(BG)
    # gradient and fonts scale with CELL_SIZE so proportions stay the same
    gradient_height = max(8, int(ORIGINAL_GRADIENT_HEIGHT * CELL_SIZE / ORIGINAL_CELL))
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
    scale = CELL_SIZE / ORIGINAL_CELL
    font_btn = pygame.font.SysFont("helvetica", max(12, int(ORIGINAL_FONT_SIZE * scale)))
    btn_x_x = board_offset_x - BTN_WIDTH - int(30 * scale)
    btn_x_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_x = pygame.Rect(btn_x_x, btn_x_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(screen, (220, 120, 120), btn_x)
    name_x = player_names['X'] if player_names and 'X' in player_names else 'X'
    text_x = font_btn.render(f"{name_x}: ({3-measure_uses['X']} übrig)", True, (255, 255, 255))
    text_x_rect = text_x.get_rect(center=(btn_x.x + BTN_WIDTH//2, btn_x.y + BTN_HEIGHT + int(16 * scale)))
    screen.blit(text_x, text_x_rect)
    button_rects["X"] = btn_x
    btn_o_x = board_offset_x + WIDTH + int(30 * scale)
    btn_o_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_o = pygame.Rect(btn_o_x, btn_o_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(screen, (220, 220, 120), btn_o)
    name_o = player_names['O'] if player_names and 'O' in player_names else 'O'
    text_o = font_btn.render(f"{name_o}: ({3-measure_uses['O']} übrig)", True, (255, 255, 255))
    text_o_rect = text_o.get_rect(center=(btn_o.x + BTN_WIDTH//2, btn_o.y + BTN_HEIGHT + int(16 * scale)))
    screen.blit(text_o, text_o_rect)
    button_rects["O"] = btn_o
    if winner_text:
        # use Helvetica (fallbacks handled by pygame) and center on window width
        font = pygame.font.SysFont("helvetica", max(30, int(60 * scale)), bold=True)
        text = font.render(winner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH//2, int(60 * scale)))
        screen.blit(text, text_rect)
    # bottom-center small buttons: restart and home (change names)
    icon_size = max(28, int(28 * scale))
    center_x = WINDOW_WIDTH // 2
    # move persistent bottom icons slightly down for visual spacing
    btn_y = HEIGHT - int(40 * scale) + int(10 * scale)
    restart_rect = pygame.Rect(center_x - 56, btn_y - icon_size//2, icon_size, icon_size)
    home_rect = pygame.Rect(center_x + 20, btn_y - icon_size//2, icon_size, icon_size)
    # draw icons if available, otherwise fallback to simple shapes + glyphs
    if IMAGES.get('restart'):
        img = IMAGES['restart']
        if img.get_size() != (restart_rect.w, restart_rect.h):
            img = pygame.transform.smoothscale(img, (restart_rect.w, restart_rect.h))
        screen.blit(img, restart_rect.topleft)
    else:
        pygame.draw.ellipse(screen, (120, 120, 180), restart_rect)
        icon_font = pygame.font.SysFont("helvetica", max(18, int(18 * scale)))
        r_txt = icon_font.render("↺", True, WHITE)
        screen.blit(r_txt, r_txt.get_rect(center=restart_rect.center))
    if IMAGES.get('home'):
        img2 = IMAGES['home']
        if img2.get_size() != (home_rect.w, home_rect.h):
            img2 = pygame.transform.smoothscale(img2, (home_rect.w, home_rect.h))
        screen.blit(img2, home_rect.topleft)
    else:
        pygame.draw.ellipse(screen, (120, 180, 120), home_rect)
        icon_font = pygame.font.SysFont("helvetica", max(18, int(18 * scale)))
        h_txt = icon_font.render("⌂", True, WHITE)
        screen.blit(h_txt, h_txt.get_rect(center=home_rect.center))
    button_rects['restart'] = restart_rect
    button_rects['home'] = home_rect
    pygame.display.flip()
    return button_rects


def get_player_names(screen):
    pygame.key.set_repeat(300, 50)
    font = pygame.font.SysFont("helvetica", 28)
    small = pygame.font.SysFont("helvetica", 20)
    # italic variant for placeholder/example text
    small_italic = pygame.font.SysFont("helvetica", 20, italic=True)
    placeholder_color = (180, 180, 180)
    name_x = "Spieler X"
    name_o = "Spieler O"
    active = 'X'
    start_btn = pygame.Rect(WINDOW_WIDTH//2 - 80, HEIGHT//2 + 80, 160, 36)
    while True:
        screen.fill(BG)
        title = font.render("Namen eingeben", True, WHITE)
        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH//2, HEIGHT//2 - 120)))
        # input boxes
        box_w = 300
        box_h = 36
        box_x = WINDOW_WIDTH//2 - box_w//2
        x_box = pygame.Rect(box_x, HEIGHT//2 - 40, box_w, box_h)
        o_box = pygame.Rect(box_x, HEIGHT//2 + 10, box_w, box_h)
        pygame.draw.rect(screen, (40,40,40), x_box)
        pygame.draw.rect(screen, (40,40,40), o_box)
        # active border
        if active == 'X':
            pygame.draw.rect(screen, (180,180,100), x_box, 2)
        else:
            pygame.draw.rect(screen, (180,180,100), o_box, 2)
        # render placeholders in italic and lighter color
        if name_x == "Spieler X":
            txt_x = small_italic.render(name_x, True, placeholder_color)
        else:
            txt_x = small.render(name_x, True, WHITE)
        if name_o == "Spieler O":
            txt_o = small_italic.render(name_o, True, placeholder_color)
        else:
            txt_o = small.render(name_o, True, WHITE)
        screen.blit(txt_x, (x_box.x + 8, x_box.y + 8))
        screen.blit(txt_o, (o_box.x + 8, o_box.y + 8))
        pygame.draw.rect(screen, (100,180,100), start_btn)
        start_txt = small.render("Start", True, WHITE)
        screen.blit(start_txt, start_txt.get_rect(center=start_btn.center))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = 'O' if active == 'X' else 'X'
                elif event.key == pygame.K_RETURN:
                    if name_x.strip() and name_o.strip():
                        return {'X': name_x.strip(), 'O': name_o.strip()}
                elif event.key == pygame.K_BACKSPACE:
                    # if placeholder is present, a single backspace clears it
                    if active == 'X':
                        if name_x == "Spieler X":
                            name_x = ""
                        else:
                            name_x = name_x[:-1]
                    else:
                        if name_o == "Spieler O":
                            name_o = ""
                        else:
                            name_o = name_o[:-1]
                else:
                    ch = event.unicode
                    if ch.isprintable():
                        if active == 'X':
                            name_x += ch
                        else:
                            name_o += ch
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if x_box.collidepoint(mx, my):
                    active = 'X'
                if o_box.collidepoint(mx, my):
                    active = 'O'
                if start_btn.collidepoint(mx, my):
                    if name_x.strip() and name_o.strip():
                        return {'X': name_x.strip(), 'O': name_o.strip()}

def measure_superpositions(board, superpos_pairs):
    for group in superpos_pairs:
        positions = group[:-1]
        player = group[-1]
        n = len(positions)
        if n == 2:
            result = qiskit_measure(1)
            r0, c0 = positions[0]
            r1, c1 = positions[1]
            if result[0] == '0':
                board[r0][c0] = player
                board[r1][c1] = " "
            else:
                board[r0][c0] = " "
                board[r1][c1] = player
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
    global N_SUPERPOS, WINDOW_WIDTH, HEIGHT, CELL_SIZE, RADIUS, WIDTH, BTN_WIDTH, BTN_HEIGHT
    N_SUPERPOS = n_superpos
    pygame.init()
   
    screen = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Quixit Pygame")

   
    info = pygame.display.Info()
    scale = min(WINDOW_WIDTH / ORIGINAL_WIDTH, HEIGHT / ORIGINAL_HEIGHT)
    CELL_SIZE = max(8, int(ORIGINAL_CELL * scale * BOARD_VISUAL_SCALE))
    RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))
    WIDTH = COLS * CELL_SIZE
    BTN_WIDTH = max(24, int(ORIGINAL_BTN_WIDTH * scale * BTN_VISUAL_SCALE))
    BTN_HEIGHT = max(12, int(ORIGINAL_BTN_HEIGHT * scale * BTN_VISUAL_SCALE))
    # load / scale images for icons (if present in assets/)
    global IMAGES
    icon_size = max(28, int(28 * scale))
    IMAGES = load_images((icon_size, icon_size))
    board = create_board()
    current_player = "X"
    game_over = False

    superpos_count = 0
    last_superpos_cols = []
    superpos_groups = []
    superpos_temp = []
    measure_uses = {"X": 0, "O": 0}
    MAX_MEASURE = 3

    # ask for player names before starting the main loop
    player_names = get_player_names(screen)
    while True:
        winner_text = None
        screen.fill(BG)
        button_rects = draw_board(screen, board, measure_uses, winner_text, current_player, player_names)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # handle window resize: recompute sizes but keep proportions
            elif event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH = event.w
                HEIGHT = event.h
                scale = max(0.1, min(WINDOW_WIDTH / ORIGINAL_WIDTH, HEIGHT / ORIGINAL_HEIGHT))
                CELL_SIZE = max(8, int(ORIGINAL_CELL * scale * BOARD_VISUAL_SCALE))
                RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))
                WIDTH = COLS * CELL_SIZE
                BTN_WIDTH = max(24, int(ORIGINAL_BTN_WIDTH * scale * BTN_VISUAL_SCALE))
                BTN_HEIGHT = max(12, int(ORIGINAL_BTN_HEIGHT * scale * BTN_VISUAL_SCALE))
                # rescale icons on resize
                icon_size = max(28, int(28 * scale))
                IMAGES = load_images((icon_size, icon_size))
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                # check persistent bottom buttons first
                if button_rects.get('restart') and button_rects['restart'].collidepoint(x, y):
                    board = create_board()
                    measure_uses = {"X": 0, "O": 0}
                    current_player = "X"
                    game_over = False
                    turn_count = 0
                    superpos_count = 0
                    last_superpos_cols = []
                    superpos_groups = []
                    superpos_temp = []
                    winner_text = None
                    continue
                if button_rects.get('home') and button_rects['home'].collidepoint(x, y):
                    # go back to name entry
                    player_names = get_player_names(screen)
                    board = create_board()
                    measure_uses = {"X": 0, "O": 0}
                    current_player = "X"
                    game_over = False
                    turn_count = 0
                    superpos_count = 0
                    last_superpos_cols = []
                    superpos_groups = []
                    superpos_temp = []
                    winner_text = None
                    continue
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
                        winner_text = "Rot gewinnt!" if current_player == "X" else "Gelb gewinnt!"
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
                    draw_board(screen, board, measure_uses, winner_text, current_player, player_names)
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
                            if turn_count % (N_SUPERPOS*3) == 0 and superpos_groups and measure_uses["X"] >= MAX_MEASURE and measure_uses["O"] >= MAX_MEASURE:
                                if superpos_temp:
                                    superpos_groups.append(tuple(superpos_temp + [current_player]))
                                    superpos_temp = []
                                    superpos_count = 0
                                    last_superpos_cols = []
                                measure_superpositions(board, superpos_groups)
                                apply_gravity(board)
            if event.type == pygame.KEYDOWN and not game_over:
                # fullscreen toggle (F11) and quit (ESC)
                if event.key == pygame.K_F11:
                    if screen.get_flags() & pygame.FULLSCREEN:
                        pygame.display.set_mode((WINDOW_WIDTH, HEIGHT), pygame.RESIZABLE)
                    else:
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        info = pygame.display.Info()
                        WINDOW_WIDTH = info.current_w
                        HEIGHT = info.current_h
                        scale = max(0.1, min(WINDOW_WIDTH / ORIGINAL_WIDTH, HEIGHT / ORIGINAL_HEIGHT))
                        CELL_SIZE = max(8, int(ORIGINAL_CELL * scale * BOARD_VISUAL_SCALE))
                        RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))
                        WIDTH = COLS * CELL_SIZE
                        BTN_WIDTH = max(24, int(ORIGINAL_BTN_WIDTH * scale * BTN_VISUAL_SCALE))
                        BTN_HEIGHT = max(12, int(ORIGINAL_BTN_HEIGHT * scale * BTN_VISUAL_SCALE))
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
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
                            if turn_count % (N_SUPERPOS*3) == 0 and superpos_groups and measure_uses["X"] >= MAX_MEASURE and measure_uses["O"] >= MAX_MEASURE:
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
                    # measuring with Enter consumes a turn
                    turn_count += 1
                    x_win = check_win(board, "X")
                    o_win = check_win(board, "O")
                    if x_win and o_win:
                        winner_text = "Rot gewinnt!" if current_player == "X" else "Gelb gewinnt!"
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
                    # switch current player as a measured turn was used
                    current_player = "O" if current_player == "X" else "X"
                    draw_board(screen, board, measure_uses, winner_text, current_player, player_names)
                    continue
        if not game_over:
            if check_win(board, "X"):
                winner_text = "Rot gewinnt!"
                game_over = True
            elif check_win(board, "O"):
                winner_text = "Gelb gewinnt!"
                game_over = True
            elif all(board[0][c] != " " for c in range(COLS)):
                winner_text = "Unentschieden!"
                game_over = True

        button_rects = draw_board(screen, board, measure_uses, winner_text, current_player, player_names)
        if game_over:
            # Display an overlay with Restart and Exit; recalc sizes on resize
            scale = CELL_SIZE / ORIGINAL_CELL
            font_btn = pygame.font.SysFont(None, max(16, int(ORIGINAL_FONT_SIZE * scale)))
            restart_btn = pygame.Rect(WINDOW_WIDTH//2 - int(120*scale), HEIGHT//2 + int(40*scale), int(240*scale), int(36*scale))
            exit_btn = pygame.Rect(WINDOW_WIDTH//2 - int(120*scale), HEIGHT//2 + int(90*scale), int(240*scale), int(36*scale))
            while game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        import subprocess, os
                        menu_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pygame-q-c4/quixit_main.py'))
                        subprocess.Popen([sys.executable, menu_path])
                        sys.exit()
                    if event.type == pygame.VIDEORESIZE:
                        WINDOW_WIDTH = event.w
                        HEIGHT = event.h
                        scale = max(0.1, min(WINDOW_WIDTH / ORIGINAL_WIDTH, HEIGHT / ORIGINAL_HEIGHT))
                        CELL_SIZE = max(8, int(ORIGINAL_CELL * scale * BOARD_VISUAL_SCALE))
                        RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))
                        WIDTH = COLS * CELL_SIZE
                        BTN_WIDTH = max(24, int(ORIGINAL_BTN_WIDTH * scale * BTN_VISUAL_SCALE))
                        BTN_HEIGHT = max(12, int(ORIGINAL_BTN_HEIGHT * scale * BTN_VISUAL_SCALE))
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        # check bottom persistent buttons returned by draw_board
                        if button_rects.get('restart') and button_rects['restart'].collidepoint(mx, my):
                            board = create_board()
                            measure_uses = {"X": 0, "O": 0}
                            current_player = "X"
                            game_over = False
                            turn_count = 0
                            superpos_count = 0
                            last_superpos_cols = []
                            superpos_groups = []
                            superpos_temp = []
                            winner_text = None
                            break
                        if button_rects.get('home') and button_rects['home'].collidepoint(mx, my):
                            player_names = get_player_names(screen)
                            board = create_board()
                            measure_uses = {"X": 0, "O": 0}
                            current_player = "X"
                            game_over = False
                            turn_count = 0
                            superpos_count = 0
                            last_superpos_cols = []
                            superpos_groups = []
                            superpos_temp = []
                            winner_text = None
                            break
                # draw board underneath; no centered dark panel to avoid black box
                button_rects = draw_board(screen, board, measure_uses, winner_text, current_player, player_names)
                pygame.display.flip()
                pygame.time.wait(100)

if __name__ == "__main__":
    import sys
    n_superpos = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    main(n_superpos)