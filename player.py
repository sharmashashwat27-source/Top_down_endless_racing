import random

import pygame

from src.car_sprite import get_car_surface


class Player:

    BODY_COLOR = (210, 40, 40)

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

        # --- nitro ---
        self.max_nitro = 100.0
        self.nitro = 100.0
        self.nitro_drain = 0.6
        self.nitro_regen = 0.15
        self.nitro_unlock_level = 25.0
        self.nitro_locked = False
        self.boosting = False
        self.boost_acceleration = 0.45
        self.boost_max_speed = 30

        # --- crash recovery ---
        self.invincible = 0

    def hit(self):
        """Called by the game when the player crashes into traffic."""

        self.velocity *= 0.4
        self.invincible = 120

    def update(self):

        keys = pygame.key.get_pressed()

        forward = pygame.Vector2(0, -1)

        forward_speed = self.velocity.dot(forward)

        if keys[pygame.K_w] or keys[pygame.K_UP]:

            self.velocity += forward * self.acceleration

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:

            if forward_speed > 0.5:

                self.velocity -= forward * self.brake_force

            else:

                self.velocity -= forward * self.reverse_acceleration

        # ---- nitro ----
        wants_boost = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        if self.nitro_locked and self.nitro >= self.nitro_unlock_level:
            self.nitro_locked = False

        self.boosting = (
            wants_boost
            and not self.nitro_locked
            and self.nitro > 0
        )

        if self.boosting:

            self.velocity += forward * self.boost_acceleration
            self.nitro = max(0, self.nitro - self.nitro_drain)

            if self.nitro <= 0:
                self.nitro_locked = True

        else:

            self.nitro = min(self.max_nitro, self.nitro + self.nitro_regen)

        forward_speed = self.velocity.dot(forward)

        cap = self.boost_max_speed if self.boosting else self.max_speed

        if forward_speed > cap:

            # ease back down instead of snapping when nitro ends
            excess = forward_speed - cap
            ease = 1.0 if self.boosting else 0.08

            self.velocity -= forward * (excess * ease)

        if forward_speed < -self.max_reverse_speed:

            self.velocity -= forward * (forward_speed + self.max_reverse_speed)

        steering = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:

            steering = -1

        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:

            steering = 1

        if steering != 0:

            self.position.x += steering * self.lane_speed

        target_lean = steering * self.max_lean

        self.visual_angle += (target_lean - self.visual_angle) * self.lean_speed

        self.velocity.y *= self.drag

        self.position.y += self.velocity.y

        if abs(self.velocity.y) < 0.01:

            self.velocity.y = 0

        if self.invincible > 0:

            self.invincible -= 1

    def draw(self, screen, screen_position):

        x = int(screen_position.x)
        y = int(screen_position.y)

        if self.boosting:

            length = random.randint(18, 34)

            pygame.draw.polygon(
                screen,
                (255, 120, 30),
                [(x - 9, y + 32), (x + 9, y + 32), (x, y + 32 + length)]
            )

            pygame.draw.polygon(
                screen,
                (255, 230, 120),
                [(x - 4, y + 32), (x + 4, y + 32), (x, y + 32 + length // 2)]
            )

        # blink while invincible
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return

        car = get_car_surface(self.BODY_COLOR)

        rotated = pygame.transform.rotate(car, -self.visual_angle)

        rect = rotated.get_rect(center=(x, y))

        screen.blit(rotated, rect)
