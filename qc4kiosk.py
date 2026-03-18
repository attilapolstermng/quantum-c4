import pygame
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "assets"

def load_images(target_size):
    imgs = {}
    def load(name):
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

IMAGES = {}

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_ibm_runtime import QiskitRuntimeService

backend = Aer.get_backend("aer_simulator")

ROWS, COLS = 6, 7
ORIGINAL_CELL = 80
ORIGINAL_WIDTH = COLS * ORIGINAL_CELL
ORIGINAL_HEIGHT = (ROWS + 1) * ORIGINAL_CELL
ORIGINAL_GRADIENT_HEIGHT = 180
ORIGINAL_BTN_WIDTH = 120
ORIGINAL_BTN_HEIGHT = 32
ORIGINAL_FONT_SIZE = 22

CELL_SIZE = ORIGINAL_CELL
WIDTH = ORIGINAL_WIDTH
HEIGHT = 720
BTN_WIDTH = ORIGINAL_BTN_WIDTH
BTN_HEIGHT = ORIGINAL_BTN_HEIGHT
WINDOW_WIDTH = 1280
BOARD_VISUAL_SCALE = 0.95
BTN_VISUAL_SCALE = 0.9
HOLE_SCALE = 0.85
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

def draw_board(surface, board, measure_uses, game_width, game_height, winner_text=None, current_player=None, player_names=None):
    surface.fill(BG)
    
    gradient_height = max(8, int(ORIGINAL_GRADIENT_HEIGHT * CELL_SIZE / ORIGINAL_CELL))
    gradient_surface = pygame.Surface((game_width, gradient_height), pygame.SRCALPHA)
    grad_color = (220, 220, 0) if current_player == "O" else (220, 0, 0)
    for y in range(gradient_height):
        alpha = int(120 * (1 - y / gradient_height))
        pygame.draw.rect(gradient_surface, grad_color + (alpha,), (0, gradient_height - y - 1, game_width, 1))
    surface.blit(gradient_surface, (0, game_height - gradient_height))
    
    board_offset_x = (game_width - WIDTH) // 2
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
            pygame.draw.circle(surface, color, (x, y), RADIUS)
            pygame.draw.circle(surface, BLACK, (x, y), RADIUS, 2)
    
    button_rects = {}
    scale = CELL_SIZE / ORIGINAL_CELL
    font_btn = pygame.font.SysFont("helvetica", max(12, int(ORIGINAL_FONT_SIZE * scale)))
    
    btn_x_x = board_offset_x - BTN_WIDTH - int(30 * scale)
    btn_x_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_x = pygame.Rect(btn_x_x, btn_x_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(surface, (220, 120, 120), btn_x)
    name_x = player_names['X'] if player_names and 'X' in player_names else 'X'
    text_x = font_btn.render(f"{name_x}: ({3-measure_uses['X']} übrig)", True, (255, 255, 255))
    text_x_rect = text_x.get_rect(center=(btn_x.x + BTN_WIDTH//2, btn_x.y + BTN_HEIGHT + int(16 * scale)))
    surface.blit(text_x, text_x_rect)
    button_rects["X"] = btn_x
    
    btn_o_x = board_offset_x + WIDTH + int(30 * scale)
    btn_o_y = CELL_SIZE + CELL_SIZE // 2 - BTN_HEIGHT // 2
    btn_o = pygame.Rect(btn_o_x, btn_o_y, BTN_WIDTH, BTN_HEIGHT)
    pygame.draw.rect(surface, (220, 220, 120), btn_o)
    name_o = player_names['O'] if player_names and 'O' in player_names else 'O'
    text_o = font_btn.render(f"{name_o}: ({3-measure_uses['O']} übrig)", True, (255, 255, 255))
    text_o_rect = text_o.get_rect(center=(btn_o.x + BTN_WIDTH//2, btn_o.y + BTN_HEIGHT + int(16 * scale)))
    surface.blit(text_o, text_o_rect)
    button_rects["O"] = btn_o
    
    if winner_text:
        font = pygame.font.SysFont("helvetica", max(30, int(60 * scale)), bold=True)
        text = font.render(winner_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(game_width//2, int(60 * scale)))
        surface.blit(text, text_rect)
    
    icon_size = max(28, int(28 * scale))
    center_x = game_width // 2
    btn_y = game_height - int(40 * scale) + int(10 * scale)
    restart_rect = pygame.Rect(center_x - 56, btn_y - icon_size//2, icon_size, icon_size)
    home_rect = pygame.Rect(center_x + 20, btn_y - icon_size//2, icon_size, icon_size)
    
    if IMAGES.get('restart'):
        img = IMAGES['restart']
        if img.get_size() != (restart_rect.w, restart_rect.h):
            img = pygame.transform.smoothscale(img, (restart_rect.w, restart_rect.h))
        surface.blit(img, restart_rect.topleft)
    else:
        pygame.draw.ellipse(surface, (120, 120, 180), restart_rect)
        icon_font = pygame.font.SysFont("helvetica", max(18, int(18 * scale)))
        r_txt = icon_font.render("↺", True, WHITE)
        surface.blit(r_txt, r_txt.get_rect(center=restart_rect.center))
    
    if IMAGES.get('home'):
        img2 = IMAGES['home']
        if img2.get_size() != (home_rect.w, home_rect.h):
            img2 = pygame.transform.smoothscale(img2, (home_rect.w, home_rect.h))
        surface.blit(img2, home_rect.topleft)
    else:
        pygame.draw.ellipse(surface, (120, 180, 120), home_rect)
        icon_font = pygame.font.SysFont("helvetica", max(18, int(18 * scale)))
        h_txt = icon_font.render("⌂", True, WHITE)
        surface.blit(h_txt, h_txt.get_rect(center=home_rect.center))
    
    button_rects['restart'] = restart_rect
    button_rects['home'] = home_rect
    return button_rects


def get_player_names(screen, screen_width, screen_height):
    pygame.key.set_repeat(300, 50)
    font = pygame.font.SysFont("helvetica", 28)
    small = pygame.font.SysFont("helvetica", 20)
    small_italic = pygame.font.SysFont("helvetica", 20, italic=True)
    placeholder_color = (180, 180, 180)
    name_x = ""
    name_o = ""
    active = 'X'
    start_btn = pygame.Rect(screen_width//2 - 80, screen_height//2 + 80, 160, 36)
    
    while True:
        screen.fill(BG)
        title = font.render("Namen eingeben", True, WHITE)
        screen.blit(title, title.get_rect(center=(screen_width//2, screen_height//2 - 120)))
        
        box_w = 300
        box_h = 36
        box_x = screen_width//2 - box_w//2
        x_box = pygame.Rect(box_x, screen_height//2 - 40, box_w, box_h)
        o_box = pygame.Rect(box_x, screen_height//2 + 10, box_w, box_h)
        pygame.draw.rect(screen, (40,40,40), x_box)
        pygame.draw.rect(screen, (40,40,40), o_box)
        
        if active == 'X':
            pygame.draw.rect(screen, (180,180,100), x_box, 2)
        else:
            pygame.draw.rect(screen, (180,180,100), o_box, 2)
        
       # render placeholders in italic and lighter color
        if name_x == "":
            txt_x = small_italic.render("Spieler X", True, placeholder_color)
        else:
            txt_x = small.render(name_x, True, WHITE)
        if name_o == "":
            txt_o = small_italic.render("Spieler O", True, placeholder_color)
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
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_TAB:
                    active = 'O' if active == 'X' else 'X'
                elif event.key == pygame.K_RETURN:
                    if name_x.strip() and name_o.strip():
                        return {'X': name_x.strip(), 'O': name_o.strip()}
                elif event.key == pygame.K_BACKSPACE:
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
    global N_SUPERPOS, CELL_SIZE, RADIUS, WIDTH, BTN_WIDTH, BTN_HEIGHT
    N_SUPERPOS = n_superpos
    
    pygame.init()
    
    # Hole Bildschirmauflösung
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    
    # Erstelle Fullscreen
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Quixit Pygame")
    
    # Berechne Skalierung - 80% der Bildschirmgröße für Puffer
    scale = min(screen_width / (ORIGINAL_WIDTH * 1.5), screen_height / ORIGINAL_HEIGHT) * 0.75
    CELL_SIZE = max(8, int(ORIGINAL_CELL * scale * BOARD_VISUAL_SCALE))
    RADIUS = max(4, int((CELL_SIZE // 2 - 5) * HOLE_SCALE))
    WIDTH = COLS * CELL_SIZE
    BTN_WIDTH = max(24, int(ORIGINAL_BTN_WIDTH * scale * BTN_VISUAL_SCALE))
    BTN_HEIGHT = max(12, int(ORIGINAL_BTN_HEIGHT * scale * BTN_VISUAL_SCALE))
    
    # Berechne game_surface Größe - groß genug für Board + Buttons + Text
    button_spacing = int(30 * scale)
    extra_text_space = int(50 * scale)
    game_width = WIDTH + 2 * (BTN_WIDTH + button_spacing + extra_text_space)
    game_height = (ROWS + 1) * CELL_SIZE + int(120 * scale)
    
    # Berechne Offset für Zentrierung
    offset_x = (screen_width - game_width) // 2
    offset_y = (screen_height - game_height) // 2
    
    # Erstelle game_surface
    game_surface = pygame.Surface((game_width, game_height))
    
    # load icons
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

    player_names = get_player_names(screen, screen_width, screen_height)
    
    while True:
        winner_text = None
        button_rects = draw_board(game_surface, board, measure_uses, game_width, game_height, winner_text, current_player, player_names)
        
        # Schwarzer Hintergrund und zentrierte game_surface
        screen.fill((0, 0, 0))
        screen.blit(game_surface, (offset_x, offset_y))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                # Mauskoordinaten auf game_surface umrechnen
                x = x - offset_x
                y = y - offset_y
                
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
                    player_names = get_player_names(screen, screen_width, screen_height)
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
                    continue
                
                board_offset_x = (game_width - WIDTH) // 2
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
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
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
                        continue
                    if superpos_temp:
                        superpos_groups.append(tuple(superpos_temp + [current_player]))
                        superpos_temp = []
                        superpos_count = 0
                        last_superpos_cols = []
                    measure_superpositions(board, superpos_groups)
                    apply_gravity(board)
                    measure_uses[current_player] += 1
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
                    current_player = "O" if current_player == "X" else "X"
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

        if game_over:
            while game_over:
                button_rects = draw_board(game_surface, board, measure_uses, game_width, game_height, winner_text, current_player, player_names)
                screen.fill((0, 0, 0))
                screen.blit(game_surface, (offset_x, offset_y))
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                            pygame.quit()
                            sys.exit()
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = event.pos
                        mx = mx - offset_x
                        my = my - offset_y
                        
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
                            player_names = get_player_names(screen, screen_width, screen_height)
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
                
                pygame.time.wait(100)

if __name__ == "__main__":
    import sys
    n_superpos = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    main(n_superpos)