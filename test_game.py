import pygame
import sys
import math

pygame.init()

# Screen setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blue Sky and Green Grass Background")

# Colors
BLUE_SKY = (135, 206, 235)
GREEN_GRASS = (34, 139, 34)

SKIN      = (255, 200, 150)
BROWN     = (139, 90, 43)
ORANGE    = (255, 140, 0)
DARK_BLUE = (30, 60, 120)
GOLD      = (255, 215, 0)
WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)

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

# Cloud settings
clouds = [
    {"x": 100, "y": 70,  "speed": 0.4, "size": 1.0},
    {"x": 350, "y": 150, "speed": 0.6, "size": 1.3},
    {"x": 600, "y": 270, "speed": 0.3, "size": 0.9},
    {"x": 200, "y": 350, "speed": 0.5, "size": 1.1},
]


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
    pygame.draw.ellipse(surface, BROWN, (le2[0] - 7, le2[1] - 4, 14, 8))

    # Body
    pygame.draw.rect(surface, ORANGE, (x - 14, y - 44, 28, 34), border_radius=6)
    pygame.draw.rect(surface, BROWN, (x - 14, y - 22, 28, 5))

    # arm swing
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


clock = pygame.time.Clock()
running = True

while running:
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

    # Walking animation
    walk_frame += 0.15

    # Move clouds
    for cloud in clouds:
        cloud["x"] += cloud["speed"]

        # Wrap clouds back to left side
        if cloud["x"] > SCREEN_WIDTH + 30:
            cloud["x"] = -70

    # Draw background
    screen.fill(BLUE_SKY)

    # Draw clouds
    for cloud in clouds:
        draw_cloud(
            screen,
            cloud["x"],
            cloud["y"],
            cloud["size"]
        )

    # Draw grass
    pygame.draw.rect(
        screen,
        GREEN_GRASS,
        (0, grass_y_position, SCREEN_WIDTH, GRASS_HEIGHT)
    )

    # Draw character
    draw_character(
        screen,
        player_x,
        player_y,
        facing,
        walk_frame,
        on_ground
    )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()