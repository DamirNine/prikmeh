# fix_arrows.py - fix dimension arrows in image19.png
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

im = Image.open(r"scratch_media/image19.png").convert("RGB")
draw = ImageDraw.Draw(im)
orig = np.array(Image.open(r"scratch_media/image19.png").convert("RGB"))

W = (255, 255, 255)
BK = "black"

# ─────────────────────────────────────────────────────────────────────────────
# 1. FIX odk (kamen): shorten diameter line to circle boundary
# ─────────────────────────────────────────────────────────────────────────────
CX, CY, R = 1132.46, 675.89, 93.6
LINE_START  = np.array([1158.0, 660.0])
LINE_END_BAD = np.array([1030.0, 747.0])

d    = LINE_END_BAD - LINE_START
dlen = float(np.linalg.norm(d))
u    = d / dlen

ox = LINE_START[0] - CX
oy = LINE_START[1] - CY
b2 = ox * u[0] + oy * u[1]
c  = ox**2 + oy**2 - R**2
t_good = -b2 + math.sqrt(b2**2 - c)  # far intersection

LINE_END_GOOD = LINE_START + u * t_good
ex, ey = int(round(LINE_END_GOOD[0])), int(round(LINE_END_GOOD[1]))

# Erase overshoot: white blob along line from correct end to past old end
PAD = 9
t0, t1 = t_good - 3, dlen + 16
for i in range(201):
    t  = t0 + (t1 - t0) * i / 200
    px = int(round(LINE_START[0] + u[0] * t))
    py = int(round(LINE_START[1] + u[1] * t))
    draw.ellipse([px-PAD, py-PAD, px+PAD, py+PAD], fill=W)

# Redraw line from start to correct end
draw.line([(int(round(LINE_START[0])), int(round(LINE_START[1]))), (ex, ey)],
          fill=BK, width=4)

# Arrowhead at correct end
AL, AW = 18, 7
perp = np.array([-u[1], u[0]])
tip  = np.array([ex, ey])
b    = tip - u * AL
p1   = b + perp * AW
p2   = b - perp * AW
draw.polygon([(int(round(tip[0])), int(round(tip[1]))),
              (int(round(p1[0])),  int(round(p1[1]))),
              (int(round(p2[0])),  int(round(p2[1])))], fill=BK)
print(f"odk fixed: arrowhead now at ({ex},{ey})")

# ─────────────────────────────────────────────────────────────────────────────
# 1b. FIX od (kulisa hole) leader: the pristine leader is NOT one straight
# line — it is a straight segment from the label that kinks into a curved
# hook running along the bottom of the circle before its arrowhead. That
# curved hook is the "shifted/extra arrow" defect. Found via connected-
# component analysis (the whole blob — ring + leader — is one component;
# subtracting the fitted ring annulus from it isolates exactly the stray
# line+hook pixels). Erase all of it, redraw a clean ring, then draw one
# straight radial leader from the label to the boundary.
# ─────────────────────────────────────────────────────────────────────────────
from scipy import ndimage

OCX, OCY, OR = 371.8908289919709, 637.8344635689203, 66.53262867282413

cy0, cy1, cx0, cx1 = 560, 745, 190, 460
sub = orig[cy0:cy1, cx0:cx1, 0]
dark = sub < 160
lbl, _n = ndimage.label(dark, structure=np.ones((3, 3)))
comp_id = lbl[int(OCY) - cy0 - int(OR), int(OCX) - cx0]  # point at ring top
ys, xs = np.where(lbl == comp_id)
xs_full, ys_full = xs + cx0, ys + cy0
dist_full = np.sqrt((xs_full - OCX) ** 2 + (ys_full - OCY) ** 2)
stray = np.abs(dist_full - OR) > 5
xl, yl = xs_full[stray], ys_full[stray]

canvas = np.zeros((cy1 - cy0, cx1 - cx0), dtype=bool)
canvas[yl - cy0, xl - cx0] = True
canvas = ndimage.binary_dilation(canvas, iterations=3)

arr = np.array(im)
region = arr[cy0:cy1, cx0:cx1]
region[canvas] = 255
im = Image.fromarray(arr)
draw = ImageDraw.Draw(im)
draw.ellipse([OCX - OR, OCY - OR, OCX + OR, OCY + OR], outline=BK, width=7)
print(f"old od leader+hook erased ({stray.sum()} px, dilated), ring redrawn clean")

# Draw a new leader: start right after the (shifted) label, pointed straight
# at the circle center, crossing the near edge and stopping with the
# arrowhead touching the FAR inner wall — i.e. the arrow sits inside the
# circle, same convention as the odk fix above, not just tangent to it.
OD_START = np.array([285.0, 716.0])
od_to_center = np.array([OCX, OCY]) - OD_START
od_dist = float(np.linalg.norm(od_to_center))
od_u = od_to_center / od_dist
OD_TIP = OD_START + od_u * (od_dist + OR)
oex, oey = int(round(OD_TIP[0])), int(round(OD_TIP[1]))

draw.line([(int(round(OD_START[0])), int(round(OD_START[1]))), (oex, oey)],
          fill=BK, width=3)
AL2, AW2 = 14, 5
perp2 = np.array([-od_u[1], od_u[0]])
tip2 = np.array([oex, oey])
base2 = tip2 - od_u * AL2
p1b = base2 + perp2 * AW2
p2b = base2 - perp2 * AW2
draw.polygon([(int(round(tip2[0])), int(round(tip2[1]))),
              (int(round(p1b[0])), int(round(p1b[1]))),
              (int(round(p2b[0])), int(round(p2b[1])))], fill=BK)
print(f"od leader redrawn, radial tip at ({oex},{oey})")

# ─────────────────────────────────────────────────────────────────────────────
# 1c. Shift the "d" letter in "ød" further right: visible gap from "ø", and
# clear of the kulisa body contour strokes that pass close to this corner
# (diagonal contour tip at x~232,y~695 above; another at x~257,y~751 below).
# ─────────────────────────────────────────────────────────────────────────────
D_X0, D_Y0, D_X1, D_Y1 = 234, 697, 261, 740
SHIFT_D = 14
d_patch = im.crop((D_X0, D_Y0, D_X1, D_Y1)).copy()
draw.rectangle([D_X0-1, D_Y0-1, D_X1+1, D_Y1+1], fill=W)
im.paste(d_patch, (D_X0 + SHIFT_D, D_Y0))
print("letter d shifted")

# ─────────────────────────────────────────────────────────────────────────────
# 2. FIX bp (kulisa slot width): erase broken marks, redraw arrow + restore ellipse
# ─────────────────────────────────────────────────────────────────────────────
SLOT_X0, SLOT_X1 = 477, 701
SLOT_Y0, SLOT_Y1 = 617, 660
CAP_R  = (SLOT_Y1 - SLOT_Y0) // 2   # 21
CAP_CX = SLOT_X1 - CAP_R            # 680

# 2a. Erase all broken-bp marks.
# Pixel scan of original shows: broken text at x=741-765, ellipse at x=783-789 — no overlap!
broken_boxes = [
    (694, 593, 716, 639),   # L-bracket at right of lп extension tick
    (694, 651, 725, 666),   # tiny stray dash below slot
    (728, 617, 769, 645),   # "б"-like upper text fragment (comp99)
    (727, 644, 769, 673),   # "п"-like lower text fragment (comp104)
]
for (x0, y0, x1, y1) in broken_boxes:
    draw.rectangle([x0, y0, x1, y1], fill=W)

# Restore slot right cap in case erase nicked it
draw.arc([CAP_CX - CAP_R, SLOT_Y0, CAP_CX + CAP_R, SLOT_Y1],
         start=-90, end=90, fill=BK, width=4)

# 2c. Draw a clean vertical bp dimension arrow just right of the slot right cap
# Place at x=708 (7px right of slot tip at x=701), y: 617..660
AX   = 708
YTOP = SLOT_Y0    # 617
YBOT = SLOT_Y1    # 660
AMID = (YTOP + YBOT) // 2   # 638

LTHK = 3   # line thickness
AH   = 10  # arrowhead height
AHW  = 4   # arrowhead half-width

# Thin extension ticks from slot top/bottom to the arrow line
draw.line([(SLOT_X1, YTOP), (AX + 3, YTOP)], fill=BK, width=LTHK)
draw.line([(SLOT_X1, YBOT), (AX + 3, YBOT)], fill=BK, width=LTHK)

# Vertical centre line
draw.line([(AX, YTOP + AH), (AX, YBOT - AH)], fill=BK, width=LTHK)

# Arrowheads: upward at YTOP, downward at YBOT
draw.polygon([(AX, YTOP),       (AX - AHW, YTOP + AH), (AX + AHW, YTOP + AH)], fill=BK)
draw.polygon([(AX, YBOT),       (AX - AHW, YBOT - AH), (AX + AHW, YBOT - AH)], fill=BK)

# Label "bп" — font matching existing labels (~22px at image res)
try:
    font = ImageFont.truetype(r"C:/Windows/Fonts/arial.ttf", 22)
except Exception:
    font = ImageFont.load_default()

draw.text((AX + 7, AMID - 11), "bп", font=font, fill=BK)
print("bp fixed")

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
out = "scratch_media/image19_fixed.png"
im.save(out)
print(f"saved: {out}")
