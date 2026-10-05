import pygame

SIZES = {
    "car": (36, 68),
    "van": (40, 84),
    "truck": (46, 124),
    "bus": (46, 136),
    "bike": (20, 46),
}

_cache = {}

DARK = (25, 25, 25)
TIRE = (15, 15, 15)
GLASS = (55, 90, 140)
LIGHT = (255, 220, 120)


def _lighten(color, amount=0.35):

    return tuple(int(c + (255 - c) * amount) for c in color)


def _wheels(s, w, ys):

    for y in ys:
        pygame.draw.rect(s, TIRE, (0, y, 6, 14), border_radius=2)
        pygame.draw.rect(s, TIRE, (w - 6, y, 6, 14), border_radius=2)


def _headlights(s, w):

    pygame.draw.rect(s, LIGHT, (8, 6, 5, 7), border_radius=2)
    pygame.draw.rect(s, LIGHT, (w - 13, 6, 5, 7), border_radius=2)


def _car(w, h, color):

    s = pygame.Surface((w, h), pygame.SRCALPHA)

    pygame.draw.rect(s, DARK, (3, 2, 30, 64), border_radius=9)
    pygame.draw.rect(s, color, (5, 4, 26, 60), border_radius=7)
    pygame.draw.polygon(s, (245, 245, 245), [(18, 5), (9, 16), (27, 16)])
    pygame.draw.polygon(s, GLASS, [(9, 19), (27, 19), (25, 32), (11, 32)])
    pygame.draw.rect(s, (30, 50, 80), (11, 35, 14, 13), border_radius=3)

    _headlights(s, w)
    _wheels(s, w, [17, 45])

    return s


def _van(w, h, color):

    s = pygame.Surface((w, h), pygame.SRCALPHA)

    _wheels(s, w, [14, h - 34])

    pygame.draw.rect(s, DARK, (3, 2, w - 6, h - 4), border_radius=9)
    pygame.draw.rect(s, color, (5, 4, w - 10, h - 8), border_radius=7)
    pygame.draw.polygon(s, GLASS, [(9, 12), (w - 9, 12), (w - 11, 28), (11, 28)])
    pygame.draw.rect(s, _lighten(color), (9, 34, w - 18, h - 48), border_radius=4)

    _headlights(s, w)

    return s


def _truck(w, h, color):

    s = pygame.Surface((w, h), pygame.SRCALPHA)

    _wheels(s, w, [10, h - 48, h - 30])

    pygame.draw.rect(s, (60, 60, 60), (3, 38, w - 6, h - 40), border_radius=5)
    pygame.draw.rect(s, (228, 228, 228), (5, 40, w - 10, h - 44), border_radius=4)

    for y in range(52, h - 6, 14):
        pygame.draw.line(s, (190, 190, 190), (7, y), (w - 8, y), 2)

    pygame.draw.rect(s, DARK, (3, 2, w - 6, 40), border_radius=9)
    pygame.draw.rect(s, color, (5, 4, w - 10, 36), border_radius=7)
    pygame.draw.polygon(s, GLASS, [(10, 10), (w - 10, 10), (w - 12, 24), (12, 24)])

    _headlights(s, w)

    return s


def _bus(w, h, color):

    s = pygame.Surface((w, h), pygame.SRCALPHA)

    _wheels(s, w, [16, h - 50, h - 32])

    pygame.draw.rect(s, DARK, (3, 2, w - 6, h - 4), border_radius=10)
    pygame.draw.rect(s, color, (5, 4, w - 10, h - 8), border_radius=8)

    pygame.draw.rect(s, _lighten(color, 0.5), (9, 30, w - 18, h - 44), border_radius=5)

    for y in range(42, h - 16, 14):
        pygame.draw.line(s, _lighten(color, 0.2), (10, y), (w - 11, y), 2)

    pygame.draw.polygon(s, GLASS, [(9, 8), (w - 9, 8), (w - 11, 24), (11, 24)])

    _headlights(s, w)

    return s


def _bike(w, h, color):

    s = pygame.Surface((w, h), pygame.SRCALPHA)

    cx = w // 2

    pygame.draw.rect(s, TIRE, (cx - 2, 1, 4, 12), border_radius=2)
    pygame.draw.rect(s, TIRE, (cx - 2, h - 14, 4, 13), border_radius=2)

    pygame.draw.ellipse(s, color, (cx - 4, 10, 8, 26))
    pygame.draw.ellipse(s, (40, 40, 50), (cx - 7, 14, 14, 14))
    pygame.draw.line(s, TIRE, (1, 12), (w - 2, 12), 3)
    pygame.draw.circle(s, color, (cx, 24), 5)
    pygame.draw.rect(s, LIGHT, (cx - 2, 0, 4, 3))

    return s


_BUILDERS = {
    "car": _car,
    "van": _van,
    "truck": _truck,
    "bus": _bus,
    "bike": _bike,
}


def get_vehicle_surface(kind, color):

    key = (kind, color)

    if key not in _cache:

        w, h = SIZES[kind]

        _cache[key] = _BUILDERS[kind](w, h, color)

    return _cache[key]


def get_car_surface(color):

    return get_vehicle_surface("car", color)
