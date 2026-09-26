import pygame


class Player:

    def __init__(self):

        self.position = pygame.Vector2(0, 400)
        self.velocity = pygame.Vector2(0, 0)

        self.angle = 0.0
        self.visual_angle = 0.0

        self.width = 36
        self.height = 68

        self.acceleration = 0.20
        self.reverse_acceleration = 0.12
        self.brake_force = 0.30

        self.max_speed = 20
        self.max_reverse_speed = 7

        self.lane_speed = 4.5
        self.max_lean = 12
        self.lean_speed = 0.25

        self.drag = 0.985


    def update(self):

        keys = pygame.key.get_pressed()

        forward = pygame.Vector2(0, -1)

        forward_speed = self.velocity.dot(forward)

        if keys[pygame.K_w] or keys[pygame.K_UP]:

            self.velocity += (
                forward *
                self.acceleration
            )

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:

            if forward_speed > 0.5:

                self.velocity -= (
                    forward *
                    self.brake_force
                )

            else:

                self.velocity -= (
                    forward *
                    self.reverse_acceleration
                )

        forward_speed = self.velocity.dot(forward)

        if forward_speed > self.max_speed:

            self.velocity -= (
                forward *
                (
                    forward_speed -
                    self.max_speed
                )
            )

        if forward_speed < -self.max_reverse_speed:

            self.velocity -= (
                forward *
                (
                    forward_speed +
                    self.max_reverse_speed
                )
            )

        steering = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:

            steering = -1

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:

            steering = 1

        if steering != 0:

            self.position.x += (
                steering *
                self.lane_speed
            )

        target_lean = (
            steering *
            self.max_lean
        )

        self.visual_angle += (
            target_lean -
            self.visual_angle
        ) * self.lean_speed

        self.velocity.y *= self.drag

        self.position.y += self.velocity.y

        if abs(self.velocity.y) < 0.01:

            self.velocity.y = 0


    def draw(
        self,
        screen,
        screen_position
    ):

        car_width = 36
        car_height = 68

        car = pygame.Surface(
            (
                car_width,
                car_height
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
            (210, 40, 40),
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
            -self.visual_angle
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
