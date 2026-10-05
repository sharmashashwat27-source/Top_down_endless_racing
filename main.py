import math
import os
import random
import sys

import pygame

from src.coin import Coin, Gem
from src.npc import NPC, LANES
from src.player import Player


pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Racing")

clock = pygame.time.Clock()

ROAD_WIDTH = 600
SEGMENT_LENGTH = 30
START_Y = 400

START_LIVES = 3
BASE_NPCS = 8
MAX_NPCS = 22

ROAD_COLOR = (55, 55, 55)
GRASS_COLOR = (30, 125, 45)
EDGE_COLOR = (235, 235, 235)
LINE_COLOR = (255, 205, 35)

WHITE = (255, 255, 255)

SAVE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "highscore.txt"
)

FONT_HUD = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 30)
FONT_CONTROL = pygame.font.Font(None, 38)
FONT_TITLE = pygame.font.Font(None, 72)
FONT_BIG = pygame.font.Font(None, 90)
FONT_POPUP = pygame.font.Font(None, 40)


# ------------------------------------------------------------------ high score

def load_high_score():

    try:
        with open(SAVE_FILE) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def save_high_score(value):

    try:
        with open(SAVE_FILE, "w") as f:
            f.write(str(value))
    except OSError:
        pass


# ------------------------------------------------------------------------ road

road = []
road_offset = 0          # how many old segments were pruned (keeps dashes stable)

road_x = 0
road_y = 0

curve = 0
target_curve = 0
curve_timer = 0


def choose_curve():

    global target_curve
    global curve_timer

    direction = random.choice([-1, 1])

    strength = random.choice([0.020, 0.025, 0.030, 0.035])

    target_curve = direction * strength

    curve_timer = random.randint(250, 450)


def generate_segment():

    global road_x
    global road_y
    global curve
    global curve_timer

    if curve_timer <= 0:
        choose_curve()

    curve += (target_curve - curve) * 0.025

    road.append((road_x, road_y))

    road_x += curve * SEGMENT_LENGTH

    road_y -= SEGMENT_LENGTH

    curve_timer -= 1


def init_road():
    """Build a fresh road. It starts BEHIND the player so there is no cut-off."""

    global road, road_offset
    global road_x, road_y
    global curve, target_curve, curve_timer

    road = []
    road_offset = 0

    road_x = 0
    road_y = START_Y + SEGMENT_LENGTH * 40

    curve = 0
    target_curve = 0
    curve_timer = 150        # start with a short straight

    for _ in range(800):
        generate_segment()


def prune_road():
    """Drop segments far behind the player so the list never grows forever."""

    global road_offset

    limit = player.position.y + 1500

    remove = 0

    while remove < len(road) - 2 and road[remove][1] > limit:
        remove += 1

    if remove:
        del road[:remove]
        road_offset += remove


def get_road_center(y):
    """Interpolated road centre at world height y (segments are evenly spaced)."""

    if len(road) < 2:
        return 0

    position = (road[0][1] - y) / SEGMENT_LENGTH

    position = max(0, min(len(road) - 1.001, position))

    i = int(position)
    t = position - i

    return road[i][0] + (road[i + 1][0] - road[i][0]) * t


def draw_road():

    first_y = road[0][1]

    i0 = max(
        0,
        int((first_y - (camera_y + HEIGHT + 500)) / SEGMENT_LENGTH)
    )

    i1 = min(
        len(road),
        int((first_y - (camera_y - 500)) / SEGMENT_LENGTH) + 2
    )

    points = road[i0:i1]

    if len(points) < 2:
        return

    visible = [(x - camera_x, y - camera_y) for x, y in points]

    half_width = ROAD_WIDTH / 2

    left_edge = []
    right_edge = []

    last = len(visible) - 1

    for i, (x, y) in enumerate(visible):

        ax, ay = visible[max(i - 1, 0)]
        bx, by = visible[min(i + 1, last)]

        dx = bx - ax
        dy = by - ay

        length = max(1, math.hypot(dx, dy))

        nx = -dy / length
        ny = dx / length

        left_edge.append((x + nx * half_width, y + ny * half_width))
        right_edge.append((x - nx * half_width, y - ny * half_width))

    pygame.draw.polygon(screen, ROAD_COLOR, left_edge + right_edge[::-1])

    pygame.draw.lines(screen, EDGE_COLOR, False, left_edge, 6)
    pygame.draw.lines(screen, EDGE_COLOR, False, right_edge, 6)

    for i in range(len(visible) - 1):

        if (road_offset + i0 + i) % 4 != 0:
            continue

        x1, y1 = visible[i]
        x2, y2 = visible[i + 1]

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            5
        )


# --------------------------------------------------------------------- helpers

def distance_m():

    return max(0, (START_Y - player.position.y) / 20)


def current_score():

    return int(distance_m()) + bonus_score


def progress():
    """0 at the start, 1 after about 5000 m. Everything that gets harder uses this."""

    return min(1.0, distance_m() / 5000)


def difficulty():
    """NPC speed multiplier, grows slowly the further you drive."""

    return 1 + 0.25 * progress()


def add_popup(text, color=WHITE):

    popups.append([text, 70, color])

    del popups[:-4]


# ------------------------------------------------------------------------- NPCs

def lane_change_chance():

    return 0.3 + 0.4 * progress()


def spawn_clear(x, y, width, height, ignore=None):
    """True if a vehicle of this size at (x, y) would not touch any other NPC."""

    for other in npcs:

        if other is ignore:
            continue

        if (
            abs(other.position.x - x) < (width + other.width) / 2 + 30
            and abs(other.position.y - y) < (height + other.height) / 2 + 140
        ):
            return False

    return True


def find_spawn(ignore=None):
    """Pick a free spot ON the road ahead. Returns None if nothing is free right now."""

    p = progress()

    near = int(1800 - 600 * p)
    far = int(3500 - 1000 * p)

    for _ in range(30):

        kind = NPC.random_kind()

        spec = NPC.KINDS[kind]

        y = player.position.y - random.randint(near, far)

        lane = random.choice(LANES)

        center = get_road_center(y)

        if spawn_clear(center + lane, y, spec["w"], spec["h"], ignore):
            return kind, center, y, lane

    return None


def create_npc(distance, lane, lane_change):

    npc_y = player.position.y - distance

    return NPC(
        get_road_center(npc_y),
        npc_y,
        lane,
        lane_change,
        difficulty()
    )


def create_traffic():

    return [
        create_npc(250, -180, False),
        create_npc(500, 0, False),
        create_npc(750, 180, True),
        create_npc(1000, -180, True),
        create_npc(1250, 180, False),
        create_npc(1500, 0, True),
        create_npc(1750, -180, False),
        create_npc(2000, 180, True)
    ]


def respawn_npc(npc):

    spot = find_spawn(npc)

    if spot is None:
        return False

    kind, center, y, lane = spot

    npc.respawn(
        center,
        y,
        lane,
        random.random() < lane_change_chance(),
        difficulty(),
        kind
    )

    return True


def add_npc():

    spot = find_spawn()

    if spot is None:
        return

    kind, center, y, lane = spot

    npcs.append(
        NPC(
            center,
            y,
            lane,
            random.random() < lane_change_chance(),
            difficulty(),
            kind
        )
    )


def player_collision(player, npc):

    return (
        abs(player.position.x - npc.position.x)
        < (player.width + npc.width) / 2 - 2
        and abs(player.position.y - npc.position.y)
        < (player.height + npc.height) / 2 - 10
    )


def separate_npcs():
    """Safety net: if two vehicles ever overlap, the one behind drops back."""

    for i in range(len(npcs)):

        for j in range(i + 1, len(npcs)):

            a = npcs[i]
            b = npcs[j]

            min_dx = (a.width + b.width) / 2 + 4
            min_dy = (a.height + b.height) / 2 + 6

            if (
                abs(a.position.x - b.position.x) >= min_dx
                or abs(a.position.y - b.position.y) >= min_dy
            ):
                continue

            if a.position.y > b.position.y:
                back, front = a, b
            else:
                back, front = b, a

            back.position.y = front.position.y + min_dy
            back.speed = min(back.speed, front.speed)


# ------------------------------------------------------------------ coins & gems

def spawn_coin_line():

    lane = random.choice(LANES)

    start = player.position.y - random.randint(1500, 3000)

    for i in range(random.randint(4, 7)):

        y = start - i * 70

        coins.append(Coin(get_road_center(y) + lane, y))


def spawn_gem():

    y = player.position.y - random.randint(1500, 3000)

    gems.append(Gem(get_road_center(y) + random.choice(LANES), y))


# ------------------------------------------------------------------------ state

def reset_game():

    global player, npcs, coins, gems, popups
    global camera_x, camera_y
    global lives, bonus_score, coin_count, gem_count
    global game_over, paused, new_best

    player = Player()

    init_road()

    camera_x = 0
    camera_y = player.position.y - 500

    npcs = create_traffic()
    coins = []
    gems = []
    popups = []

    lives = START_LIVES
    bonus_score = 0
    coin_count = 0
    gem_count = 0

    game_over = False
    paused = False
    new_best = False


high_score = load_high_score()

reset_game()

controls_start_time = pygame.time.get_ticks()
controls_duration = 5000
show_controls = True

close_button = pygame.Rect(WIDTH // 2 - 100, 590, 200, 55)

frame = 0


# ---------------------------------------------------------------------- drawing

def dim(alpha):

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))


def draw_centered(text, font, y, color=WHITE):

    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))


def draw_heart(x, y, color):

    pygame.draw.circle(screen, color, (x - 6, y - 3), 7)
    pygame.draw.circle(screen, color, (x + 6, y - 3), 7)
    pygame.draw.polygon(screen, color, [(x - 13, y), (x + 13, y), (x, y + 14)])


def draw_hud():

    speed = abs(player.velocity.y)

    kmh = int(speed * 10.8)

    screen.blit(FONT_HUD.render(f"SPEED {kmh} KM/H", True, WHITE), (30, 25))
    screen.blit(FONT_HUD.render(f"SCORE {current_score()}", True, WHITE), (30, 55))
    screen.blit(
        FONT_HUD.render(f"BEST {max(high_score, current_score())}", True, (255, 220, 120)),
        (30, 85)
    )
    screen.blit(
        FONT_HUD.render(f"COINS {coin_count}", True, (255, 160, 40)),
        (30, 115)
    )
    screen.blit(
        FONT_HUD.render(f"GEMS {gem_count}", True, (255, 130, 235)),
        (30, 145)
    )

    # lives
    for i in range(START_LIVES):

        color = (225, 50, 60) if i < lives else (70, 70, 70)

        draw_heart(WIDTH - 40 - i * 36, 40, color)

    # nitro bar
    bar = pygame.Rect(30, HEIGHT - 50, 220, 18)

    pygame.draw.rect(screen, (20, 20, 20), bar, border_radius=6)

    fill = bar.copy()
    fill.width = int(bar.width * player.nitro / player.max_nitro)

    fill_color = (120, 120, 120) if player.nitro_locked else (255, 140, 30)

    if fill.width > 0:
        pygame.draw.rect(screen, fill_color, fill, border_radius=6)

    pygame.draw.rect(screen, WHITE, bar, 2, border_radius=6)

    screen.blit(FONT_SMALL.render("NITRO (SHIFT)", True, WHITE), (30, HEIGHT - 78))

    # popups
    for i, (text, timer, color) in enumerate(popups):

        surface = FONT_POPUP.render(text, True, color)
        surface.set_alpha(min(255, timer * 8))

        screen.blit(surface, surface.get_rect(center=(WIDTH // 2, 120 + i * 38)))


def draw_controls():

    dim(170)

    draw_centered("CONTROLS", FONT_TITLE, 110)

    lines = [
        "W / UP       Accelerate",
        "S / DOWN     Brake / Reverse",
        "A / LEFT     Move Left",
        "D / RIGHT    Move Right",
        "SHIFT        Nitro Boost",
        "P            Pause"
    ]

    for i, line in enumerate(lines):
        draw_centered(line, FONT_CONTROL, 190 + i * 50)

    draw_centered("R = Restart     Q / ESC = Quit", FONT_SMALL, 505)
    draw_centered("Grab coins, dodge traffic, you have 3 lives", FONT_SMALL, 540)

    pygame.draw.rect(screen, (190, 45, 45), close_button, border_radius=8)

    close_text = FONT_HUD.render("CLOSE", True, WHITE)
    screen.blit(close_text, close_text.get_rect(center=close_button.center))


def draw_game_over():

    dim(180)

    draw_centered("GAME OVER", FONT_BIG, HEIGHT // 2 - 90)
    draw_centered(f"SCORE {current_score()}", FONT_CONTROL, HEIGHT // 2 - 20)

    if new_best:
        draw_centered("NEW BEST!", FONT_CONTROL, HEIGHT // 2 + 20, (255, 220, 120))
    else:
        draw_centered(f"BEST {high_score}", FONT_CONTROL, HEIGHT // 2 + 20)

    draw_centered("R = RETRY     Q / ESC = QUIT", FONT_CONTROL, HEIGHT // 2 + 90)


def draw_pause():

    dim(140)

    draw_centered("PAUSED", FONT_BIG, HEIGHT // 2 - 20)
    draw_centered("P = RESUME", FONT_CONTROL, HEIGHT // 2 + 50)


# -------------------------------------------------------------------- main loop

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if show_controls and close_button.collidepoint(event.pos):
                show_controls = False

        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                running = False

            elif event.key == pygame.K_r:
                reset_game()

            elif event.key == pygame.K_p:

                if not game_over and not show_controls:
                    paused = not paused

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):

                show_controls = False

    if (
        show_controls
        and pygame.time.get_ticks() - controls_start_time >= controls_duration
    ):
        show_controls = False

    playing = not (game_over or paused or show_controls)

    if playing:

        frame += 1

        player.update()

        prune_road()

        while road[-1][1] > player.position.y - 20000:
            generate_segment()

        # ---- NPCs
        for npc in npcs:
            npc.update(get_road_center(npc.position.y), npcs)

        separate_npcs()

        speed = abs(player.velocity.y)

        for npc in npcs:

            if (
                npc.position.y > player.position.y + 1000
                or npc.position.y < player.position.y - 5000
            ):
                respawn_npc(npc)
                continue

            # near miss bonus: you overtook a car that was close but not touching
            if not npc.passed and npc.position.y > player.position.y:

                npc.passed = True

                gap = abs(npc.position.x - player.position.x)

                if 34 <= gap < 75 and speed > 6:

                    bonus_score += 25
                    add_popup("NEAR MISS +25", (120, 220, 255))

        # more and more traffic the further you go
        target_npcs = BASE_NPCS + int(progress() * (MAX_NPCS - BASE_NPCS))

        if len(npcs) < target_npcs:
            add_npc()

        # ---- coins
        if len(coins) < 10:
            spawn_coin_line()

        remaining = []

        for coin in coins:

            if coin.position.y > player.position.y + 800:
                continue

            if (
                abs(coin.position.x - player.position.x) < 32
                and abs(coin.position.y - player.position.y) < 50
            ):
                coin_count += 1
                bonus_score += 50
                continue

            remaining.append(coin)

        coins = remaining

        # ---- gems
        remaining_gems = []

        for gem in gems:

            if gem.position.y > player.position.y + 800:
                continue

            if (
                abs(gem.position.x - player.position.x) < 34
                and abs(gem.position.y - player.position.y) < 50
            ):
                gem_count += 1
                bonus_score += Gem.VALUE
                add_popup(f"GEM +{Gem.VALUE}", (255, 130, 235))
                continue

            remaining_gems.append(gem)

        gems = remaining_gems

        if not gems and random.random() < 0.002:
            spawn_gem()

        # ---- crashes
        if player.invincible <= 0:

            for npc in npcs:

                if player_collision(player, npc):

                    lives -= 1

                    player.hit()
                    respawn_npc(npc)

                    if lives <= 0:

                        game_over = True

                        score = current_score()

                        if score > high_score:
                            high_score = score
                            new_best = True
                            save_high_score(high_score)

                    else:
                        add_popup("CRASH!", (255, 90, 90))

                    break

        # ---- off-road slowdown
        if abs(player.position.x - get_road_center(player.position.y)) > ROAD_WIDTH / 2:
            player.velocity *= 0.97

        # ---- camera
        target_camera_x = player.position.x - WIDTH / 2
        target_camera_y = player.position.y - 500

        camera_x += (target_camera_x - camera_x) * 0.08
        camera_y += (target_camera_y - camera_y) * 0.08

        # ---- popups
        for popup in popups:
            popup[1] -= 1

        popups = [p for p in popups if p[1] > 0]

    # ------------------------------------------------------------------- draw
    screen.fill(GRASS_COLOR)

    draw_road()

    for coin in coins:

        pos = pygame.Vector2(
            coin.position.x - camera_x,
            coin.position.y - camera_y
        )

        if -50 < pos.y < HEIGHT + 50:
            coin.draw(screen, pos, frame)

    for gem in gems:

        pos = pygame.Vector2(
            gem.position.x - camera_x,
            gem.position.y - camera_y
        )

        if -50 < pos.y < HEIGHT + 50:
            gem.draw(screen, pos, frame)

    for npc in npcs:

        pos = pygame.Vector2(
            npc.position.x - camera_x,
            npc.position.y - camera_y
        )

        if -150 < pos.x < WIDTH + 150 and -150 < pos.y < HEIGHT + 150:
            npc.draw(screen, pos)

    player.draw(
        screen,
        pygame.Vector2(
            player.position.x - camera_x,
            player.position.y - camera_y
        )
    )

    if not game_over:
        draw_hud()

    if show_controls:
        draw_controls()

    if paused:
        draw_pause()

    if game_over:
        draw_game_over()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()

sys.exit()
