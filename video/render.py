# -*- coding: utf-8 -*-
"""Render the r/Piracy GTA VI decomp' video (v2).

PIL scene groups -> numpy compositor -> raw RGB pipe -> ffmpeg (libx264).
Narration clips are concatenated and mixed with a generated lo-fi bed.

usage:  python render.py 16x9|9x16
        python render.py 16x9 --preview BEAT:SCENE out.png
"""
import sys, os, math, json, random, subprocess, itertools, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import content
from content import BEATS, CAPTIONS, SOURCES

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

FONT_DIR = "assets/fonts"
FORMATS = {
    "16x9": dict(W=1920, H=1080, fps=30, out="exports/gtavi_piracy_recap_16x9.mp4"),
    "9x16": dict(W=1080, H=1920, fps=30, out="exports/gtavi_piracy_recap_9x16.mp4"),
}

# ---------------------------------------------------------------- colours ---
BG_TOP   = (20, 19, 25)
BG_BOT   = (9, 9, 13)
PANEL    = (25, 25, 32)
PANEL_L  = (38, 38, 49)
LINE     = (54, 54, 70)
TXT      = (240, 237, 231)
MUTED    = (163, 158, 150)
DIM      = (110, 106, 102)
ORANGE   = (255, 69, 0)
TEAL     = (64, 208, 200)
PINK     = (255, 88, 176)
UPVOTE   = (255, 69, 0)
DOWN     = (140, 143, 175)
USERCLR  = (170, 180, 255)
ACCENTS  = {"orange": ORANGE, "teal": TEAL, "pink": PINK}

# ------------------------------------------------------------------ fonts ---
_fc = {}
def F(name, size):
    key = (name, max(6, int(size)))
    if key not in _fc:
        _fc[key] = ImageFont.truetype(os.path.join(FONT_DIR, name), key[1])
    return _fc[key]

def inter(w, s):   return F("inter-latin-%d-normal.ttf" % w, s)
def anton(s):      return F("anton-latin-400-normal.ttf", s)
def monof(s, b=False):  return F("space-mono-latin-%d-normal.ttf" % (700 if b else 400), s)


class L:
    portrait = False
    W = H = 0
    s = 1.0
    M = pad = 0
    fs = {}
    rad = 24
    avatar = 56
    content_top = content_bot = 0

    @classmethod
    def init(cls, W, H):
        cls.W, cls.H = W, H
        cls.portrait = H > W
        s = (H / 1920.0) if cls.portrait else (W / 1920.0)
        cls.s = s
        cls.M = int(W * (0.060 if cls.portrait else 0.055))
        cls.pad = int(W * (0.058 if cls.portrait else 0.030))
        base = dict(kicker=25, sub=37, top=26, user=30, meta=25, body=40,
                    score=29, cta=25, cap=41, label=25, small=24)
        cls.fs = {k: max(11, int(v * s)) for k, v in base.items()}
        cls.rad = int(20 * s)
        cls.avatar = int(50 * s)
        cls.content_top = int(H * (0.215 if cls.portrait else 0.215))
        cls.content_bot = int(H * (0.815 if cls.portrait else 0.795))


# ---------------------------------------------------------------- helpers ---
def ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3

def ease_inout(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def cl(x):
    return max(0.0, min(1.0, x))


def tlayer(txt, font, fill, tracking=0):
    """Text rendered on its own RGBA layer using true font metrics."""
    asc, desc = font.getmetrics()
    w = int(math.ceil(font.getlength(txt))) + 4
    im = Image.new("RGBA", (max(1, w), asc + desc + 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2, asc + 1), txt, font=font, fill=fill, anchor="ls")
    return im


def wrap(text, font, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if not cur or font.getlength(t) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_anton(text, maxw, hi, max_lines=1):
    size = int(hi)
    while size > 12:
        f = anton(size)
        if font_lines_fit(text, f, maxw, max_lines):
            return f
        size = int(size * 0.94)
    return anton(14)


def font_lines_fit(text, f, maxw, max_lines):
    ls = wrap(text, f, maxw)
    return len(ls) <= max_lines and all(f.getlength(l) <= maxw for l in ls)


def rrect(img, box, r, fill=None, outline=None, width=1):
    d = ImageDraw.Draw(img)
    r = max(0, min(int(r), (box[2] - box[0]) // 2, (box[3] - box[1]) // 2))
    d.rounded_rectangle([int(v) for v in box], radius=r, fill=fill, outline=outline, width=width)


# ------------------------------------------------------------------ assets ---
_bg = {}
_marks = {}

def _smooth_noise(w, h, seed):
    def one(cell, sd):
        rng = np.random.default_rng(sd)
        gw, gh = w // cell + 3, h // cell + 3
        a = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
        return np.asarray(im, dtype=np.float32) / 255.0
    return np.clip(one(300, seed) * 0.55 + one(110, seed + 1) * 0.3 + one(40, seed + 2) * 0.15, 0, 1)


def build_background(W, H):
    """Base gradient + soft glows + faint grid. Per-beat colour blobs are added live."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = xx / W, yy / H
    base = np.zeros((H, W, 3), np.float32)
    for i in range(3):
        base[..., i] = BG_TOP[i] * (1 - y) + BG_BOT[i] * y
    # broad top-right light, bottom-left counter light
    g1 = np.exp(-(((x - 0.80) ** 2) / 0.10 + ((y - 0.06) ** 2) / 0.09))
    g2 = np.exp(-(((x - 0.12) ** 2) / 0.14 + ((y - 0.95) ** 2) / 0.12))
    n = _smooth_noise(W, H, 7)
    for i in range(3):
        base[..., i] += g1 * (255 * 0.055) * (0.5 + 0.8 * n)
        base[..., i] += g2 * (30, 60, 62)[i] * 0.5 * (0.6 + 0.7 * (1 - n))
    # faint grid
    gm = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(gm)
    step = int(W * 0.031)
    for gx in range(0, W, step):
        gd.line([(gx, 0), (gx, H)], fill=(9, 9, 12))
    for gy in range(0, H, step):
        gd.line([(0, gy), (W, gy)], fill=(9, 9, 12))
    base += np.asarray(gm, dtype=np.float32)
    # vignette
    v = 1.0 - 0.30 * (((x - .5) ** 2) * 1.5 + ((y - .5) ** 2) * 1.7)
    base *= v[..., None]
    base += ((np.random.default_rng(3).random((H, W)).astype(np.float32) - .5) * 4)[..., None]
    _bg[(W, H)] = np.clip(base, 0, 255).astype(np.uint8)


def get_bg(W, H):
    if (W, H) not in _bg:
        build_background(W + 160, H)
        _bg[(W, H)] = _bg[(W + 160, H)]
    return _bg[(W, H)]


_blob = {}
GP = 220  # padding so blobs can drift without wrapping


def glow_blob(W, H, color):
    """Soft radial light, oversized so it can drift; returns float array."""
    key = (W, H, color)
    if key not in _blob:
        gw, gh = (W + 2 * GP) // 6, (H + 2 * GP) // 6
        yy, xx = np.mgrid[0:gh, 0:gw].astype(np.float32)
        u = np.arange(gw, dtype=np.float32) / (gw - 1)
        v = np.arange(gh, dtype=np.float32) / (gh - 1)
        d = ((u[None, :] - 0.5) ** 2 * 1.6 + (v[:, None] - 0.5) ** 2 * 2.0)
        al = np.clip(1 - np.maximum(d, 0) * 2.0, 0, 1) ** 2.0
        # feather to zero at the array edges so no hard border ever shows
        wx = np.clip(np.sin(np.pi * u), 0, 1) ** 0.75
        wy = np.clip(np.sin(np.pi * v), 0, 1) ** 0.75
        al = np.clip(al * wy[:, None] * wx[None, :], 0, 1).astype(np.float32)
        assert al.ndim == 2 and al.dtype == np.float32, (al.shape, al.dtype)
        im = Image.fromarray(np.ascontiguousarray((al * 255).astype(np.uint8))).resize((W + 2 * GP, H + 2 * GP), Image.BICUBIC)
        al = np.asarray(im, dtype=np.float32) / 255.0
        arr = np.zeros((H + 2 * GP, W + 2 * GP, 3), np.float32)
        for i in range(3):
            arr[..., i] = al * color[i]
        _blob[key] = arr
    return _blob[key]


def floating_marks(W, H, beat):
    key = (W, H, beat)
    if key in _marks:
        return _marks[key]
    hh = int(H * 1.6)
    layer = Image.new("RGB", (W, hh), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = monof(int(W * 0.0105) + 8)
    rng = random.Random(beat * 13 + 5)
    seq = ["0", "1", "ldr", "b.w", "mov", "ret", "str", "cmp", "nop", "0x4B",
           "{}", "//", "??", "$", "yarr", "AI", "ai", "!!"]
    for i in range(64):
        x = rng.randint(0, W - 10)
        y = rng.randint(0, hh - 20)
        txt = " ".join(rng.choice(seq) for _ in range(rng.randint(2, 5)))
        c = rng.randint(0, 3)
        col = (26, 26, 35) if c < 2 else ((33, 29, 38) if c == 2 else (28, 37, 39))
        d.text((x, y), txt, font=f, fill=col)
    _marks[key] = layer
    return layer


_grain = {}
def grain(gf, W, H):
    k = gf % 10
    key = (k, W, H)
    if key not in _grain:
        rng = np.random.default_rng(700 + k)
        a = (rng.random((H // 2, W // 2)).astype(np.float32) - 0.5) * 4.5
        im = Image.fromarray(np.clip(a + 128, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        _grain[key] = np.asarray(im, dtype=np.float32) - 128.0
    return _grain[key]


_ovl = {}
def overlay(W, H):
    key = (W, H)
    if key in _ovl:
        a = _ovl[key]
        return a
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = xx / W, yy / H
    v = (((x - .5) ** 2) * 0.75 + ((y - .5) ** 2) * 1.0)
    _ovl[key] = (-(v * 62))[..., None].astype(np.float32).repeat(3, axis=2)
    return _ovl[key]


# --------------------------------------------------------------- elements ---
def ribbon(text, accent, fs):
    f = monof(fs, True)
    h = int(fs * 1.95)
    w = int(f.getlength(text)) + int(h * 0.85)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, h], fill=accent)
    d.text((w / 2, h / 2 + 1), text, font=f, fill=(12, 12, 16), anchor="mm")
    return im


def avatar(size, seed):
    pal = [(255, 69, 0), (64, 208, 200), (255, 88, 176), (170, 180, 255),
           (255, 176, 32), (120, 220, 120), (255, 120, 90), (190, 140, 255)]
    c = pal[seed % len(pal)]
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=c)
    px = max(2, size // 10)
    rng = random.Random(seed * 31 + 5)
    ox = oy = (size - 5 * px) / 2
    cells = [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
             (1, 2), (2, 2), (3, 2), (1, 3), (2, 3)]
    body = (16, 16, 22)
    for (gx, gy) in cells:
        if rng.random() < 0.15:
            continue
        d.rectangle([ox + gx * px, oy + gy * px, ox + (gx + 1) * px - 1, oy + (gy + 1) * px - 1], fill=body)
    ey = oy + px + px // 2
    d.rectangle([ox + px, ey, ox + px + px // 2, ey + px // 2], fill=c)
    d.rectangle([ox + 3 * px, ey, ox + 3 * px + px // 2, ey + px // 2], fill=c)
    return im


# ------------------------------------------------------------------ cards ---
def upvote_icon(size, color):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(size / 2, 0), (size, size * 0.92), (0, size * 0.92)], fill=color)
    return im


def arrow_icon(w, h, color):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    t = max(3, int(h * 0.16))
    y = h / 2
    d.rectangle([0, y - t / 2, w * 0.62, y + t / 2], fill=color)
    d.polygon([(w * 0.58, y - h * 0.30), (w, y), (w * 0.58, y + h * 0.30)], fill=color)
    return im


def build_card(c, accent, idx, W):
    """Reddit-style comment card, shrunk to fit the content zone."""
    pad = L.pad
    cw = W - 2 * L.M
    inner = cw - 2 * pad
    tag = ribbon(c["tag"], accent, L.fs["top"])
    av = L.avatar
    uf = inter(700, L.fs["user"])
    mf = monof(L.fs["meta"])
    hdr_h = max(av, L.fs["user"] + int(L.fs["meta"] * 2.0))
    top = int(pad * 0.95)
    hy = top + tag.height + int(pad * 0.8)
    body_top = hy + hdr_h + int(pad * 0.6)
    bottom_pad = int(pad * 0.85)
    max_h = int(L.H * (0.60 if L.portrait else 0.585))

    # pick the biggest body size whose wrapped text fits the zone
    body_px = L.fs["body"]
    while True:
        bf = inter(400, body_px)
        lh = int(body_px * 1.46)
        lines = []
        for para in c["body"]:
            lines.extend(wrap(para, bf, inner - int(pad * 0.15)))
            lines.append("")
        lines = lines[:-1]
        ch = body_top + len(lines) * lh + bottom_pad
        if ch <= max_h or body_px <= 16:
            break
        body_px -= 1

    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    rrect(card, [0, 0, cw - 1, ch - 1], L.rad, fill=PANEL + (255,), outline=LINE + (255,), width=2)
    card.alpha_composite(tag, (pad, top))
    card.alpha_composite(avatar(av, idx), (pad, hy))
    ux = pad + av + int(pad * 0.55)
    ul = tlayer(c["user"], uf, USERCLR + (255,))
    card.alpha_composite(ul, (ux, hy))
    ml = tlayer("%s ago  \u2022  u/%s" % (c["time"], c["user"]), mf, MUTED + (255,))
    card.alpha_composite(ml, (ux, hy + ul.height + int(L.fs["meta"] * 0.3)))

    # vote pill with a drawn upvote triangle
    vf = monof(L.fs["score"], True)
    vs = c["votes"]
    tw = int(vf.getlength(vs))
    ph = int(L.fs["score"] * 1.9)
    tri = upvote_icon(int(ph * 0.42), UPVOTE)
    pw = int(ph * 0.55) + tri.width + int(ph * 0.22) + tw + int(ph * 0.55)
    pill = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    rrect(pill, [0, 0, pw - 1, ph - 1], ph // 2, fill=PANEL_L + (255,), outline=(72, 72, 92) + (255,), width=2)
    pd = ImageDraw.Draw(pill)
    pill.alpha_composite(tri, (int(ph * 0.55), (ph - tri.height) // 2 - 1))
    pd.text((int(ph * 0.55) + tri.width + int(ph * 0.22), ph / 2 + 1), vs, font=vf, fill=TXT, anchor="lm")
    card.alpha_composite(pill, (cw - pad - pw, hy + (hdr_h - ph) // 2))

    bd = ImageDraw.Draw(card)
    yy = body_top
    for ln in lines:
        if ln:
            bd.text((pad + 2, yy + int(lh * 0.80)), ln, font=bf, fill=TXT + (255,), anchor="la")
        yy += lh
    return card, 0


# ------------------------------------------------------------------ scenes ---
def scene_group(go, W, H):
    """Build a scene into elements (img, dx, dy-relative, delay) + total height."""
    kind = go["kind"]
    ac = ACCENTS[go.get("accent", "orange")]
    M = L.M
    maxw = W - 2 * M
    els = []
    y = 0

    def put(img, x, dy, delay=0.0, motion=0.35):
        els.append([img, int(x), int(dy), delay, motion])

    def center_text(txt, font, fill, delay=0.0, gap_after=0.0):
        nonlocal y
        im = tlayer(txt, font, fill)
        put(im, (W - im.width) / 2, y, delay)
        y += im.height + int(gap_after)

    # ------------------------------------------------------------ title/quote
    if kind in ("title", "quote", "end"):
        kick = go.get("kicker")
        if kick:
            kf = monof(L.fs["kicker"])
            kl = tlayer(kick.upper(), kf, MUTED + (255,))
            gap = int(L.fs["kicker"] * 0.9)
            w = kl.width + gap + int(L.fs["kicker"] * 0.75)
            im = Image.new("RGBA", (w, kl.height + int(L.fs["kicker"] * 0.2)), (0, 0, 0, 0))
            ImageDraw.Draw(im).rectangle([0, 0, int(L.fs["kicker"] * 0.42), im.height], fill=ac)
            im.alpha_composite(kl, (int(L.fs["kicker"] * 0.75), 0))
            put(im, (W - im.width) / 2, y, 0.0)
            y += im.height + int(L.fs["kicker"] * 0.8)

        l1, l2, l3 = go.get("l1", ""), go.get("l2", ""), go.get("l3", "")
        if kind == "end":
            hi = H * (0.135 if not L.portrait else 0.075)
        elif kind == "title":
            hi = H * (0.125 if not L.portrait else 0.082)
        else:
            hi = H * (0.098 if not L.portrait else 0.062)
        if kind == "end":
            hi = H * (0.125 if not L.portrait else 0.072)
        for i, (txt, col) in enumerate([(l1, ac if kind != "title" else TXT),
                                        (l2, TXT if kind != "title" else ac),
                                        (l3, ac)]):
            if not txt:
                continue
            f = fit_anton(txt, maxw, hi)
            im = tlayer(txt, f, col + (255,))
            put(im, (W - im.width) / 2, y, 0.07 * i, 0.5)
            y += int(f.size * 1.04)
        # rule + sub
        sub = go.get("sub", "")
        if sub:
            y += int(H * 0.014)
            rule = Image.new("RGBA", (int(W * (0.14 if not L.portrait else 0.22)), max(3, int(4 * L.s))), (0, 0, 0, 0))
            ImageDraw.Draw(rule).rectangle([0, 0, rule.width, rule.height], fill=ac + (235,))
            put(rule, (W - rule.width) / 2, y, 0.22, 0.25)
            y += rule.height + int(H * 0.024)
            sf = inter(500, L.fs["sub"])
            for ln in wrap(sub, sf, maxw):
                center_text(ln, sf, TXT + (255,), 0.26, int(L.fs["sub"] * 0.28))
        if kind == "end":
            csf = monof(int(L.fs["meta"] * 0.82))
            creds = ["thread: r/Piracy decomp discussion, 2026  \u2022  quotes: public Reddit comments, lightly trimmed",
                     "figures as claimed in the thread, unverified  \u2022  music + visuals generated for this video"]
            for cline in creds:
                im4 = tlayer(cline, csf, DIM + (255,))
                if im4.width > maxw:
                    continue
                put(im4, (W - im4.width) / 2, y + int(H * 0.05), 0.4, 0.15)
                y += int(csf.size * 1.7)

    # ------------------------------------------------------------------ stat
    elif kind == "stat":
        lbl = go.get("label", "")
        if lbl:
            lf = monof(L.fs["label"])
            center_text(lbl, lf, ac + (255,), 0.02, int(H * 0.012))
        f = fit_anton(go["big"], maxw, H * (0.155 if not L.portrait else 0.098))
        center_text(go["big"], f, TXT + (255,), 0.0, int(H * 0.012))
        sub = go.get("sub", "")
        if sub:
            sf = inter(500, L.fs["sub"])
            for ln in wrap(sub, sf, maxw):
                center_text(ln, sf, MUTED + (255,), 0.18, int(L.fs["sub"] * 0.25))

    # ----------------------------------------------------------------- money
    elif kind == "money":
        lf = monof(L.fs["label"])
        center_text(go.get("label", "IN"), lf, ac + (255,), 0.0, int(H * 0.006))
        num_h = int(H * (0.150 if not L.portrait else 0.090)) + int(H * 0.012)
        els.append(["__money__", go, y, num_h, 0])
        y += num_h + int(H * 0.042)
        bh = max(14, int(H * 0.017))
        lblh = int(L.fs["label"] * 1.9)
        block_h = 2 * (bh + lblh) + int(H * 0.014)
        els.append(["__moneybars__", block_h, bh, lblh, y])
        y += block_h + int(H * 0.030)
        sub = go.get("sub", "")
        if sub:
            sf = inter(500, L.fs["sub"])
            for ln in wrap(sub, sf, maxw):
                center_text(ln, sf, TXT + (255,), 0.30, int(L.fs["sub"] * 0.25))

    # ------------------------------------------------------------------ card
    elif kind == "card":
        card, over = build_card(go["comment"], ac, abs(hash(go["comment"]["user"])) % 8, W)
        els.append(["__card__", card, over, 0.0, 0])
        y += card.height

    # --------------------------------------------------------------- explain
    elif kind == "explain":
        s = min(W, H)
        bs = int(s * (0.26 if not L.portrait else 0.24))
        # lego block
        blk = Image.new("RGBA", (bs, bs), (0, 0, 0, 0))
        bd = ImageDraw.Draw(blk)
        rrect(blk, [0, bs * 0.2, bs - 1, bs - 1], int(bs * 0.07), fill=(196, 70, 44), outline=(255, 132, 92), width=3)
        for i in range(4):
            bx = bs * (0.12 + i * 0.215)
            bd.ellipse([bx, bs * 0.02, bx + bs * 0.15, bs * 0.22], fill=(232, 96, 60), outline=(255, 145, 105), width=2)
        # play-doh blob
        blob = Image.new("RGBA", (bs, bs), (0, 0, 0, 0))
        dd = ImageDraw.Draw(blob)
        n = 18
        for i in range(n):
            ang = 2 * math.pi * i / n
            r = bs * (0.36 + 0.05 * math.sin(i * 2.3))
            px = bs / 2 + r * math.cos(ang)
            py = bs / 2 + r * math.sin(ang)
            rr = bs * (0.13 + 0.02 * math.cos(i * 1.7))
            dd.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(86, 202, 194, 255))
        dd.ellipse([bs * 0.29, bs * 0.25, bs * 0.36, bs * 0.32], fill=(16, 60, 60, 255))
        dd.ellipse([bs * 0.49, bs * 0.24, bs * 0.56, bs * 0.31], fill=(16, 60, 60, 255))
        arrow = arrow_icon(bs * 0.30, bs * 0.22, MUTED + (255,))
        if L.portrait:
            put(blk, (W - bs) / 2, y, 0.0, 0.5)
            y += bs
            put(arrow, (W - bs * 0.30) / 2, y, 0.10, 0.3)
            y += int(bs * 0.34)
            put(blob, (W - bs) / 2, y, 0.16, 0.5)
            y += bs + int(H * 0.03)
        else:
            total = bs * 2 + int(bs * 0.34)
            x0 = (W - total) / 2
            put(blk, x0, y, 0.0, 0.5)
            put(arrow, x0 + bs + int(bs * 0.02), y + bs * 0.36, 0.10, 0.3)
            put(blob, x0 + bs + int(bs * 0.34), y, 0.16, 0.5)
            y += bs + int(H * 0.045)
        # title row: LEGO [arrow] PLAY-DOH
        f = anton(int(H * (0.070 if not L.portrait else 0.046)))
        a_img = arrow_icon(f.size * 0.62, f.size * 0.46, ac + (255,))
        pieces = [tlayer("LEGO", f, TXT + (255,)), a_img, tlayer("PLAY-DOH", f, ac + (255,))]
        gap = int(f.size * 0.30)
        tw = sum(p.width for p in pieces) + gap * (len(pieces) - 1)
        if tw > maxw:
            f = anton(int(f.size * maxw / tw))
            a_img = arrow_icon(f.size * 0.62, f.size * 0.46, ac + (255,))
            pieces = [tlayer("LEGO", f, TXT + (255,)), a_img, tlayer("PLAY-DOH", f, ac + (255,))]
            gap = int(f.size * 0.30)
            tw = sum(p.width for p in pieces) + gap * (len(pieces) - 1)
        row = Image.new("RGBA", (tw, max(p.height for p in pieces)), (0, 0, 0, 0))
        x = 0
        for p in pieces:
            row.alpha_composite(p, (x, (row.height - p.height) // 2))
            x += p.width + gap
        put(row, (W - row.width) / 2, y, 0.24, 0.4)
        y += row.height + int(H * 0.010)
        t2 = go.get("l2", "")
        f2 = fit_anton(t2, maxw, H * (0.048 if not L.portrait else 0.034))
        center_text(t2, f2, ac + (255,), 0.30, int(H * 0.012))
        sub = go.get("sub", "")
        if sub:
            sf = inter(500, L.fs["sub"])
            for ln in wrap(sub, sf, maxw):
                center_text(ln, sf, MUTED + (255,), 0.34, int(L.fs["sub"] * 0.22))

    # ---------------------------------------------------------------- decomp
    elif kind == "decomp":
        win_w = int(W * (0.86 if not L.portrait else 0.92))
        win_h = int(H * (0.34 if not L.portrait else 0.24))
        els.append(["__decomp__", win_w, win_h, 0.0, 0])
        y += win_h + int(H * 0.028)
        t1 = go.get("l1", "LIVE DECOMPILATION")
        f = fit_anton(t1, maxw, H * (0.058 if not L.portrait else 0.042))
        center_text(t1, f, ac + (255,), 0.16, int(H * 0.004))
        t2 = go.get("l2", "")
        if t2:
            f2 = monof(int(H * (0.024 if not L.portrait else 0.019)))
            center_text(t2, f2, MUTED + (255,), 0.2, int(H * 0.006))
        sub = go.get("sub", "")
        if sub:
            sf = inter(500, L.fs["sub"])
            for ln in wrap(sub, sf, maxw):
                center_text(ln, sf, TXT + (255,), 0.26, int(L.fs["sub"] * 0.2))

    return els, y


def build_scene(go, W, H):
    els, gh = scene_group(go, W, H)
    return {"els": els, "h": gh, "kind": go["kind"]}


# -------------------------------------------------------------- compositing ---
def draw_decomp(canvas, x, y, w, h, t, accent):
    win = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(win)
    rrect(win, [0, 0, w - 1, h - 1], int(w * 0.012), fill=(16, 16, 22, 235), outline=LINE + (255,), width=2)
    barh = int(h * 0.11)
    rrect(win, [0, 0, w - 1, barh], int(w * 0.012), fill=(34, 34, 46, 255))
    d.line([0, barh, w, barh], fill=LINE + (255,), width=2)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cxp = int(w * 0.025) + i * int(w * 0.022)
        d.ellipse([cxp, barh * 0.32, cxp + barh * 0.34, barh * 0.32 + barh * 0.34], fill=col)
    d.text((w * 0.13, barh * 0.52), "decomp \u2014 gta6.exe \u2014 watcher", font=monof(max(12, int(h * 0.042))), fill=MUTED, anchor="lm")
    canvas.alpha_composite(win, (int(x), int(y)))
    # code lines
    f = monof(max(11, int(h * 0.040)))
    rng = random.Random(9)
    ops = ["func_0x%04X", "sub_%04X", "mov", "ldr", "cmp", "b.eq", "stp", "ret", "nop", "adrp"]
    d2 = ImageDraw.Draw(canvas)
    ly = y + barh + int(h * 0.045)
    lh = int(f.size * 1.62)
    i = 0
    while ly + f.size < y + h - h * 0.045:
        addr = "%06X" % (rng.randint(0x1000, 0x9FFFF))
        op = rng.choice(ops)
        arg = rng.choice(["+0x1c", "x0, x1", "w2, #4", "0x20", "x3!, #0x10", "sp!, #0x10", "#1"])
        line = "%s   %-9s %s" % (addr, op, arg)
        col = (150, 216, 186) if i % 5 else (126, 170, 246)
        # lines appear progressively
        if ly < y + h * (0.16 + 0.84 * cl(t / 1.6)):
            d2.text((x + w * 0.045, ly), line, font=f, fill=col)
            if i == int(len(ops) * 1.2) and int(t * 3) % 2 == 0:
                d2.rectangle([x + w * 0.045, ly, x + w * 0.045 + w * 0.35, ly + lh], outline=accent + (180,), width=2)
        ly += lh
        i += 1


def render_group(canvas, sc, t, shake, accent, W, H):
    kind = sc["kind"]
    els, gh = sc["els"], sc["h"]
    avail = L.content_bot - L.content_top
    gy = L.content_top + max(0, int((avail - gh) * 0.45))
    for e in els:
        tag = e[0]
        if tag == "__card__":
            card = e[1]
            p = ease_out(cl(t / 0.6))
            x = (W - card.width) / 2 + shake[0]
            y = gy + (1 - p) * H * 0.05 + shake[1]
            alpha = cl(t / 0.3)
            spr = card
            if alpha < 0.999:
                spr = card.copy()
                spr.putalpha(card.split()[3].point(lambda v, a=alpha: int(v * a)))
            canvas.alpha_composite(spr, (int(x), int(y)))
        elif tag == "__money__":
            go, dy0, numh = e[1], e[2], e[3]
            prog = ease_out(cl((t - 0.1) / 1.3))
            val = go["target"] * prog
            s = "$" + format(int(val), ",d")
            f = anton(int(H * (0.150 if not L.portrait else 0.090)))
            while f.getlength(s) > W - 2 * L.M and f.size > 20:
                f = anton(f.size - 4)
            im = tlayer(s, f, ORANGE + (255,))
            canvas.alpha_composite(im, (int((W - im.width) / 2 + shake[0]), int(gy + dy0 + shake[1])))
        elif tag == "__moneybars__":
            block_h, bh, lblh, dy0 = e[1], e[2], e[3], e[4]
            d = ImageDraw.Draw(canvas)
            bx = int(W * (0.20 if not L.portrait else 0.08))
            bw = int(W * (0.60 if not L.portrait else 0.84))
            lf = monof(int(L.fs["label"] * 0.95))
            rows = [("REVENUE", 1.0, ORANGE, "$4B"), ("EST. DEV + MARKETING", 0.375, TEAL, "$1.5B")]
            prog = ease_out(cl((t - 0.25) / 1.2))
            for i, (name, frac, col, valtxt) in enumerate(rows):
                by = int(gy + dy0 + i * (bh + lblh + int(H * 0.012)))
                d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=PANEL_L + (255,))
                fw = max(4, int(bw * frac * prog))
                d.rounded_rectangle([bx, by, bx + fw, by + bh], radius=bh // 2, fill=col + (255,))
                ly = by + bh + int(lblh * 0.18)
                d.text((bx, ly), name, font=lf, fill=MUTED)
                if prog > 0.98:
                    d.text((bx + bw, ly), valtxt, font=lf, fill=col, anchor="ra")
        elif tag == "__decomp__":
            _, ww, wh, delay, _m = e
            p = ease_out(cl(t / 0.45))
            if p <= 0.01:
                continue
            x = (W - ww) / 2
            y = gy + (1 - p) * H * 0.04 + shake[1]
            draw_decomp(canvas, x, y, ww, int(wh * p) if p < 1 else wh, t, accent)
        else:
            img, x, dy, delay, motion = e
            lt = t - delay
            if lt < 0:
                continue
            alpha = cl(lt / 0.26)
            p = ease_out(cl(lt / 0.55))
            y = gy + dy + (1 - p) * H * 0.022 * (0.5 + motion) + math.sin(lt * 0.9) * 1.2
            spr = img
            if alpha < 0.999:
                spr = img.copy()
                spr.putalpha(img.split()[3].point(lambda v, a=alpha: int(v * a)))
            canvas.alpha_composite(spr, (int(x + shake[0]), int(y + shake[1])))


def caption_bar(t, text, W, H, accent):
    fs = L.fs["cap"]
    f = inter(800, fs)
    maxw = int(W * (0.88 if not L.portrait else 0.90))
    lines = wrap(text.upper(), f, maxw)
    lh = int(fs * 1.38)
    bw = max(f.getlength(ln) for ln in lines) + int(fs * 1.9)
    bh = lh * len(lines) + int(fs * 0.9)
    bar = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0))
    rrect(bar, [0, 0, bar.width - 1, bar.height - 1], int(fs * 0.38), fill=(9, 9, 13, 224), outline=accent + (185,), width=2)
    d = ImageDraw.Draw(bar)
    d.rectangle([0, 0, int(fs * 0.22), bar.height], fill=accent)
    yy = int(fs * 0.45)
    for ln in lines:
        d.text((int(fs * 0.95), yy), ln, font=f, fill=TXT, anchor="la")
        yy += lh
    return bar, (int((W - bar.width) / 2), int(H - L.safe_bottom(bh)))


# ------------------------------------------------------------------- audio ---
def clip_path(b):
    return "audio/beat%s.mp3" % b["id"][1:]


def decode_clip(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-i", path,
                        "-f", "s16le", "-ac", "1", "-ar", "44100", "-"],
                       capture_output=True, check=True)
    a = np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    nz = np.nonzero(np.abs(a) > 0.004)[0]
    if nz.size:
        a = a[max(0, nz[0] - int(0.05 * 44100)): nz[-1] + int(0.08 * 44100)]
    return a


def audio_durations():
    return [len(decode_clip(clip_path(b))) / 44100.0 for b in BEATS]


def build_voice(durs, path="build/voice.wav"):
    gap = int(0.28 * 44100)
    chunks = []
    for i, b in enumerate(BEATS):
        chunks.append(decode_clip(clip_path(b)))
        if i < len(BEATS) - 1:
            chunks.append(np.zeros(gap, np.float32))
    a = np.concatenate(chunks)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    return len(a) / 44100.0


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


def make_lofi(path, dur, bpm=76):
    sr = 44100
    n = int(dur * sr) + sr
    rng = np.random.default_rng(11)
    step = 60.0 / bpm
    bar = 4 * step
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]
    barN = int(round(bar * sr))
    tb = np.arange(barN) / sr
    pads = []
    for ch in chords:
        p = np.zeros(barN, np.float32)
        for note in ch:
            f = hz(note)
            for det in (-0.15, 0.15):
                ph = 2 * np.pi * (f + det) * tb
                p += (np.sin(ph) * 0.5 + np.sin(2 * ph) * 0.16 + np.sin(3 * ph) * 0.07).astype(np.float32) * 0.055
        pads.append(p)
    pad = np.zeros(n, np.float32)
    for b in range(n // barN + 1):
        i0, i1 = b * barN, min(n, (b + 1) * barN)
        pad[i0:i1] += pads[b % 4][:i1 - i0]
    t = np.arange(n) / sr
    pad *= (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t)).astype(np.float32)
    pad *= (1 - 0.35 * np.exp(-np.mod(t, step) * 9)).astype(np.float32)

    kick = np.zeros(n, np.float32)
    tt = np.arange(int(0.22 * sr)) / sr
    kf = 52 + 60 * np.exp(-tt * 30)
    kbody = (np.sin(2 * np.pi * np.cumsum(kf) / sr) * np.exp(-tt * 13) * 0.55).astype(np.float32)
    for k in range(int(dur * bpm / 60) + 2):
        idx = int(k * step * sr)
        if idx + kbody.size >= n:
            break
        kick[idx:idx + kbody.size] += kbody

    snare = np.zeros(n, np.float32)
    ts = np.arange(int(0.18 * sr)) / sr
    nz = rng.standard_normal(ts.size).astype(np.float32)
    sbody = nz * np.exp(-ts * 22).astype(np.float32) * 0.10
    for k in range(int(dur / step) + 2):
        idx = int((k + 0.5) * step * sr)
        if idx + sbody.size >= n:
            break
        snare[idx:idx + sbody.size] += sbody

    hats = np.zeros(n, np.float32)
    th = np.arange(int(0.06 * sr)) / sr
    hb = (rng.standard_normal(th.size) * np.exp(-th * 60) * 0.045).astype(np.float32)
    for k in range(int(dur / (step / 2)) + 2):
        idx = int(k * step / 2 * sr)
        if idx + hb.size >= n:
            break
        hats[idx:idx + hb.size] += hb

    crackle = ((rng.random(n) > 0.9985) * rng.standard_normal(n) * 0.12).astype(np.float32)
    noise = rng.standard_normal(n).astype(np.float32) * 0.006
    mix = pad + kick + snare + hats + crackle + noise
    fi, fo = int(2.0 * sr), int(3.0 * sr)
    mix[:fi] *= np.linspace(0, 1, fi).astype(np.float32)
    mix[-fo:] *= np.linspace(1, 0, fo).astype(np.float32)
    mix = mix / max(1e-6, np.max(np.abs(mix))) * 0.72
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    return path


def mix_audio(voice, lofi, out, dur):
    fc = (
        "[0:a]aresample=44100,pan=stereo|c0=c0|c1=c0,highpass=f=85,acompressor=threshold=0.12:ratio=3:attack=8:release=140[vo];"
        "[1:a]aresample=44100,volume=0.9,lowpass=f=3600,highpass=f=50[mu];"
        "[mu][vo]sidechaincompress=threshold=0.05:ratio=12:attack=10:release=350[md];"
        "[md][vo]amix=inputs=2:duration=longest:normalize=0,volume=1.35,"
        "alimiter=limit=0.85:level=false,aresample=44100[out]"
    )
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error", "-i", voice, "-i", lofi,
                    "-filter_complex", fc, "-map", "[out]", "-t", "%.3f" % dur,
                    "-c:a", "aac", "-b:a", "192k", out], check=True)


# L helper for caption position
def _safe_bottom(bh):
    return int(L.H * (0.085 if L.portrait else 0.048)) + bh
L.safe_bottom = staticmethod(_safe_bottom)


# ------------------------------------------------------------------- render ---
def main():
    fmt = sys.argv[1] if len(sys.argv) > 1 else "16x9"
    cfg = FORMATS[fmt]
    W, H, fps = cfg["W"], cfg["H"], cfg["fps"]
    L.init(W, H)
    get_bg(W, H)
    ovl = overlay(W, H)

    durs = audio_durations()
    beats, cur = [], 0.0
    for b, d in zip(BEATS, durs):
        scs = []
        for sc in b["scenes"]:
            f0, f1 = sc["frac"]
            scs.append((sc, cur + f0 * d, cur + f1 * d))
        beats.append(scs)
        cur += d + 0.28
    TOTAL = cur
    json.dump({"total": TOTAL, "beats": [[s0, s1] for sc, s0, s1 in beats[-1]]}, open("build/timing.json", "w"))

    cache = {}

    def cached(bi, si, go):
        key = (fmt, bi, si)
        if key not in cache:
            cache[key] = build_scene(go, W, H)
        return cache[key]

    caps = {}
    for bi, b in enumerate(BEATS):
        t0, t1 = beats[bi][0][1], beats[bi][-1][2]
        lst = CAPTIONS.get(b["id"], [])
        caps[bi] = [t0 - 0.7 + (t1 - t0 + 0.7) * i / max(1, len(lst)) for i in range(len(lst))]

    # preview mode
    pre = None
    if "--preview" in sys.argv:
        spec = sys.argv[sys.argv.index("--preview") + 1]
        out = sys.argv[sys.argv.index("--preview") + 2]
        bi, si = [int(v) for v in spec.split(":")]
        sc, s0, s1 = beats[bi][si]
        pre = (int((s0 + s1) * 0.5 * fps), out, s0)

    nframes = int(TOTAL * fps)
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-an", "build/video_only.mp4"]
    proc = None if pre else subprocess.Popen(cmd, stdin=subprocess.PIPE)
    rng = np.random.default_rng(3)

    for gf in range(nframes):
        if pre and gf != pre[0]:
            continue
        t = gf / fps
        bi = 0
        for i, b in enumerate(beats):
            if b[0][1] <= t:
                bi = i
        scs = beats[bi]
        si = 0
        for i, (sc_, s0, s1) in enumerate(scs):
            if s0 <= t < s1:
                si = i
                break
            if t >= s1:
                si = min(i + 1, len(scs) - 1)
        go, s0, s1 = scs[si]
        st = t - s0
        accent = ACCENTS[go.get("accent", "orange")]

        base = get_bg(W, H)
        shift = int(t * 6) % 128
        canvas = Image.fromarray(base[:, shift:shift + W].copy()).convert("RGBA")

        # per-beat glow light: added to the base image, drifting slowly
        s1 = 0.105 + 0.03 * math.sin(t * 0.4)
        s2 = 0.045 + 0.02 * math.cos(t * 0.31)
        g1 = glow_blob(W, H, accent)
        g2 = glow_blob(W, H, TEAL)
        ox1 = int(GP + 90 * math.sin(t * 0.2))
        oy1 = int(GP - H * 0.18)
        oy1 = max(0, min(oy1, 2 * GP))
        ox2 = int(GP - 130 * math.cos(t * 0.17))
        oy2 = int(GP - H * 0.05)
        oy2 = max(0, min(oy2, 2 * GP))
        ox1 = max(0, min(ox1, 2 * GP))
        ox2 = max(0, min(ox2, 2 * GP))
        base_f = base[:, shift:shift + W].astype(np.float32)
        base_f += g1[oy1:oy1 + H, ox1:ox1 + W] * s1
        base_f += g2[oy2:oy2 + H, ox2:ox2 + W] * s2
        canvas = Image.fromarray(np.clip(base_f, 0, 255).astype(np.uint8)).convert("RGBA")

        if go["kind"] != "card":
            fm = floating_marks(W, H, bi)
            off = int(t * 20) % max(1, fm.height - H)
            canvas.alpha_composite(fm.crop((0, off, W, off + H)).convert("RGBA"), (0, 0))

        # accent edge + top progress
        ed = ImageDraw.Draw(canvas)
        ed.rectangle([0, 0, max(3, int(W * 0.0035)), H], fill=accent + (140,))
        ed.rectangle([0, 0, int(W * cl(t / TOTAL)), max(5, int(H * 0.005))], fill=accent + (255,))

        gd_amt = 0
        if st < 0.12:
            gd_amt = int(1 + (0.12 - st) * 55)
        shake = (rng.normal(0, gd_amt * 0.25), rng.normal(0, gd_amt * 0.25)) if gd_amt else (0.0, 0.0)

        sc = cached(bi, si, go)
        render_group(canvas, sc, st, shake, accent, W, H)

        bar = caption_bar(t, next((c for i, c in enumerate(CAPTIONS.get(BEATS[bi]["id"], [])) if t >= caps[bi][i]), None),
                          W, H, accent) if st > 0.02 else None
        if bar:
            canvas.alpha_composite(bar[0], bar[1])

        arr = np.asarray(canvas.convert("RGB"), dtype=np.float32)
        arr += grain(gf, W, H)[..., None]
        arr += ovl
        arr = np.clip(arr, 0, 255)

        if gd_amt and gf % 2 == 0:
            img = Image.fromarray(arr.astype(np.uint8))
            for _ in range(3):
                y0 = int(rng.integers(0, H - 60))
                hgt = int(rng.integers(10, 70))
                dx = int(rng.integers(-gd_amt * 3, gd_amt * 3 + 1))
                sl = img.crop((0, y0, W, y0 + hgt))
                r, g, b = sl.split()
                img.paste(Image.merge("RGB", (b, g, r)), (dx, y0))
            arr = np.asarray(img, dtype=np.float32)

        out = arr.astype(np.uint8)
        if pre:
            Image.fromarray(out).save(pre[1])
            print("wrote", pre[1])
            return
        proc.stdin.write(out.tobytes())
        if gf % 120 == 0:
            print("frame %d/%d  t=%.1fs" % (gf, nframes, t), flush=True)

    proc.stdin.close()
    proc.wait()

    make_lofi("build/lofi.wav", TOTAL)
    voice = "build/voice.wav"
    build_voice(durs, voice)
    mix_audio(voice, "build/lofi.wav", "build/mix.m4a", TOTAL)
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                    "-i", "build/video_only.mp4", "-i", "build/mix.m4a",
                    "-c:v", "copy", "-c:a", "copy", "-shortest", cfg["out"]], check=True)
    print("DONE", cfg["out"], "%.1fs" % TOTAL)


if __name__ == "__main__":
    main()
