import random
import pygame

from src.car_sprite import get_vehicle_surface

LANES = (-180, 0, 180)


class NPC:

    # width/height must match src/car_sprite.py SIZES
    KINDS = {
        "car":   {"w": 36, "h": 68,  "speed": (6, 10), "weight": 50},
        "van":   {"w": 40, "h": 84,  "speed": (5, 9),  "weight": 18},
        "truck": {"w": 46, "h": 124, "speed": (4, 7),  "weight": 14},
        "bus":   {"w": 46, "h": 136, "speed": (5, 8),  "weight": 10},
        "bike":  {"w": 20, "h": 46,  "speed": (7, 11), "weight": 8},
    }

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

    # Turn indicator colors
    AMBER_ON = (255, 180, 0)
    AMBER_OFF = (80, 60, 0)

    @staticmethod
    def random_kind():

        kinds = list(NPC.KINDS)
        weights = [NPC.KINDS[k]["weight"] for k in kinds]

        return random.choices(kinds, weights)[0]

    def __init__(self, road_center, y, lane_offset=0, lane_change=False, speed_scale=1.0, kind=None):

        self.respawn(road_center, y, lane_offset, lane_change, speed_scale, kind)

    def respawn(self, road_center, y, lane_offset, lane_change, speed_scale=1.0, kind=None):
        """(Re)place this vehicle on the road. Also used for the first spawn."""

        self.kind = kind or NPC.random_kind()

        spec = NPC.KINDS[self.kind]

        self.width = spec["w"]
        self.height = spec["h"]

        self.position = pygame.Vector2(road_center + lane_offset, y)

        # lane is stored relative to the road, so vehicles follow the curves
        self.lane_offset = lane_offset
        self.lane_change = lane_change

        low, high = spec["speed"]

        self.base_speed = random.uniform(low, high) * speed_scale
        self.speed = self.base_speed

        self.color = random.choice(self.COLORS)

        self.change_timer = random.randint(180, 300)

        self.lean = 0

        # used by the near-miss bonus in main.py
        self.passed = False

        # ---- Turn signal tracking variables
        self.target_lane_offset = lane_offset
        self.indicator_side = None  # None, "LEFT", or "RIGHT"
        self.blink_timer = 0
        self.blink_visible = False

    def _lane_clear(self, target_x, others):
        """True if nothing is in the way while sliding over to target_x."""

        low = min(self.position.x, target_x)
        high = max(self.position.x, target_x)

        for other in others:

            if other is self:
                continue

            reach = (self.width + other.width) / 2 + 8

            # same lane as me: the following logic handles that one
            if abs(other.position.x - self.position.x) < reach:
                continue

            if (
                low - reach < other.position.x < high + reach
                and abs(other.position.y - self.position.y)
                < (self.height + other.height) / 2 + 120
            ):
                return False

        return True

    def update(self, road_center, other_npcs):

        # ---- keep a safe distance from whatever is ahead in my lane
        target_speed = self.base_speed
        blocked_ahead = False

        for other in other_npcs:

            if other is self:
                continue

            lateral = abs(other.position.x - self.position.x)

            if lateral >= (self.width + other.width) / 2 + 8:
                continue

            distance = self.position.y - other.position.y

            if distance <= 0:
                continue

            gap = distance - (self.height + other.height) / 2

            if gap < 90:

                target_speed = min(target_speed, other.speed * 0.85)
                blocked_ahead = True

            elif gap < 180:

                target_speed = min(target_speed, other.speed)
                blocked_ahead = True

        if target_speed < self.speed:
            self.speed = max(target_speed, self.speed - 0.3)
        else:
            self.speed = min(target_speed, self.speed + 0.05)

        self.position.y -= self.speed

        # ---- lane changes (only into a lane that is really free)
        if self.lane_change:

            if blocked_ahead:
                self.change_timer = min(self.change_timer, 1)

            self.change_timer -= 1

            if self.change_timer <= 0:

                self.change_timer = random.randint(180, 300)

                options = [lane for lane in LANES if lane != self.lane_offset]
                random.shuffle(options)

                changed = False

                for lane in options:

                    if self._lane_clear(road_center + lane, other_npcs):

                        self.target_lane_offset = lane
                        self.lane_offset = lane

                        # Determine blinker side based on chosen target lane
                        if lane > self.position.x - road_center:
                            self.indicator_side = "RIGHT"
                        else:
                            self.indicator_side = "LEFT"

                        changed = True
                        break

                if not changed and blocked_ahead:
                    self.change_timer = 20      # try again very soon

        # ---- steer towards my lane, which is always measured from the road centre
        desired_x = road_center + self.lane_offset

        difference = desired_x - self.position.x

        if self.lane_change:

            if abs(difference) > 2:

                direction = 1 if difference > 0 else -1

                self.position.x += direction * min(abs(difference), 3.5)

                self.lean += (direction * 10 - self.lean) * 0.15

            else:

                self.lean *= 0.85

                # Disable indicator once vehicle successfully centers in new lane
                self.indicator_side = None

        else:

            self.position.x += difference * 0.05

            self.lean *= 0.85

        # ---- update indicator flashing state
        if self.indicator_side:
            self.blink_timer += 1
            if self.blink_timer >= 15:  # Toggle every 15 frames (~0.25 seconds)
                self.blink_visible = not self.blink_visible
                self.blink_timer = 0
        else:
            self.blink_visible = False
            self.blink_timer = 0

    def draw(self, screen, screen_position):

        sprite = get_vehicle_surface(self.kind, self.color)

        # 1. Draw turn signals onto unrotated sprite surface
        if self.indicator_side is not None:

            # Create a editable copy of the vehicle sprite frame
            sprite = sprite.copy()

            # Front & Rear indicator bulb positions based on vehicle size
            left_x = 4
            right_x = self.width - 4
            front_y = 6
            rear_y = self.height - 6

            signal_radius = 2

            left_color = self.AMBER_ON if (self.indicator_side == "LEFT" and self.blink_visible) else self.AMBER_OFF
            right_color = self.AMBER_ON if (self.indicator_side == "RIGHT" and self.blink_visible) else self.AMBER_OFF

            # Front-left and Rear-left bulbs
            pygame.draw.circle(sprite, left_color, (left_x, front_y), signal_radius)
            pygame.draw.circle(sprite, left_color, (left_x, rear_y), signal_radius)

            # Front-right and Rear-right bulbs
            pygame.draw.circle(sprite, right_color, (right_x, front_y), signal_radius)
            pygame.draw.circle(sprite, right_color, (right_x, rear_y), signal_radius)

        # 2. Rotate sprite and blit to screen (Preserves lean mechanics)
        rotated = pygame.transform.rotate(sprite, -self.lean)

        rect = rotated.get_rect(center=(round(screen_position.x), round(screen_position.y))        )

        screen.blit(rotated, rect)
