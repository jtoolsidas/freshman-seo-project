import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blue Sky and Green Grass Background")

# Colors
BLUE_SKY = (135, 206, 235)
GREEN_GRASS = (34, 139, 34)

SKIN        = (255, 200, 150)
BROWN       = (139, 90, 43)
ORANGE      = (255, 140, 0)
DARK_BLUE   = (30, 60, 120)
GOLD        = (255, 215, 0)
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
LIGHT_BLUE  = (173, 216, 230)
CORRECT_GREEN = (50, 200, 80)
WRONG_RED     = (220, 50, 50)

correct_sound = pygame.mixer.Sound("correct.mp3")
wrong_sound = pygame.mixer.Sound("wrong.mp3")

# Optional volume (0.0 to 1.0)
correct_sound.set_volume(0.5)
wrong_sound.set_volume(0.5)

# Grass setup (moved down)
GRASS_HEIGHT = 150
grass_y_position = SCREEN_HEIGHT - 100

# Movement constants
GRAVITY = 0.5
JUMP_STRENGTH = -13
PLAYER_SPEED = 4

# Character state
player_x = 100
ground_level = grass_y_position - 20
player_y = float(ground_level)
player_vel_y = 0
on_ground = True
facing = 1  # 1 = right, -1 = left
walk_frame = 0.0

score = 0
lives = 3
timer_seconds = 120  # 2 minutes
timer_ms      = 0    # tracks milliseconds within each second

# Cloud settings
clouds = [
    {"x": 100, "y": 70,  "speed": 0.4, "size": 1.0},
    {"x": 350, "y": 150, "speed": 0.6, "size": 1.3},
    {"x": 600, "y": 270, "speed": 0.3, "size": 0.9},
    {"x": 200, "y": 350, "speed": 0.5, "size": 1.1},
]

# Math equations
QUESTIONS = [
    ("x + 2 = 5", 3, [1, 4, 6]),
    ("x - 4 = 3", 7, [5, 8, 9]),
    ("2x = 8", 4, [2, 6, 8]),
    ("x + 6 = 10", 4, [2, 5, 7]),
    ("x - 1 = 6", 7, [4, 5, 8]),
    ("3x = 15", 5, [3, 6, 9]),
    ("x + 9 = 12", 3, [1, 5, 7]),
    ("x - 2 = 4", 6, [3, 5, 7]),
    ("5x = 20", 4, [2, 5, 6]),
    ("x + 8 = 15", 7, [4, 6, 8]),
    ("x - 5 = 2", 7, [4, 6, 9]),
    ("2x = 12", 6, [3, 4, 8]),
    ("x + 1 = 9", 8, [5, 6, 7]),
    ("x - 3 = 5", 8, [4, 6, 9]),
    ("4x = 16", 4, [2, 6, 8]),
    ("x + 4 = 11", 7, [5, 6, 9]),
    ("x - 6 = 1", 7, [3, 5, 8]),
    ("x + 3 = 8", 5, [2, 4, 6]),
    ("10x = 50", 5, [2, 4, 10]),
    ("x - 7 = 2", 9, [5, 6, 8]),
]

font_eq  = pygame.font.SysFont("Arial", 20, bold=True)
font_ans = pygame.font.SysFont("Arial", 19, bold=True)
font_ui  = pygame.font.SysFont("Arial", 24, bold=True)


class FallingEquation:
    WIDTH  = 200
    HEIGHT = 46

    def __init__(self):
        self.active    = False
        self.answered  = False
        self.flash     = 0
        self.flash_col = WHITE
        self.choices   = []
        self._respawn()

    def _respawn(self):
        entry = random.choice(QUESTIONS)
        self.text, self.answer, wrongs = entry

        bw, bh = 88, 32
        spacing = 4
        total_choices_width = 4 * bw + 3 * spacing
        safe_margin = 20

        # Keep answers fully on screen
        min_x = total_choices_width // 2 + safe_margin
        max_x = SCREEN_WIDTH - total_choices_width // 2 - safe_margin

        self.x = random.randint(min_x, max_x)
        self.y = -self.HEIGHT
        self.speed = random.uniform(0.6, 0.8)

        self.active = True
        self.answered = False
        self.flash = 0
        self.flash_col = WHITE

        options = wrongs[:3] + [self.answer]
        random.shuffle(options)

        self.choices = []

        for i, val in enumerate(options):
            bx = self.x - total_choices_width // 2 + i * (bw + spacing)
            by = self.y + self.HEIGHT + 4
            self.choices.append(
                AnswerChoice(bx, by, bw, bh, val)
            )

    def update(self):
        if not self.active:
            return
        if self.flash > 0:
            self.flash -= 1
            if self.flash == 0:
                self._respawn()
            return
        if self.answered:
            return

        self.y += self.speed
        for ch in self.choices:
            ch.y = self.y + self.HEIGHT + 4  # buttons follow the box down

        if self.y > grass_y_position - 10:   # missed = hits the ground
            self._miss()

    def _miss(self):
        global lives, timer_seconds, game_over

        wrong_sound.play()
        lives -= 1
        timer_seconds -= 5
        timer_seconds = max(0, timer_seconds)

        if lives <= 0:
            game_over = True
            return

        self.answered = True
        self.flash = 80
        self.flash_col = WRONG_RED

    def check_answer(self, chosen):
        global score, lives, timer_seconds, game_over, game_won

        self.answered = True

        if chosen == self.answer:
            correct_sound.play()
            score += 10
            timer_seconds += 5
            self.flash_col = CORRECT_GREEN

            if score >= 100:
                game_won = True

        else:
            wrong_sound.play()
            lives -= 1
            timer_seconds -= 5
            timer_seconds = max(0, timer_seconds)

            if lives <= 0:
                game_over = True
                return

            self.flash_col = WRONG_RED

        self.flash = 80


    def draw(self, surface):
        if not self.active:
            return
        rect = pygame.Rect(self.x - self.WIDTH // 2,
                           int(self.y), self.WIDTH, self.HEIGHT)
        col = self.flash_col if self.flash > 0 else DARK_BLUE
        pygame.draw.rect(surface, col,   rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
        txt = font_eq.render(self.text, True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))
        if not self.answered:
            for ch in self.choices:
                ch.draw(surface)

    def get_rect(self):
        return pygame.Rect(self.x - self.WIDTH // 2,
                           int(self.y), self.WIDTH, self.HEIGHT)


class AnswerChoice:
    def __init__(self, x, y, w, h, value):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.value     = value

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surface):
        r = self.get_rect()
        col = (50, 50, 120)
        pygame.draw.rect(surface, col,   r, border_radius=6)
        pygame.draw.rect(surface, WHITE, r, 1, border_radius=6)
        lbl = font_ans.render(str(self.value), True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=r.center))


def draw_cloud(surface, x, y, scale=1):
    """Draw a fluffy cloud."""
    puff_size = int(30 * scale)

    pygame.draw.circle(surface, WHITE, (int(x), int(y)), puff_size)
    pygame.draw.circle(surface, WHITE, (int(x + 25 * scale), int(y - 10 * scale)), puff_size)
    pygame.draw.circle(surface, WHITE, (int(x + 50 * scale), int(y)), puff_size)
    pygame.draw.circle(surface, WHITE, (int(x + 25 * scale), int(y + 10 * scale)), puff_size)

    pygame.draw.ellipse(
        surface,
        WHITE,
        (
            int(x - 10 * scale),
            int(y),
            int(70 * scale),
            int(30 * scale)
        )
    )


def draw_character(surface, x, y, facing, walk_frame, on_ground):
    x, y = int(x), int(y)
    f = facing
    wf = walk_frame

    # Leg swing animation
    if on_ground:
        leg1 = math.sin(wf) * 18
        leg2 = -math.sin(wf) * 18
    else:
        leg1, leg2 = 20, -20

    def limb_end(angle, length=18, base_y=0):
        rad = math.radians(angle)
        return (
            x + int(math.sin(rad) * length * f),
            y + base_y + int(math.cos(rad) * 20)
        )

    # Legs
    le1 = limb_end(leg1)
    le2 = limb_end(leg2)

    pygame.draw.line(surface, BROWN, (x, y - 10), le1, 6)
    pygame.draw.line(surface, BROWN, (x, y - 10), le2, 6)

    pygame.draw.ellipse(surface, BROWN, (le1[0] - 7, le1[1] - 4, 14, 8))
    pygame.draw.ellipse(surface, BROWN, (le2[0] - 7, le2[1] - 4,14, 8))

    # Body
    pygame.draw.rect(surface, ORANGE, (x - 14, y - 44, 28, 34), border_radius=6)
    pygame.draw.rect(surface, BROWN, (x - 14, y - 22, 28, 5))

    # Arm swing
    arm1 = limb_end(-leg1 * 0.6, length=16, base_y=-38)
    arm2 = limb_end(-leg2 * 0.6, length=16, base_y=-38)

    pygame.draw.line(surface, SKIN, (x - 8 * f, y - 40), arm1, 5)
    pygame.draw.line(surface, SKIN, (x + 8 * f, y - 40), arm2, 5)

    pygame.draw.circle(surface, SKIN, arm1, 5)
    pygame.draw.circle(surface, SKIN, arm2, 5)

    # Head
    pygame.draw.circle(surface, SKIN, (x, y - 52), 14)

    # Hair
    pygame.draw.arc(surface, BROWN, (x - 14, y - 68, 28, 24), 0, math.pi, 6)

    # Eye
    eye_x = x + 5 * f
    pygame.draw.circle(surface, WHITE, (eye_x, y - 53), 4)
    pygame.draw.circle(surface, BLACK, (eye_x + f, y - 53), 2)

    '''
    # Hat
    pygame.draw.rect(surface, DARK_BLUE, (x - 12, y - 68, 24,  8), border_radius=3)  # brim
    pygame.draw.rect(surface, DARK_BLUE, (x -  8, y - 80, 16, 14), border_radius=4)  # top
    pygame.draw.circle(surface, GOLD, (x - 7, y - 72), 3)                             # pin
    '''


# Equation spawn setup
MAX_EQUATIONS  = 2
SPAWN_INTERVAL = 900
spawn_timer    = 0
equations      = [FallingEquation() for _ in range(MAX_EQUATIONS)]

# Only the first starts active & others wait for the spawn timer
for i in range(1, MAX_EQUATIONS):
    equations[i].active = False
# Fonts for instruction screen
title_font = pygame.font.SysFont("Arial", 42, bold=True)
instruction_font = pygame.font.SysFont("Arial", 26)
small_font = pygame.font.SysFont("Arial", 22)

# Instruction screen
show_instructions = True

while show_instructions:
    screen.fill(BLUE_SKY)

    # Title
    title_text = title_font.render("How to Play", True, DARK_BLUE)
    screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 80)))

    instructions = [
        "You start with a 2 minute timer.",
        "Getting a question RIGHT adds time.",
        "Getting a question WRONG removes time.",
        "Missing a question also removes time.",
        "You have 3 lives.",
        "Wrong answers remove a life.",
        "Answer questions by jumping to",
        "or standing underneath the correct answer choice.",
        "Reach 100 points to win!"
    ]

    y_pos = 130
    for line in instructions:
        text = instruction_font.render(line, True, BLACK)
        screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, y_pos)))
        y_pos += 40

    start_text = small_font.render(
        "Press ENTER to Start", True, (220, 50, 50)
    )
    screen.blit(
        start_text,
        start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    )

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                show_instructions = False

clock = pygame.time.Clock()
running = True
game_over = False
game_won = False

while running:
    # Tick the countdown timer using milliseconds since last frame
    dt = clock.get_time()
    timer_ms += dt
    if timer_ms >= 1000:
        timer_ms      -= 1000
        timer_seconds -= 1
        if timer_seconds <= 0:
            timer_seconds = 0
            game_over = True
            running = False  # game ends when timer hits 0
            

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            



    # Keyboard input
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_x -= PLAYER_SPEED
        facing = -1

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_x += PLAYER_SPEED
        facing = 1

    if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
        player_vel_y = JUMP_STRENGTH
        on_ground = False

    # Keep player inside screen
    player_x = max(30, min(SCREEN_WIDTH - 30, player_x))

    # Gravity
    player_vel_y += GRAVITY
    player_y += player_vel_y

    if player_y >= ground_level:
        player_y = ground_level
        player_vel_y = 0
        on_ground = True

    # Player hitbox
    player_rect = pygame.Rect(int(player_x - 15), int(player_y - 65), 30, 65)

    # Check if player touches an answer button by jumping into it
    for eq in equations:
        if eq.active and not eq.answered and eq.flash == 0:
            for ch in eq.choices:
                if player_rect.colliderect(ch.get_rect()):
                    eq.check_answer(ch.value)
                    break

    # Walking animation
    walk_frame += 0.15

    # Spawn new equations on a timer
    spawn_timer += 1
    if spawn_timer >= SPAWN_INTERVAL:
        spawn_timer = 0

        for eq in equations:
            if not eq.active:

                placed = False
                attempts = 0

                while not placed and attempts < 50:
                    eq._respawn()
                    placed = True

                    # Create rectangle for new equation + answer buttons
                    eq_rect = pygame.Rect(
                        eq.x - 180,
                        eq.y,
                        360,
                        90
                    )

                    for other in equations:
                        if other is not eq and other.active:

                            other_rect = pygame.Rect(
                                other.x - 180,
                                other.y,
                                360,
                                90
                            )

                            # Prevent touching or overlap
                            expanded_other = other_rect.inflate(80, 60)

                            if eq_rect.colliderect(expanded_other):
                                placed = False
                                break

                    attempts += 1

                break

    # Update all equations
    for eq in equations:
        eq.update()
        if game_over or game_won:
            running = False


    # Move clouds
    for cloud in clouds:
        cloud["x"] += cloud["speed"]
        if cloud["x"] > SCREEN_WIDTH + 30:
            cloud["x"] = -70

    # Draw background
    screen.fill(BLUE_SKY)

    # Draw clouds
    for cloud in clouds:
        draw_cloud(screen, cloud["x"], cloud["y"], cloud["size"])

    # Draw grass
    pygame.draw.rect(screen, GREEN_GRASS, (0, grass_y_position, SCREEN_WIDTH, GRASS_HEIGHT))

    # Draw equations
    for eq in equations:
        eq.draw(screen)

    # Draw character
    draw_character(screen, player_x, player_y, facing, walk_frame, on_ground)

    # HUD — score, timer, lives
    mins = timer_seconds // 60
    secs = timer_seconds % 60
    timer_str   = f"{mins}:{secs:02d}"
    timer_color = (220, 50, 50) if timer_seconds <= 30 else GOLD  # red when under 30s

    score_txt = font_ui.render(f"Score: {score}", True, GOLD)
    timer_txt = font_ui.render(timer_str, True, timer_color)
    lives_txt = font_ui.render("Lives: " + "♥ " * lives, True, (220, 50, 50))

    screen.blit(score_txt, (10, 10))
    screen.blit(timer_txt, timer_txt.get_rect(centerx=SCREEN_WIDTH // 2, y=10))
    screen.blit(lives_txt, (SCREEN_WIDTH - 180, 10))

    pygame.display.flip()
    clock.tick(60)

# ---------------- WIN SCREEN ----------------
while game_won:
    screen.fill((30, 30, 30))

    title = title_font.render("YOU WIN!", True, CORRECT_GREEN)

    score_text = instruction_font.render(
        f"Final Score: {score}", True, WHITE
    )

    restart_text = small_font.render(
        "Press R to Play Again", True, GOLD
    )

    quit_text = small_font.render(
        "Press Q to Quit", True, WHITE
    )

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
    screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 260)))
    screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, 340)))
    screen.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH // 2, 390)))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_r:
                score = 0
                lives = 3
                timer_seconds = 120
                timer_ms = 0

                player_x = 100
                player_y = float(ground_level)
                player_vel_y = 0
                on_ground = True

                equations = [FallingEquation() for _ in range(MAX_EQUATIONS)]

                for i in range(1, MAX_EQUATIONS):
                    equations[i].active = False

                spawn_timer = 0

                running = True
                game_won = False

            
# ---------------- GAME OVER SCREEN ----------------
while game_over:
    screen.fill((30, 30, 30))

    title = title_font.render("GAME OVER", True, WRONG_RED)
    score_text = instruction_font.render(
        f"Final Score: {score}", True, WHITE
    )

    restart_text = small_font.render(
        "Press R to Restart", True, GOLD
    )

    quit_text = small_font.render(
        "Press Q to Quit", True, WHITE
    )

    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 180)))
    screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, 260)))
    screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH // 2, 340)))
    screen.blit(quit_text, quit_text.get_rect(center=(SCREEN_WIDTH // 2, 390)))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

            if event.key == pygame.K_r:
                # Reset game state
                score = 0
                lives = 3
                timer_seconds = 120
                timer_ms = 0

                player_x = 100
                player_y = float(ground_level)
                player_vel_y = 0
                on_ground = True

                equations = [FallingEquation() for _ in range(MAX_EQUATIONS)]

                for i in range(1, MAX_EQUATIONS):
                    equations[i].active = False

                spawn_timer = 0

                running = True
                game_over = False
                game_won = False

pygame.quit()
sys.exit() 
