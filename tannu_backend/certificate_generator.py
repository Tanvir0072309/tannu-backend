"""
certificate_generator.py  —  tannu_backend/
Generates per-student certificate PNG using Pillow.

Template: tannu_backend/assets/Tannu-certificate-demo.png
          (your actual gold/black certificate image — 2000×1414 px)

Flow:
  1. Open the PNG template
  2. White-out the pre-existing placeholder text areas
  3. Draw student's Name, Body paragraph, Udyam No, Certificate No
  4. Return PNG bytes

Requirements:
    pip install pillow

Fonts used (already on Ubuntu / bundled with most systems):
  - Lora-Italic-Variable.ttf   (name field — elegant italic serif)
  - Lora-Variable.ttf          (body text)
  - LiberationSerif-Bold.ttf   (certificate number — bold)
"""

import io
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ─── FONT PATHS (try in order; first found wins) ─────────────────────────────
_FONT_CANDIDATES = {
    "italic": [
        "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
    ],
    "regular": [
        "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    ],
}


def _get_font(style: str, size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES[style]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    # Absolute last resort: PIL default (no kerning, ugly but works)
    return ImageFont.load_default()


# ─── COLORS ───────────────────────────────────────────────────────────────────
_GOLD   = (101, 76,  0)    # dark gold — for student name
_DARK   = ( 25, 15,  5)    # near-black — for body text
_BROWN  = ( 55, 38,  8)    # warm brown — for Udyam No
_CREAM  = (230, 200, 130)  # cream/gold — for cert no on dark strip
_BG     = (255, 255, 243)  # cream background of certificate
_STRIP  = ( 30, 22, 10)    # dark strip at the very bottom


# ─── CANVAS SIZE (template is 2000×1414) ─────────────────────────────────────
_W = 2000
_H = 1414

# ─── TEXT ZONES (pixel coordinates on 2000×1414 template) ────────────────────
# These were calibrated against Tannu-certificate-demo.png
_ZONE_NAME_Y      = 478          # top-y for student name
_ZONE_BODY_Y      = 738          # top-y for body paragraph
_ZONE_BODY_LH     = 50           # line-height in px for body text
_ZONE_BODY_WRAP   = 92           # max chars per body line
_ZONE_UDYAM_XY    = (112, 1240)  # start (x, y) of Udyam No text
_ZONE_CERTNO_XY   = (100, 1338)  # start (x, y) of Certificate No

# Erase rectangles (covers old placeholder text in template)
_ERASE_NAME   = (280,  478, 1720,  535)
_ERASE_BODY   = ( 80,  730, 1920,  930)
_ERASE_UDYAM  = ( 80, 1235,  700, 1278)
_ERASE_CERTNO = ( 40, 1332,  820, 1385)


# ─── HELPER: center text horizontally ────────────────────────────────────────
def _draw_centered(draw: ImageDraw.ImageDraw, text: str, font, y: int, color: tuple):
    bb = draw.textbbox((0, 0), text, font=font)
    x = (_W - (bb[2] - bb[0])) // 2
    draw.text((x, y), text, font=font, fill=color)


# ─── HELPER: format date ─────────────────────────────────────────────────────
def _fmt_date(val) -> str:
    if not val:
        return "—"
    if hasattr(val, "strftime"):
        try:
            return val.strftime("%-d %B %Y")
        except ValueError:
            return val.strftime("%d %B %Y").lstrip("0")
    return str(val)


# ─── MAIN PUBLIC FUNCTION ─────────────────────────────────────────────────────
def generate_certificate(student, udyam_no: str = "UDYAM-GJ-XXXXXXXX") -> bytes:
    """
    Generate a certificate PNG for `student` and return raw PNG bytes.

    `student` must have attributes:
        .name, .start_date, .end_date, .cert_no
    """
    template_path = _find_template()

    img  = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fonts
    fnt_name   = _get_font("italic",  84)
    fnt_body   = _get_font("regular", 35)
    fnt_small  = _get_font("regular", 33)
    fnt_certno = _get_font("bold",    43)

    # ── 1. ERASE placeholder areas ────────────────────────────────────────────
    draw.rectangle(_ERASE_NAME,   fill=_BG)
    draw.rectangle(_ERASE_BODY,   fill=_BG)
    draw.rectangle(_ERASE_UDYAM,  fill=_BG)
    draw.rectangle(_ERASE_CERTNO, fill=_STRIP)

    # ── 2. STUDENT NAME ───────────────────────────────────────────────────────
    name = student.name.strip()
    _draw_centered(draw, name, fnt_name, _ZONE_NAME_Y, _GOLD)

    # ── 3. BODY PARAGRAPH ─────────────────────────────────────────────────────
    start_str = _fmt_date(student.start_date)
    end_str   = _fmt_date(student.end_date)
    body = (
        f"This is to certify that {name} has successfully completed the "
        f"One-Month Tailoring & Cutting Certification Course conducted from "
        f"{start_str} to {end_str}. During this training program, the student "
        f"successfully learned fabric cutting, stitching techniques, body measurements, "
        f"sewing machine handling, and garment finishing with dedication and practical performance."
    )
    y = _ZONE_BODY_Y
    for line in textwrap.wrap(body, width=_ZONE_BODY_WRAP):
        _draw_centered(draw, line, fnt_body, y, _DARK)
        y += _ZONE_BODY_LH

    # ── 4. UDYAM REGISTRATION NO ──────────────────────────────────────────────
    draw.text(
        _ZONE_UDYAM_XY,
        f"Udyam Registration No: {udyam_no}",
        font=fnt_small,
        fill=_BROWN,
    )

    # ── 5. CERTIFICATE NUMBER ─────────────────────────────────────────────────
    draw.text(
        _ZONE_CERTNO_XY,
        f"Certificate No: {student.cert_no}",
        font=fnt_certno,
        fill=_CREAM,
    )

    # ── 6. Encode to PNG bytes ─────────────────────────────────────────────────
    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(200, 200))
    return buf.getvalue()


# ─── TEMPLATE FINDER ──────────────────────────────────────────────────────────
def _find_template() -> Path:
    """
    Look for the template PNG in several locations.
    Priority order:
      1. tannu_backend/assets/Tannu-certificate-demo.png   (production location)
      2. CERTIFICATE_TEMPLATE_PATH from Django settings (if set)
      3. Any .png in tannu_backend/assets/
    """
    # 1. Try Django settings first so it works from any cwd
    try:
        from django.conf import settings as djs
        base = Path(djs.BASE_DIR)
        candidate = base / "tannu_backend" / "assets" / "Tannu-certificate-demo.png"
        if candidate.exists():
            return candidate

        # 2. Check CERTIFICATE_TEMPLATE_PATH setting
        tp = getattr(djs, "CERTIFICATE_TEMPLATE_PATH", None)
        if tp and Path(tp).exists():
            return Path(tp)

        # 3. Any PNG in assets/
        assets = base / "tannu_backend" / "assets"
        pngs = list(assets.glob("*.png"))
        if pngs:
            return pngs[0]

    except Exception:
        pass

    # Fallback: relative to this file
    here = Path(__file__).parent
    for name in ["Tannu-certificate-demo.png", "certificate_template.png"]:
        p = here / "assets" / name
        if p.exists():
            return p

    raise FileNotFoundError(
        "Certificate template not found!\n"
        "→ Place  Tannu-certificate-demo.png  inside  tannu_backend/assets/\n"
        "  (This is the gold/black certificate image you provided.)"
    )


# ─── BACKWARD COMPAT alias (old views.py called generate_certificate_pptx) ───
generate_certificate_pptx = generate_certificate