import pygame
import random
from .hole import Hole
from .sounds import Sounds

# Game Engine

DARK_BROWN = (60, 40, 20)
MOLE_BROWN = (140, 95, 55)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (170, 170, 170)
LIGHT = (225, 235, 215)
GOLD = (255, 215, 90)
BUTTON_COLOR = (80, 120, 62)
BUTTON_HOVER = (135, 195, 100)
QUIT_COLOR = (140, 55, 45)
QUIT_HOVER = (215, 90, 70)

HOLE_RADIUS = 40
MOLE_RADIUS = 32
MARGIN = 10                 # minimum gap between any text and the window edge
INPUT_DELAY_FRAMES = 30     # 0.5 s before a menu/end screen accepts input

# Screens
MENU = "menu"               # choose a difficulty
PLAYING = "playing"         # the 30-second round
GAME_OVER = "game_over"     # results, Replay / Quit

# name -> (spawn_chance, mole_up_frames)
DIFFICULTIES = {
    "Easy": (0.01, 70),
    "Medium": (0.02, 45),
    "Hard": (0.035, 28),
}
DIFFICULTY_NOTES = {
    "Easy": "Slow moles",
    "Medium": "Normal pace",
    "Hard": "Fast moles",
}


class GameEngine:
    def __init__(self, width, height, rows=3, cols=3):
        self.width = width
        self.height = height

        self.holes = []
        spacing_x = width // (cols + 1)
        spacing_y = (height - 80) // (rows + 1)
        for r in range(rows):
            for c in range(cols):
                cx = spacing_x * (c + 1)
                cy = 80 + spacing_y * (r + 1)
                self.holes.append(Hole(cx, cy, HOLE_RADIUS))

        self.round_seconds = 30

        self.font = pygame.font.SysFont("Arial", 28)
        self.big_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 54, bold=True)
        self.score_font = pygame.font.SysFont("Arial", 46, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.note_font = pygame.font.SysFont("Arial", 16)
        self.button_font = pygame.font.SysFont("Arial", 22, bold=True)

        self.sounds = Sounds()
        self.quit_requested = False
        self._hand_cursor = False

        cx = width // 2

        # Start menu: three difficulty buttons stacked vertically.
        btn_w, btn_h, gap = 240, 60, 12
        top = 235
        self.menu_buttons = []
        for i, label in enumerate(["Easy", "Medium", "Hard"]):
            rect = pygame.Rect(cx - btn_w // 2, top + i * (btn_h + gap), btn_w, btn_h)
            self.menu_buttons.append((label, rect))

        # Game Over: Replay and Quit side by side.
        btn_w, btn_h, gap = 160, 52, 20
        start_x = cx - (2 * btn_w + gap) // 2
        btn_y = height // 2 + 75
        self.end_buttons = [
            ("Replay", pygame.Rect(start_x, btn_y, btn_w, btn_h)),
            ("Quit", pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)),
        ]

        self.difficulty = "Medium"
        self.spawn_chance, self.mole_up_frames = DIFFICULTIES[self.difficulty]
        self._clear_round()
        self._set_state(MENU)

    # ------------------------------------------------------------ state

    @property
    def game_over(self):
        return self.state == GAME_OVER

    def _set_state(self, state):
        self.state = state
        self.state_frames = 0

    def _clear_round(self):
        self.time_left_frames = self.round_seconds * 60
        self.score = 0
        self.misses = 0
        for hole in self.holes:
            hole.reset()

    def reset(self, difficulty):
        """Start a new round at the given difficulty."""
        self.difficulty = difficulty
        self.spawn_chance, self.mole_up_frames = DIFFICULTIES[difficulty]
        self._clear_round()
        self._set_state(PLAYING)

    def replay(self):
        """Go back to the start menu to pick a difficulty again."""
        self._clear_round()
        self._set_state(MENU)

    # ------------------------------------------------------------ input

    def handle_event(self, event):
        # Only MOUSEBUTTONDOWN with the left button counts as a click.
        # Holding the button produces no further events, so a held click
        # counts once; MOUSEBUTTONUP, MOUSEMOTION, right/middle clicks and
        # the scroll wheel (buttons 4/5) are all ignored.
        if self.state == PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
        else:
            self._handle_screen_event(event)

    def _screen_ready(self):
        # A short delay stops a click from the previous screen (a last-
        # second whack, or a double-click on Replay) from landing on a
        # button of the newly shown screen.
        return self.state_frames >= INPUT_DELAY_FRAMES

    def _current_buttons(self):
        if self.state == MENU:
            return self.menu_buttons
        if self.state == GAME_OVER:
            return self.end_buttons
        return []

    def _hovered_button(self, pos):
        if not self._screen_ready():
            return None
        for label, rect in self._current_buttons():
            if rect.collidepoint(pos):
                return label
        return None

    def _handle_screen_event(self, event):
        if not self._screen_ready():
            return
        choice = None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            choice = self._hovered_button(event.pos)
        elif event.type == pygame.KEYDOWN:
            if self.state == MENU:
                keys = {
                    pygame.K_1: "Easy", pygame.K_KP1: "Easy",
                    pygame.K_2: "Medium", pygame.K_KP2: "Medium",
                    pygame.K_3: "Hard", pygame.K_KP3: "Hard",
                    pygame.K_q: "Quit", pygame.K_ESCAPE: "Quit",
                }
            else:
                keys = {
                    pygame.K_r: "Replay", pygame.K_RETURN: "Replay",
                    pygame.K_KP_ENTER: "Replay",
                    pygame.K_q: "Quit", pygame.K_ESCAPE: "Quit",
                }
            choice = keys.get(event.key)

        if choice == "Quit":
            self.quit_requested = True
        elif choice == "Replay":
            self.replay()
        elif choice in DIFFICULTIES:
            self.reset(choice)

    def _handle_click(self, pos):
        # Only holes whose drawn circle contains the click are candidates;
        # of those, the single closest one gets the click.
        candidates = [hole for hole in self.holes if hole.contains(pos)]
        target = min(candidates, key=lambda h: h.distance_to(pos), default=None)

        if target is not None and target.whack():
            self.score += 1
            self.sounds.play("whack")
        else:
            self.misses += 1
            self.sounds.play("miss")

    def handle_input(self):
        # Reserved for continuously-held-key input; this game is
        # entirely mouse-driven, so there's nothing to poll here.
        pass

    # ----------------------------------------------------------- update

    def update(self):
        if self.state != PLAYING:
            self.state_frames += 1
            return

        self.time_left_frames -= 1
        if self.time_left_frames <= 0:
            self.time_left_frames = 0
            for hole in self.holes:
                hole.reset()
            self._set_state(GAME_OVER)
            self.sounds.play("round_over")   # runs once per round
            return

        for hole in self.holes:
            hole.update()
            if not hole.active and random.random() < self.spawn_chance:
                hole.pop_up(self.mole_up_frames)
                self.sounds.play("pop")

    # ----------------------------------------------------------- render

    def _fit(self, surface, max_width):
        """Shrink a rendered text surface if it is wider than max_width, so
        text stays inside the window even with a wider fallback font."""
        if surface.get_width() <= max_width:
            return surface
        scale = max_width / surface.get_width()
        size = (max_width, max(1, int(surface.get_height() * scale)))
        return pygame.transform.smoothscale(surface, size)

    def _set_hand_cursor(self, on):
        if on == self._hand_cursor:
            return
        self._hand_cursor = on
        try:
            pygame.mouse.set_cursor(
                pygame.SYSTEM_CURSOR_HAND if on else pygame.SYSTEM_CURSOR_ARROW
            )
        except pygame.error:
            pass   # some platforms have no system cursors; hover colour still shows

    def render(self, screen):
        for hole in self.holes:
            pygame.draw.circle(screen, DARK_BROWN, (hole.center_x, hole.center_y), HOLE_RADIUS)
            if hole.active:
                pygame.draw.circle(screen, MOLE_BROWN, (hole.center_x, hole.center_y), MOLE_RADIUS)

        if self.state != MENU:
            timer_text = self.font.render(f"Time: {max(0, self.time_left_frames // 60)}s", True, BLACK)
            timer_rect = timer_text.get_rect(topright=(self.width - MARGIN, MARGIN))
            score_text = self.font.render(f"Score: {self.score} | {self.difficulty}", True, BLACK)
            score_text = self._fit(score_text, timer_rect.left - 2 * MARGIN)
            screen.blit(score_text, (MARGIN, MARGIN))
            screen.blit(timer_text, timer_rect)

        if self.state == PLAYING:
            self._set_hand_cursor(False)
        else:
            self._render_screen(screen)

    def screen_layout(self, mouse_pos):
        """For the menu or Game Over screen, return
        texts:   [(surface, rect)]
        buttons: [(label, rect, hovered)] as they will be drawn."""
        cx = self.width // 2
        cy = self.height // 2
        max_w = self.width - 2 * MARGIN

        texts = []

        def add(surface, center):
            surface = self._fit(surface, max_w)
            texts.append((surface, surface.get_rect(center=center)))

        if self.state == MENU:
            add(self.title_font.render("WHACK-A-MOLE", True, GOLD), (cx, 120))
            add(self.font.render("Choose your difficulty", True, WHITE), (cx, 190))
            add(self.small_font.render("Keys: 1 Easy   2 Medium   3 Hard   Esc Quit", True, WHITE),
                (cx, self.menu_buttons[-1][1].bottom + 35))
        else:
            add(self.big_font.render("GAME OVER", True, WHITE), (cx, cy - 130))
            add(self.score_font.render(f"Final score: {self.score}", True, GOLD), (cx, cy - 50))
            add(self.font.render(f"Misses: {self.misses}  |  {self.difficulty}", True, WHITE), (cx, cy + 2))
            add(self.small_font.render("Keys: R / Enter Replay   Q / Esc Quit", True, WHITE),
                (cx, self.end_buttons[0][1].bottom + 35))

        hovered_label = self._hovered_button(mouse_pos)
        buttons = []
        for label, rect in self._current_buttons():
            hovered = label == hovered_label
            # Hovered buttons grow slightly; every layout has room for this.
            buttons.append((label, rect.inflate(8, 6) if hovered else rect, hovered))
        return texts, buttons

    def _render_screen(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        texts, buttons = self.screen_layout(pygame.mouse.get_pos())
        for surface, rect in texts:
            screen.blit(surface, rect)

        ready = self._screen_ready()
        any_hovered = False
        for label, rect, hovered in buttons:
            any_hovered = any_hovered or hovered
            self._draw_button(screen, label, rect, hovered, ready)

        self._set_hand_cursor(any_hovered)

    def _draw_button(self, screen, label, rect, hovered, ready):
        if label == "Quit":
            color = QUIT_HOVER if hovered else QUIT_COLOR
        else:
            color = BUTTON_HOVER if hovered else BUTTON_COLOR
        if hovered:
            # Drop shadow under the raised button.
            pygame.draw.rect(screen, BLACK, rect.move(0, 4), border_radius=10)
        pygame.draw.rect(screen, color, rect, border_radius=10)
        border = GOLD if hovered else WHITE
        pygame.draw.rect(screen, border, rect, width=3 if hovered else 2, border_radius=10)

        text_color = WHITE if ready else GREY
        text = self._fit(self.button_font.render(label, True, text_color), rect.width - 8)
        note = DIFFICULTY_NOTES.get(label)
        if note:
            # Difficulty buttons carry a one-line description under the name.
            sub = self._fit(self.note_font.render(note, True, LIGHT if ready else GREY), rect.width - 8)
            screen.blit(text, text.get_rect(center=(rect.centerx, rect.centery - 10)))
            screen.blit(sub, sub.get_rect(center=(rect.centerx, rect.centery + 13)))
        else:
            screen.blit(text, text.get_rect(center=rect.center))