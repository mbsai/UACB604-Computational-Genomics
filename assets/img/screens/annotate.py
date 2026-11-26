"""Crop the raw captures and draw numbered callouts -> <name>.jpg used by the slides.

Boxes are given in "preview" coordinates (the page scaled to 900 px wide);
S converts them to raw pixels. After re-capturing, check the boxes still
sit on the right things (sites move their layout around).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
ACCENT = (214, 51, 132)          # magenta: visible on blue, teal and dark pages
FONT = None
for f in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
    if pathlib.Path(f).exists():
        FONT = f; break

SPEC = {
    # name: (crop box, [callout boxes]) all in preview coordinates
    "ensembl":     ((0, 0, 610, 400),
                    [(33, 85, 141, 106), (84, 111, 184, 129, "tr"), (372, 111, 478, 129), (143, 348, 402, 382)]),
    "uniprot":     ((0, 0, 760, 340),
                    [(194, 44, 456, 80), (268, 129, 467, 150), (623, 82, 722, 104)]),
    "bioproject":  ((62, 108, 820, 545),
                    [(476, 135, 582, 154), (81, 151, 472, 170, "l"), (88, 515, 410, 533)]),
    "runselector": ((0, 85, 900, 600),
                    [(213, 115, 377, 139), (158, 371, 347, 394), (348, 371, 487, 394), (158, 504, 900, 524)]),
    "ena_project": ((55, 540, 640, 870),
                    [(283, 723, 347, 744), (476, 706, 602, 752), (58, 630, 212, 650), (406, 628, 514, 654)]),
    "ena_j02482":  ((45, 124, 845, 385),
                    [(56, 138, 202, 160, "tr"), (73, 263, 282, 283, "l"), (73, 283, 282, 302, "l"), (663, 166, 812, 207)]),
}

def scale(name):
    w = Image.open(RAW / f"{name}.png").width
    return w / 900

def make(name):
    crop, boxes = SPEC[name]
    s = scale(name)
    im = Image.open(RAW / f"{name}.png").convert("RGB")
    cx0, cy0 = crop[0] * s, crop[1] * s
    im = im.crop(tuple(int(v * s) for v in crop))
    d = ImageDraw.Draw(im)
    r = int(17 * s / 3.2 * 1.6)                       # badge radius
    font = ImageFont.truetype(FONT, int(r * 1.35)) if FONT else ImageFont.load_default()
    lw = max(4, int(2 * s))
    for i, b in enumerate(boxes, 1):
        x0, y0, x1, y1 = [(b[0] * s - cx0), (b[1] * s - cy0), (b[2] * s - cx0), (b[3] * s - cy0)]
        d.rounded_rectangle((x0, y0, x1, y1), radius=lw * 2, outline=ACCENT, width=lw)
        bx, by = max(r + 2, x0 - r * 0.55), max(r + 2, y0 - r * 0.55)
        if len(b) > 4 and b[4] == "tr":                # badge at the top-right corner instead
            bx = x1 + r * 0.55
        if len(b) > 4 and b[4] == "l":                 # badge to the left, vertically centred
            bx, by = max(r + 2, x0 - r - lw), (y0 + y1) / 2
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=ACCENT, outline="white", width=max(2, lw // 2))
        d.text((bx, by), str(i), fill="white", font=font, anchor="mm")
    if im.width > 1800:
        im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
    out = HERE / f"{name}.jpg"
    im.save(out, quality=82, optimize=True, progressive=True)
    print(out.name, im.size, f"{out.stat().st_size/1024:.0f} kB")

if __name__ == "__main__":
    for n in SPEC:
        make(n)
