#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2026, Muhammad Heidir
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import sys
import io
import qrcode
import platform

import cairosvg
from PIL import Image, ImageDraw, ImageFont


def check_arguments():
    """
    Checks if the correct number of arguments are supplied via the command line.
    Expects: script.py <url> <output_filename> [svg_logo_path]
    """
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(f"[ERROR] Invalid number of arguments supplied.")
        print(f"[INFO] Usage: python {sys.argv[0]} <url> <output_filename> [svg_logo_path]")
        sys.exit(1)

    url_path = sys.argv[1]
    output_filename = sys.argv[2]
    logo_path = sys.argv[3] if len(sys.argv) == 4 else "logo.svg"

    return url_path, output_filename, logo_path


def load_svg_as_pil(svg_path, target_width=None, target_height=None):
    """Renders an SVG file directly into a Pillow RGBA Image using cairosvg."""
    png_bytes = cairosvg.svg2png(
        url=svg_path,
        output_width=target_width,
        output_height=target_height
    )
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def get_system_font(font_size):
    """Detects the operating system and loads a high-quality scalable font."""
    system = platform.system()

    if system == "Windows":
        font_names = ["arial.ttf", "calibri.ttf", "segoeui.ttf"]
        font_dir = "C:\\Windows\\Fonts"
    elif system == "Darwin":  # macOS
        font_names = [
            "Arial.ttf",
            "Helvetica.ttc",
            "SFNS.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        font_dir = "/Library/Fonts"
    else:  # Linux / Unix
        font_names = [
            "OpenSans_Bold.ttf",
            "LiberationSans-Regular.ttf",
            "DejaVuSans.ttf",
            "Ubuntu-R.ttf",
        ]
        font_dir = "/home/mheidir/.local/share/fonts/o"

    for name in font_names:
        full_path = (
            name if os.path.isabs(name) else os.path.join(font_dir, name)
        )
        if os.path.exists(full_path) or name == "Arial.ttf":
            try:
                return ImageFont.truetype(full_path, 56)
            except IOError:
                continue

    print("[WARN] Warning: Could not find system TTF fonts. Using default font.")
    return ImageFont.load_default()


def generate_framed_qrborder(url_data, output_filename="framed_qr.png", label_text="SCAN TO VISIT", logo_path="logo.svg"):
    box_size = 10
    # 1. Use ERROR_CORRECT_H to ensure scannability with central obstructions
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=4,
    )
    qr.add_data(url_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    qr_w, qr_h = qr_img.size

    # 2. Render and Overlay SVG Logo across horizontal center
    if os.path.exists(logo_path):
        # Calculate maximum banner height (~15% of QR height for scanning reliability)
        max_banner_h = int(qr_h * 0.15)
        
        # Render SVG to target width/height
        logo = load_svg_as_pil(logo_path, target_height=max_banner_h)
        
        # Ensure rendered width isn't overly wide
        target_logo_w = min(logo.width, int(qr_w * 0.65))
        if target_logo_w != logo.width:
            logo = load_svg_as_pil(logo_path, target_width=target_logo_w)

        # Calculate coordinates
        band_padding = 8
        band_h = logo.height + band_padding
        band_top = (qr_h - band_h) // 2
        band_bottom = band_top + band_h

        # Draw central horizontal white strip
        qr_draw = ImageDraw.Draw(qr_img)
        margin_x = int(qr_w * 0.10)  # Keep finder boundaries intact
        qr_draw.rectangle([margin_x, band_top, qr_w - margin_x, band_bottom], fill="white")

        # Paste SVG logo in center
        logo_x = (qr_w - logo.width) // 2
        logo_y = (qr_h - logo.height) // 2
        qr_img.paste(logo, (logo_x, logo_y), logo)
    else:
        print(f"[WARN] SVG logo not found at '{logo_path}'. Generating base QR code.")

    # Convert back to RGB for canvas frame assembly
    qr_img = qr_img.convert("RGB")

    # 3. Canvas and Frame Dimensions
    frame_padding = 20
    bottom_space = 80
    line_thickness = 20
    font_size = 12

    canvas_w = qr_w + (frame_padding * 2)
    canvas_h = qr_h + (frame_padding * 2) + bottom_space

    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    canvas_draw = ImageDraw.Draw(canvas)

    # 4. Paste QR on Canvas
    canvas.paste(qr_img, (frame_padding, frame_padding))

    # 5. Outer Frame
    frame_x0 = frame_padding // 2
    frame_y0 = frame_padding // 2
    frame_x1 = canvas_w - (frame_padding // 2)
    frame_y1 = canvas_h - (frame_padding // 2)

    canvas_draw.rounded_rectangle(
        [frame_x0, frame_y0, frame_x1, frame_y1],
        radius=20,
        outline="black",
        width=line_thickness,
    )

    # 6. Apply Label Text
    font = get_system_font(font_size)

    text_box = canvas_draw.textbbox((0, 0), label_text, font=font)
    text_w = text_box[2] - text_box[0]

    text_x = (canvas_w - text_w) // 2
    text_y = qr_h + (frame_padding * 2) + (bottom_space - 160) // 2 - 10

    canvas_draw.text((text_x, text_y), label_text, fill="black", font=font)

    canvas.save(output_filename)
    print(f"[INFO] Framed QR Code exported successfully to '{output_filename}'")


if __name__ == "__main__":
    url_path, output_filename, logo_path = check_arguments()
    print(f"[INFO] URL retrieved: {url_path}")
    print(f"[INFO] SVG Logo path: {logo_path}")

    try:
        generate_framed_qrborder(url_path, output_filename, label_text="Md. Heidir", logo_path=logo_path)
        print(f"[INFO] Success! Saved QR code to '{output_filename}'.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        sys.exit(1)

sys.exit(0)