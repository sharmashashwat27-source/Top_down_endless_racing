import math
import random

import pygame


class Coin:

    FILL = (255, 150, 30)      # orange
    EDGE = (190, 90, 10)
    SHINE = (255, 205, 110)

    def __init__(self, x, y):

        self.position = pygame.Vector2(x, y)
        self.phase = random.uniform(0, math.tau)

    def draw(self, screen, screen_position, time):

        # squash the width over time so the coin looks like it is spinning
        half_width = max(3, int(abs(math.cos(time * 0.08 + self.phase)) * 10))

        rect = pygame.Rect(0, 0, half_width * 2, 22)
        rect.center = (int(screen_position.x), int(screen_position.y))

        pygame.draw.ellipse(screen, self.FILL, rect)

        if half_width > 6:
            pygame.draw.ellipse(screen, self.SHINE, rect.inflate(-8, -10))

        pygame.draw.ellipse(screen, self.EDGE, rect, 2)


class Gem:

    VALUE = 200

    COLORS = [
        ((60, 220, 255), (20, 120, 170)),     # cyan
        ((255, 90, 210), (160, 30, 120)),     # pink
        ((100, 255, 130), (30, 150, 60)),     # green
    ]

    def __init__(self, x, y):

        self.position = pygame.Vector2(x, y)
        self.fill, self.edge = random.choice(self.COLORS)
        self.phase = random.uniform(0, math.tau)

    def draw(self, screen, screen_position, time):

        pulse = 1 + 0.12 * math.sin(time * 0.1 + self.phase)

        r = int(15 * pulse)

        cx = int(screen_position.x)
        cy = int(screen_position.y)

        wide = int(r * 0.8)

        points = [(cx, cy - r), (cx + wide, cy), (cx, cy + r), (cx - wide, cy)]

        pygame.draw.polygon(screen, self.fill, points)

        # lighter facet
        light = tuple(min(255, c + 90) for c in self.fill)

        pygame.draw.polygon(
            screen,
            light,
            [(cx, cy - r), (cx + wide, cy), (cx, cy)]
        )

        pygame.draw.polygon(screen, self.edge, points, 2)

        # sparkle
        if math.sin(time * 0.1 + self.phase) > 0.6:

            pygame.draw.line(screen, (255, 255, 255), (cx + 8, cy - r), (cx + 8, cy - r + 8), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx + 4, cy - r + 4), (cx + 12, cy - r + 4), 2)
