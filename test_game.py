import pygame
import sys
import math
import random

pygame.init()

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
    ("x + 7 = 15",         8,              [6, 10, 22]),
    ("3x = 27",            9,              [6, 12, 81]),
    ("2x + 5 = 19",        7,              [4, 12, 6]),
    ("5x - 8 = 17",        5,              [3, 9, 7]),
    ("4(x+2) = 28",        5,              [7, 3, 9]),
    ("3x-7 = 2x+9",       16,             [2, 8, 12]),
    ("2(x-4)+3 = 11",      6,              [2, 4, 8]),
    ("5x+2 = 3x+18",       8,              [4, 10, 16]),
    ("x^2 = 49",           7,              [-7, 14, 24]),
    ("x^2 - 16 = 0",       4,              [-4, 8, 2]),
    ("x^2+7x+12=0",       -3,             [-4, 3, 4]),
    ("2x^2 - 8x = 0",      4,              [0, 2, 8]),
    ("x^2-5x+6=0",         2,              [3, 1, 6]),
    ("(x+3)/2 = 7/2",      4,              [2, 7, 1]),
    ("|x - 4| = 9",        13,             [-5, 5, 4]),
    ("|2x + 1| = 7",        3,              [-4, 4, 6]),
    ("x^2-2x-15=0",        5,              [-3, 3, 7]),
    ("x/(x-2) = 3",         3,              [1, 6, -3]),
    ("x + 5 = x - 1",  "No solution", ["x=0", "x=5", "x=-5"]),
    ("(2x-1)/3=(x+5)/2",  17,             [7, 11, 3]),
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
        self.x     = random.randint(self.WIDTH // 2 + 10,
                                    SCREEN_WIDTH - self.WIDTH // 2 - 10)
        self.y     = -self.HEIGHT
        self.speed = random.uniform(0.6, 0.8)
        self.active   = True
        self.answered = False
        self.flash    = 0
        self.flash_col = WHITE

        options = wrongs[:3] + [self.answer]
        random.shuffle(options)
        self.choices = []
        bw, bh = 88, 32
        for i, val in enumerate(options):
            bx = self.x - self.WIDTH // 2 + i * (bw + 4)
            by = self.y + self.HEIGHT + 4
            self.choices.append(AnswerChoice(bx, by, bw, bh, val))

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
        global lives
        lives -= 1
        self.answered  = True
        self.flash     = 80
        self.flash_col = WRONG_RED

    def check_answer(self, chosen):
        global score, lives, timer_seconds
        self.answered = True
        if chosen == self.answer:
            score         += 10
            timer_seconds += 5             # +5 seconds for correct answer
            self.flash_col = CORRECT_GREEN
        else:
            lives         -= 1
            timer_seconds -= 5             # -5 seconds for wrong answer
            timer_seconds  = max(0, timer_seconds)  # can't go below 0
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
SPAWN_INTERVAL = 600
spawn_timer    = 0
equations      = [FallingEquation() for _ in range(MAX_EQUATIONS)]

# Only the first starts active & others wait for the spawn timer
for i in range(1, MAX_EQUATIONS):
    equations[i].active = False

clock = pygame.time.Clock()
running = True

while running:
    # Tick the countdown timer using milliseconds since last frame
    dt = clock.get_time()
    timer_ms += dt
    if timer_ms >= 1000:
        timer_ms      -= 1000
        timer_seconds -= 1
        if timer_seconds <= 0:
            timer_seconds = 0
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
                eq._respawn()
                break

    # Update all equations
    for eq in equations:
        eq.update()

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

pygame.quit()
sys.exit() 
