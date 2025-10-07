import pygame
import sys
import subprocess
import os

WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 120, 120)
YELLOW = (220, 220, 120)
BG = (21, 24, 26)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quanten Vier Gewinnt - Modus wählen")
    font = pygame.font.SysFont(None, 48)
    font_btn = pygame.font.SysFont(None, 36)

    superpos_options = [2, 3, 4, 5]
    btns_superpos = []
    while True:
        screen.fill(BG)
        title = font.render("Quanten Vier Gewinnt: Modus wählen", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

        # Superpositions-Buttons
        btns_superpos.clear()
        for i, n in enumerate(superpos_options):
            btn = pygame.Rect(WIDTH//2 - 150 + i*80, 240, 70, 40)
            pygame.draw.rect(screen, (180, 180, 255), btn)
            txt = font_btn.render(f"{n} Qubits", True, BLACK)
            screen.blit(txt, (btn.x + 5, btn.y + 5))
            btns_superpos.append((btn, n))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                # Superpositions-Auswahl
                for btn, n_qubits in btns_superpos:
                    if btn.collidepoint(x, y):
                        pygame.quit()
                        import subprocess
                        subprocess.run([sys.executable, os.path.abspath(os.path.join(os.path.dirname(__file__), '../quixit_pygame.py')), str(n_qubits)])
                        sys.exit()

if __name__ == "__main__":
    main()
