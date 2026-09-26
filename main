import pygame
import sys
import random

from src.player import Player
from src.npc import NPC


pygame.init()

WIDTH = 1280
HEIGHT = 720

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Endless Racing"
)

clock = pygame.time.Clock()

ROAD_WIDTH = 600
SEGMENT_LENGTH = 30

ROAD_COLOR = (55, 55, 55)
GRASS_COLOR = (30, 125, 45)
EDGE_COLOR = (235, 235, 235)
LINE_COLOR = (255, 205, 35)

road = []

road_x = 0
road_y = 400

curve = 0
target_curve = 0
curve_timer = 0


def choose_curve():

    global target_curve
    global curve_timer

    direction = random.choice(
        [-1, 1]
    )

    strength = random.choice(
        [
            0.020,
            0.025,
            0.030,
            0.035
        ]
    )

    target_curve = direction * strength

    curve_timer = random.randint(
        250,
        450
    )


def generate_segment():

    global road_x
    global road_y
    global curve
    global target_curve
    global curve_timer

    if curve_timer <= 0:
        choose_curve()

    curve += (
        target_curve -
        curve
    ) * 0.025

    road.append(
        (
            road_x,
            road_y
        )
    )

    road_x += (
        curve *
        SEGMENT_LENGTH
    )

    road_y -= SEGMENT_LENGTH

    curve_timer -= 1


for _ in range(2500):
    generate_segment()


def get_road_center(y):

    if len(road) < 2:
        return 0

    closest_x = road[0][0]

    closest_difference = abs(
        road[0][1] -
        y
    )

    for x, point_y in road:

        difference = abs(
            point_y -
            y
        )

        if difference < closest_difference:

            closest_difference = difference
            closest_x = x

    return closest_x


def draw_road():

    visible_points = []

    top = camera_y - 500

    bottom = (
        camera_y +
        HEIGHT +
        500
    )

    for x, y in road:

        if top <= y <= bottom:

            visible_points.append(
                (
                    x - camera_x,
                    y - camera_y
                )
            )

    if len(visible_points) < 2:
        return

    half_width = ROAD_WIDTH / 2

    left_edge = []
    right_edge = []

    for i in range(
        len(visible_points)
    ):

        x, y = visible_points[i]

        if i == 0:

            x2, y2 = visible_points[i + 1]

            dx = x2 - x
            dy = y2 - y

        elif i == len(visible_points) - 1:

            x2, y2 = visible_points[i - 1]

            dx = x - x2
            dy = y - y2

        else:

            x1, y1 = visible_points[i - 1]
            x2, y2 = visible_points[i + 1]

            dx = x2 - x1
            dy = y2 - y1

        length = max(
            1,
            (dx * dx + dy * dy) ** 0.5
        )

        nx = -dy / length
        ny = dx / length

        left_edge.append(
            (
                x + nx * half_width,
                y + ny * half_width
            )
        )

        right_edge.append(
            (
                x - nx * half_width,
                y - ny * half_width
            )
        )

    pygame.draw.polygon(
        screen,
        ROAD_COLOR,
        left_edge +
        right_edge[::-1]
    )

    pygame.draw.lines(
        screen,
        EDGE_COLOR,
        False,
        left_edge,
        6
    )

    pygame.draw.lines(
        screen,
        EDGE_COLOR,
        False,
        right_edge,
        6
    )

    for i in range(
        0,
        len(visible_points) - 1,
        4
    ):

        x1, y1 = visible_points[i]
        x2, y2 = visible_points[i + 1]

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (
                int(x1),
                int(y1)
            ),
            (
                int(x2),
                int(y2)
            ),
            5
        )


def create_npc(
    distance,
    lane,
    lane_change
):

    npc_y = (
        player.position.y -
        distance
    )

    road_center = get_road_center(
        npc_y
    )

    return NPC(
        road_center + lane,
        npc_y,
        lane_change
    )


def create_traffic():

    return [
        create_npc(
            250,
            -180,
            False
        ),
        create_npc(
            500,
            0,
            False
        ),
        create_npc(
            750,
            180,
            True
        ),
        create_npc(
            1000,
            -180,
            True
        ),
        create_npc(
            1250,
            180,
            False
        ),
        create_npc(
            1500,
            0,
            True
        ),
        create_npc(
            1750,
            -180,
            False
        ),
        create_npc(
            2000,
            180,
            True
        )
    ]


def npc_collision(a, b):

    return (
        abs(
            a.position.x -
            b.position.x
        ) < 38
        and
        abs(
            a.position.y -
            b.position.y
        ) < 65
    )


def player_collision(
    player,
    npc
):

    return (
        abs(
            player.position.x -
            npc.position.x
        ) < 34
        and
        abs(
            player.position.y -
            npc.position.y
        ) < 58
    )


def separate_npcs():

    for i in range(
        len(npcs)
    ):

        for j in range(
            i + 1,
            len(npcs)
        ):

            a = npcs[i]
            b = npcs[j]

            if npc_collision(a, b):

                difference = (
                    a.position -
                    b.position
                )

                if difference.length_squared() == 0:

                    difference = pygame.Vector2(
                        1,
                        0
                    )

                direction = (
                    difference.normalize()
                )

                overlap_x = (
                    38 -
                    abs(
                        a.position.x -
                        b.position.x
                    )
                )

                overlap_y = (
                    65 -
                    abs(
                        a.position.y -
                        b.position.y
                    )
                )

                if overlap_x < overlap_y:

                    push = pygame.Vector2(
                        direction.x,
                        0
                    )

                    a.position += (
                        push *
                        (overlap_x / 2)
                    )

                    b.position -= (
                        push *
                        (overlap_x / 2)
                    )

                else:

                    if (
                        a.position.y <
                        b.position.y
                    ):

                        a.speed = min(
                            a.speed,
                            b.speed
                        )

                    else:

                        b.speed = min(
                            b.speed,
                            a.speed
                        )


def reset_game():

    global player
    global npcs
    global camera_x
    global camera_y

    player = Player()

    camera_x = 0

    camera_y = (
        player.position.y -
        500
    )

    npcs = create_traffic()


player = Player()

camera_x = 0

camera_y = (
    player.position.y -
    500
)

npcs = create_traffic()

game_over = False

controls_start_time = pygame.time.get_ticks()

controls_duration = 5000

show_controls = True

close_button = pygame.Rect(
    WIDTH // 2 - 100,
    550,
    200,
    55
)

running = True


while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if (
                show_controls
                and
                close_button.collidepoint(
                    event.pos
                )
            ):

                show_controls = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_q:

                running = False

            elif event.key == pygame.K_ESCAPE:

                running = False

            elif event.key == pygame.K_r:

                reset_game()

                game_over = False


    if not game_over:

        player.update()

        while (
            road[-1][1] >
            player.position.y -
            20000
        ):

            generate_segment()

        for npc in npcs:

            npc_center = get_road_center(
                npc.position.y
            )

            npc.update(
                npc_center,
                npcs
            )

        separate_npcs()

        for npc in npcs:

            if (
                npc.position.y >
                player.position.y +
                1000
            ):

                new_distance = random.randint(
                    1800,
                    3500
                )

                npc_y = (
                    player.position.y -
                    new_distance
                )

                road_center = get_road_center(
                    npc_y
                )

                lane = random.choice(
                    [
                        -180,
                        0,
                        180
                    ]
                )

                npc.position = pygame.Vector2(
                    road_center + lane,
                    npc_y
                )

                npc.target_x = (
                    road_center + lane
                )

                npc.lane_change = random.choice(
                    [
                        False,
                        False,
                        True
                    ]
                )

                npc.speed = random.uniform(
                    6,
                    10
                )

        for npc in npcs:

            if player_collision(
                player,
                npc
            ):

                game_over = True

                break

        road_center = get_road_center(
            player.position.y
        )

        if (
            abs(
                player.position.x -
                road_center
            ) >
            ROAD_WIDTH / 2
        ):

            player.velocity *= 0.97

        target_camera_x = (
            player.position.x -
            WIDTH / 2
        )

        target_camera_y = (
            player.position.y -
            500
        )

        camera_x += (
            target_camera_x -
            camera_x
        ) * 0.08

        camera_y += (
            target_camera_y -
            camera_y
        ) * 0.08


    screen.fill(
        GRASS_COLOR
    )

    draw_road()


    for npc in npcs:

        npc_screen_position = pygame.Vector2(
            npc.position.x -
            camera_x,
            npc.position.y -
            camera_y
        )

        if (
            -100 <
            npc_screen_position.x <
            WIDTH + 100
            and
            -100 <
            npc_screen_position.y <
            HEIGHT + 100
        ):

            npc.draw(
                screen,
                npc_screen_position
            )


    player_position = pygame.Vector2(
        player.position.x -
        camera_x,
        player.position.y -
        camera_y
    )

    player.draw(
        screen,
        player_position
    )


    if not game_over:

        forward = pygame.Vector2(
            0,
            -1
        )

        speed = abs(
            player.velocity.dot(
                forward
            )
        )

        font = pygame.font.Font(
            None,
            32
        )

        speed_text = font.render(
            f"SPEED {int(speed)}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            speed_text,
            (30, 25)
        )


    current_time = pygame.time.get_ticks()

    controls_elapsed = (
        current_time -
        controls_start_time
    )


    if (
        show_controls
        and
        controls_elapsed < controls_duration
    ):

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 170)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        title_font = pygame.font.Font(
            None,
            72
        )

        control_font = pygame.font.Font(
            None,
            38
        )

        small_font = pygame.font.Font(
            None,
            30
        )

        title = title_font.render(
            "CONTROLS",
            True,
            (255, 255, 255)
        )

        controls_1 = control_font.render(
            "W / UP       Accelerate",
            True,
            (255, 255, 255)
        )

        controls_2 = control_font.render(
            "S / DOWN     Brake / Reverse",
            True,
            (255, 255, 255)
        )

        controls_3 = control_font.render(
            "A / LEFT     Move Left",
            True,
            (255, 255, 255)
        )

        controls_4 = control_font.render(
            "D / RIGHT    Move Right",
            True,
            (255, 255, 255)
        )

        controls_5 = small_font.render(
            "R = Restart     Q / ESC = Quit",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            title.get_rect(
                center=(
                    WIDTH // 2,
                    170
                )
            )
        )

        screen.blit(
            controls_1,
            controls_1.get_rect(
                center=(
                    WIDTH // 2,
                    270
                )
            )
        )

        screen.blit(
            controls_2,
            controls_2.get_rect(
                center=(
                    WIDTH // 2,
                    325
                )
            )
        )

        screen.blit(
            controls_3,
            controls_3.get_rect(
                center=(
                    WIDTH // 2,
                    380
                )
            )
        )

        screen.blit(
            controls_4,
            controls_4.get_rect(
                center=(
                    WIDTH // 2,
                    435
                )
            )
        )

        screen.blit(
            controls_5,
            controls_5.get_rect(
                center=(
                    WIDTH // 2,
                    495
                )
            )
        )

        pygame.draw.rect(
            screen,
            (190, 45, 45),
            close_button,
            border_radius=8
        )

        close_font = pygame.font.Font(
            None,
            32
        )

        close_text = close_font.render(
            "CLOSE",
            True,
            (255, 255, 255)
        )

        screen.blit(
            close_text,
            close_text.get_rect(
                center=close_button.center
            )
        )


    if game_over:

        overlay = pygame.Surface(
            (
                WIDTH,
                HEIGHT
            ),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 0, 180)
        )

        screen.blit(
            overlay,
            (0, 0)
        )

        game_over_font = pygame.font.Font(
            None,
            90
        )

        instruction_font = pygame.font.Font(
            None,
            38
        )

        game_over_text = game_over_font.render(
            "GAME OVER",
            True,
            (255, 255, 255)
        )

        instruction_text = instruction_font.render(
            "R = RETRY     Q / ESC = QUIT",
            True,
            (255, 255, 255)
        )

        screen.blit(
            game_over_text,
            game_over_text.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 - 50
                )
            )
        )

        screen.blit(
            instruction_text,
            instruction_text.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 + 50
                )
            )
        )


    pygame.display.flip()

    clock.tick(60)


pygame.quit()

sys.exit()
