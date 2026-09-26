import pygame
import random


class NPC:

    COLORS = [
        (40, 120, 220),
        (230, 190, 40),
        (40, 180, 90),
        (170, 60, 210),
        (240, 100, 40),
        (220, 50, 60),
        (230, 230, 230),
        (40, 190, 190)
    ]

    def __init__(self, x, y, lane_change=False):

        self.position = pygame.Vector2(x, y)

        self.speed = random.uniform(6, 10)
        self.base_speed = self.speed

        self.lane_change = lane_change

        self.color = random.choice(self.COLORS)

        self.target_x = x

        self.change_timer = random.randint(
            180,
            300
        )

        self.lean = 0

        self.width = 36
        self.height = 68

    def update(self, road_center, other_npcs):

        self.position.y -= self.speed

        if self.lane_change:

            self.change_timer -= 1

            if self.change_timer <= 0:

                self.change_timer = random.randint(
                    180,
                    300
                )

                possible_targets = [
                    road_center - 180,
                    road_center,
                    road_center + 180
                ]

                random.shuffle(
                    possible_targets
                )

                for target in possible_targets:

                    blocked = False

                    for other in other_npcs:

                        if other is self:
                            continue

                        if (
                            abs(
                                other.position.x -
                                target
                            ) < 55
                            and
                            abs(
                                other.position.y -
                                self.position.y
                            ) < 110
                        ):

                            blocked = True
                            break

                    if not blocked:

                        self.target_x = target
                        break

            difference = (
                self.target_x -
                self.position.x
            )

            if abs(difference) > 2:

                direction = (
                    1
                    if difference > 0
                    else -1
                )

                self.position.x += (
                    direction *
                    min(
                        abs(difference),
                        3.5
                    )
                )

                self.lean += (
                    direction * 10 -
                    self.lean
                ) * 0.15

            else:

                self.lean *= 0.85

        else:

            target_x = self.target_x

            difference = (
                target_x -
                self.position.x
            )

            self.position.x += (
                difference *
                0.02
            )

            self.lean *= 0.85

    def draw(
        self,
        screen,
        screen_position
    ):

        car = pygame.Surface(
            (
                36,
                68
            ),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            car,
            (25, 25, 25),
            (
                3,
                2,
                30,
                64
            ),
            border_radius=9
        )

        pygame.draw.rect(
            car,
            self.color,
            (
                5,
                4,
                26,
                60
            ),
            border_radius=7
        )

        pygame.draw.polygon(
            car,
            (245, 245, 245),
            [
                (18, 5),
                (9, 16),
                (27, 16)
            ]
        )

        pygame.draw.polygon(
            car,
            (55, 90, 140),
            [
                (9, 19),
                (27, 19),
                (25, 32),
                (11, 32)
            ]
        )

        pygame.draw.rect(
            car,
            (30, 50, 80),
            (
                11,
                35,
                14,
                13
            ),
            border_radius=3
        )

        pygame.draw.rect(
            car,
            (255, 220, 120),
            (
                8,
                6,
                5,
                7
            ),
            border_radius=2
        )

        pygame.draw.rect(
            car,
            (255, 220, 120),
            (
                23,
                6,
                5,
                7
            ),
            border_radius=2
        )

        pygame.draw.rect(
            car,
            (15, 15, 15),
            (
                0,
                17,
                6,
                14
            ),
            border_radius=2
        )

        pygame.draw.rect(
            car,
            (15, 15, 15),
            (
                30,
                17,
                6,
                14
            ),
            border_radius=2
        )

        pygame.draw.rect(
            car,
            (15, 15, 15),
            (
                0,
                45,
                6,
                14
            ),
            border_radius=2
        )

        pygame.draw.rect(
            car,
            (15, 15, 15),
            (
                30,
                45,
                6,
                14
            ),
            border_radius=2
        )

        rotated = pygame.transform.rotate(
            car,
            -self.lean
        )

        rect = rotated.get_rect(
            center=(
                int(screen_position.x),
                int(screen_position.y)
            )
        )

        screen.blit(
            rotated,
            rect
        )
