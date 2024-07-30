from typing import Tuple

white = (0xFF, 0xFF, 0xFF)
black = (0x0, 0x0, 0x0)
red = (0xFF, 0x0, 0x0)

player_atk = (0xE0, 0xE0, 0xE0)
enemy_atk = (0xFF, 0xC0, 0xC0)
needs_target = (0x3F, 0xFF, 0xFF)
status_effect_applied = (0x3F, 0xFF, 0x3F)
descend = (0x9F, 0x3F, 0xFF)

player_die = (0xFF, 0x30, 0x30)
enemy_die = (0xFF, 0xA0, 0x30)

invalid = (0xFF, 0xFF, 0x00)
impossible = (0x80, 0x80, 0x80)
error = (0xFF, 0x40, 0x40)

welcome_text = (0x20, 0xA0, 0xFF)
health_recovered = (0x0, 0xFF, 0x0)

bar_text = white
bar_filled = (0x0, 0x60, 0x0)
bar_empty = (0x40, 0x10, 0x10)

menu_title = (255, 255, 63)
menu_text = white


def lit(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    r, g, b = rgb
    r = int((255 + 2*r) / 3)
    g = int((240 + 2*g) / 3)
    b = int((2 * b) / 3)

    return r, g, b


def invisible(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    h, s, v = rgb_to_hsv(rgb)
    if h > 180:
        h -= 360
    h /= 12
    h += 45
    s /= 2
    v = (v + .5) / 2
    return hsv_to_rgb((h, s, v))


def rgb_to_hsv(
        rgb: Tuple[int, int, int]
) -> Tuple[float, float, float]:
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    c_max, c_min = max(r, g, b), min(r, g, b)
    diff = c_max - c_min

    if diff == 0:
        h = 0.0
    elif c_max == r:
        h = (60.0 * ((g - b) / diff) + 360.0) % 360.0
    elif c_max == g:
        h = (60.0 * ((b - r) / diff) + 120.0) % 360.0
    else:
        h = (60.0 * ((r - g) / diff) + 240.0) % 360.0

    if c_max == 0:
        s = 0
    else:
        s = diff / c_max

    v = c_max

    return h, s, v


def hsv_to_rgb(
        hsv: Tuple[float, float, float]
) -> Tuple[int, int, int]:
    def _clamp(f: float) -> int:
        f *= 255.0
        if f < 0.0:
            return 0
        elif f > 255.0:
            return 255
        else:
            return int(f)

    h, s, v = hsv
    r = _clamp(v)
    if s == 0:
        return r, r, r

    h = (h % 360.0) / 60.0
    region = int(h)
    fract = h - region

    p = _clamp(v * (1.0 - s))
    q = _clamp(v * (1.0 - s * fract))
    t = _clamp(v * (1.0 - s * (1.0 - fract)))

    if region == 0:
        return r, t, p
    elif region == 1:
        return q, r, p
    elif region == 2:
        return p, r, t
    elif region == 3:
        return p, q, r
    elif region == 4:
        return t, p, r
    else:
        return r, p, q
