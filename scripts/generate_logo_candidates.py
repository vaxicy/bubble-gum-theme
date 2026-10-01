# -*- coding: utf-8 -*-
"""Bubble Gum Theme - logo candidate generator.

All marks are drawn in code with Pillow. No stock art, no AI.

Run from the project root:  python3 scripts/generate_logo_candidates.py
Writes 512px transparent masters + a contact sheet to store-assets/logo-candidates/.

Art direction
- Eight genuinely different visual languages, not one silhouette with swapped
  parts: a gum sphere, a gumball machine, a wrapped candy, an overlapping bubble
  cluster, a pop burst, a gum drop, a rolled gum spiral and a bitten gumball.
- No letters, initials or monograms anywhere.
- Everything is a transparent master: no outer frame, no rounded container.
"""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

S = 256          # logical canvas
SS = 4           # supersampling factor (draw at 1024, downscale to 512)
W = S * SS
OUT_DIR = os.path.join("store-assets", "logo-candidates")

LIGHT_BG = "#FEF6FD"     # Bubble Gum Theme Light editor canvas
DARK_BG = "#32112E"      # Bubble Gum Theme Dark editor canvas
NAME_COL_W = 214
CELL_W = 232
ROW_H = 228
HEAD_H = 62

PALETTES = {
    "light": {
        "deep": "#6E1165",
        "main": "#951E88",
        "mid": "#BE4995",
        "bright": "#E85CD8",
        "glint": "#FFFFFF",
        "bg": LIGHT_BG,
    },
    "dark": {
        "deep": "#B837AC",
        "main": "#DB4BCB",
        "mid": "#F07AE3",
        "bright": "#FF9EF2",
        "glint": "#FFFFFF",
        "bg": DARK_BG,
    },
}

CLEAR = (0, 0, 0, 0)


# ------------------------------------------------------------------ helpers
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def layer():
    return Image.new("RGBA", (W, W), CLEAR)


def blank():
    return Image.new("L", (W, W), 0)


def ell(cx, cy, r, ry=None):
    ry = r if ry is None else ry
    m = blank()
    ImageDraw.Draw(m).ellipse(
        [(cx - r) * SS, (cy - ry) * SS, (cx + r) * SS, (cy + ry) * SS], fill=255)
    return m


def rrect(x0, y0, x1, y1, r):
    m = blank()
    r = max(0.0, min(r, (x1 - x0) / 2 - 0.5, (y1 - y0) / 2 - 0.5))
    ImageDraw.Draw(m).rounded_rectangle(
        [x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS, fill=255)
    return m


def poly(pts):
    m = blank()
    ImageDraw.Draw(m).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return m


def ring(cx, cy, r, thickness):
    return ImageChops.subtract(ell(cx, cy, r), ell(cx, cy, r - thickness))


def star4(cx, cy, r, waist=0.24):
    pts = []
    for i in range(8):
        a = math.pi / 2 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * waist
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts)


def uni(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = ImageChops.lighter(out, m)
    return out


def sub(a, b):
    return ImageChops.subtract(a, b)


def inter(a, b):
    return ImageChops.darker(a, b)


def soften(mask, radius=2.5):
    return mask.filter(ImageFilter.GaussianBlur(radius))


def grad(c0, c1, angle=90.0):
    sw = sh = 96
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    ps = [x * dx + y * dy for x in (0, sw - 1) for y in (0, sh - 1)]
    lo, hi = min(ps), max(ps)
    im = Image.new("RGB", (sw, sh))
    px = im.load()
    r0, g0, b0 = rgb(c0)
    r1, g1, b1 = rgb(c1)
    for y in range(sh):
        for x in range(sw):
            t = ((x * dx + y * dy) - lo) / (hi - lo)
            px[x, y] = (round(r0 + (r1 - r0) * t),
                        round(g0 + (g1 - g0) * t),
                        round(b0 + (b1 - b0) * t))
    return im.resize((W, W), Image.BICUBIC)


def radial(c0, c1, cx=0.38, cy=0.30):
    """Radial ramp: c0 at (cx, cy), c1 at the far corner - gives a sphere look."""
    sw = sh = 128
    im = Image.new("RGB", (sw, sh))
    px = im.load()
    r0, g0, b0 = rgb(c0)
    r1, g1, b1 = rgb(c1)
    far = max(math.hypot(cx - x, cy - y)
              for x in (0.0, 1.0) for y in (0.0, 1.0))
    for y in range(sh):
        for x in range(sw):
            t = math.hypot(cx - x / (sw - 1), cy - y / (sh - 1)) / far
            t = min(1.0, t ** 0.9)
            px[x, y] = (round(r0 + (r1 - r0) * t),
                        round(g0 + (g1 - g0) * t),
                        round(b0 + (b1 - b0) * t))
    return im.resize((W, W), Image.BICUBIC)


def stamp(base, mask, color=None, gradient=None, radial_grad=None,
          angle=90.0, alpha=255):
    if radial_grad is not None:
        src = radial(radial_grad[0], radial_grad[1]).convert("RGBA")
    elif gradient is not None:
        src = grad(gradient[0], gradient[1], angle).convert("RGBA")
    else:
        src = Image.new("RGBA", (W, W), rgb(color) + (255,))
    if alpha < 255:
        src.putalpha(src.getchannel("A").point(lambda v: v * alpha // 255))
    return Image.alpha_composite(base, Image.composite(src, layer(), mask))


# ------------------------------------------------------------------ designs
def d_bubble(p):
    """01 - one glossy gum sphere with a specular highlight."""
    img = layer()
    ball = ell(128, 128, 88)
    img = stamp(img, ball, radial_grad=(p["bright"], p["deep"]))
    img = stamp(img, soften(ell(98, 94, 30, 22), 6), color=p["glint"], alpha=170)
    img = stamp(img, soften(ell(160, 176, 15), 4), color=p["glint"], alpha=95)
    return img


def d_machine(p):
    """02 - a gumball machine: glass globe, three gumballs, solid base."""
    img = layer()
    img = stamp(img, ring(128, 100, 56, 10), color=p["main"])
    img = stamp(img, ell(104, 116, 14), color=p["bright"])
    img = stamp(img, ell(150, 112, 14), color=p["mid"])
    img = stamp(img, ell(128, 86, 14), color=p["bright"])
    img = stamp(img, rrect(76, 150, 180, 166, 8), color=p["main"])
    img = stamp(img, poly([(82, 166), (174, 166), (160, 198), (96, 198)]), color=p["mid"])
    return stamp(img, rrect(96, 194, 160, 210, 8), color=p["deep"])


def d_wrap(p):
    """03 - a wrapped gum: soft body with two pinched twist fans."""
    img = layer()
    left = poly([(96, 128), (36, 86), (36, 170)])
    right = poly([(160, 128), (220, 86), (220, 170)])
    img = stamp(img, left, color=p["mid"])
    img = stamp(img, right, color=p["mid"])
    img = stamp(img, poly([(96, 128), (58, 100), (58, 156)]), color=p["deep"], alpha=110)
    img = stamp(img, poly([(160, 128), (198, 100), (198, 156)]), color=p["deep"], alpha=110)
    return stamp(img, rrect(88, 96, 168, 160, 26),
                 gradient=(p["bright"], p["main"]), angle=115)


def d_cluster(p):
    """04 - three overlapping bubbles in three tones (union / lenses / core)."""
    img = layer()
    a = ell(100, 106, 56)
    b = ell(156, 106, 56)
    c = ell(128, 158, 56)
    core = inter(a, inter(b, c))
    lenses = sub(uni(inter(a, b), inter(b, c), inter(a, c)), core)
    img = stamp(img, uni(a, b, c), color=p["main"])
    img = stamp(img, lenses, color=p["mid"])
    return stamp(img, core, color=p["bright"])


def d_burst(p):
    """05 - a bubble popping: solid core with eight separated drops."""
    img = layer()
    img = stamp(img, ell(128, 128, 32), radial_grad=(p["bright"], p["deep"]))
    dots = None
    for i in range(8):
        a = 2.0 * math.pi * i / 8 - math.pi / 8
        d = ell(128 + 74 * math.cos(a), 128 + 74 * math.sin(a), 15)
        dots = d if dots is None else uni(dots, d)
    return stamp(img, dots, color=p["mid"])


def d_drop(p):
    """06 - a gum drop: teardrop with a crisp glint and an inner shadow."""
    img = layer()
    cx, cy, r, apex = 128, 148, 66, 26
    d = cy - apex
    phi = math.acos(r / d)
    tx, ty = r * math.sin(phi), cy - r * math.cos(phi)
    body = uni(ell(cx, cy, r), poly([(cx, apex), (cx - tx, ty), (cx + tx, ty)]))
    img = stamp(img, body, gradient=(p["bright"], p["deep"]), angle=105)
    img = stamp(img, sub(body, ell(cx - 22, cy + 4, r - 8)), color=p["deep"], alpha=70)
    img = stamp(img, soften(ell(110, 122, 13), 3), color=p["glint"], alpha=215)
    return stamp(img, soften(ell(116, 156, 7), 2), color=p["glint"], alpha=140)


def d_spiral(p):
    """07 - a rolled gum tape: an Archimedean spiral band."""
    img = layer()
    cx, cy, turns, band = 128, 130, 2.05, 24
    r0, r1 = 20.0, 92.0
    steps = 220
    outer, inner = [], []
    for i in range(steps + 1):
        t = i / steps
        a = -math.pi / 2 + t * turns * 2.0 * math.pi
        r = r0 + t * (r1 - r0)
        outer.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        inner.append((cx + (r - band) * math.cos(a), cy + (r - band) * math.sin(a)))
    band_mask = poly(outer + inner[::-1])
    return stamp(img, band_mask, gradient=(p["mid"], p["deep"]), angle=120)


def d_bite(p):
    """08 - a gumball with two scallopped bite marks."""
    img = layer()
    body = ell(126, 136, 86)
    body = sub(body, ell(206, 60, 44))
    body = sub(body, ell(172, 34, 26))
    img = stamp(img, body, radial_grad=(p["bright"], p["deep"]))
    img = stamp(img, soften(ell(94, 108, 24, 17), 5), color=p["glint"], alpha=150)
    return img


DESIGNS = [
    ("01-bubble", d_bubble),
    ("02-machine", d_machine),
    ("03-wrap", d_wrap),
    ("04-cluster", d_cluster),
    ("05-burst", d_burst),
    ("06-drop", d_drop),
    ("07-spiral", d_spiral),
    ("08-bite", d_bite),
]


# ------------------------------------------------------------------ output
def save_master(img, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    img.resize((512, 512), Image.LANCZOS).save(os.path.join(OUT_DIR, name + ".png"))


def font(size, bold=False):
    path = r"C:\Windows\Fonts\%s.ttf" % ("segoeuib" if bold else "segoeui")
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def checker(size, cell=14):
    """Transparency checkerboard - proves the mark really has no background."""
    im = Image.new("RGB", (size, size), "#FFFFFF")
    d = ImageDraw.Draw(im)
    for y in range(0, size, cell):
        for x in range(0, size, cell):
            if (x // cell + y // cell) % 2:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill="#E2E2EA")
    return im


def contact_sheet(rendered):
    cols = [
        ("LIGHT UI", "light", LIGHT_BG, "flat", "512 px master, shown at 180"),
        ("DARK UI", "dark", DARK_BG, "flat", "512 px master, shown at 180"),
        ("TRANSPARENT", None, None, "checker", "no background, shown at 180"),
        ("LIGHT UI SMALL", "light", LIGHT_BG, "small", "96 / 64 / 32 px"),
        ("DARK UI SMALL", "dark", DARK_BG, "small", "96 / 64 / 32 px"),
    ]
    width = NAME_COL_W + CELL_W * len(cols)
    sheet = Image.new("RGB", (width, HEAD_H + ROW_H * len(DESIGNS)), "#FFFFFF")
    d = ImageDraw.Draw(sheet)
    f_head, f_name, f_sub = font(16, True), font(19, True), font(12)
    for i, (title, _, _, _, note) in enumerate(cols):
        d.text((NAME_COL_W + i * CELL_W + 16, 14), title, font=f_head, fill="#333333")
        d.text((NAME_COL_W + i * CELL_W + 16, 36), note, font=f_sub, fill="#9A9AA4")
    for r, (slug, _) in enumerate(DESIGNS):
        y = HEAD_H + r * ROW_H
        d.line([(0, y), (width, y)], fill="#E4E4E4")
        d.text((16, y + 100), slug, font=f_name, fill="#1B1B1F")
        d.text((16, y + 126), "transparent master", font=f_sub, fill="#7A7A7A")
        for c, (_, variant, bg, mode, _) in enumerate(cols):
            x = NAME_COL_W + c * CELL_W
            if mode != "checker":
                d.rounded_rectangle([x + 10, y + 12, x + CELL_W - 10, y + ROW_H - 12],
                                    radius=12, fill=bg)
            cx, cy = x + CELL_W // 2, y + ROW_H // 2
            if mode == "flat":
                big = 180
                src = rendered[(slug, variant)]
                im = src.resize((big, big), Image.LANCZOS)
                sheet.paste(im, (cx - big // 2, cy - big // 2), im)
            elif mode == "checker":
                big = 180
                sheet.paste(checker(big), (cx - big // 2, cy - big // 2))
                src = rendered[(slug, "light")]
                im = src.resize((big, big), Image.LANCZOS)
                sheet.paste(im, (cx - big // 2, cy - big // 2), im)
                d.rectangle([cx - big // 2, cy - big // 2,
                             cx + big // 2 - 1, cy + big // 2 - 1], outline="#CFCFD8")
            else:
                src = rendered[(slug, variant)]
                sizes = (96, 64, 32)
                left = cx - 106
                for size in sizes:
                    im = src.resize((size, size), Image.LANCZOS)
                    sheet.paste(im, (left, cy - size // 2 - 6), im)
                    d.text((left, cy + 60), str(size), font=f_sub, fill="#8C8C8C"
                           if variant == "light" else "#C9A8C4")
                    left += size + 10
    out = os.path.join(OUT_DIR, "contact-sheet.png")
    sheet.save(out)
    return out


def main():
    rendered = {}
    for slug, fn in DESIGNS:
        for variant, pal in PALETTES.items():
            img = fn(pal)
            save_master(img, "%s-%s" % (slug, variant))
            rendered[(slug, variant)] = img.resize((S, S), Image.LANCZOS)
        print("done:", slug)
    print("sheet:", contact_sheet(rendered))
    print("masters:", OUT_DIR)


if __name__ == "__main__":
    main()
