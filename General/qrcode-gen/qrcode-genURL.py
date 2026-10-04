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
import json
import qrcode
import platform

from PIL import Image, ImageDraw, ImageFont

def check_arguments():
    """
    Checks if the correct number of arguments are supplied via the command line.
    Expects: script.py <input_vcf_path> <output_filename>
    """
    # sys.argv[0] is always the script name itself.
    # We need exactly 2 items in the list (script name + 2 arguments).
    if len(sys.argv) != 3:
        print(f"[ERROR] Invalid number of arguments supplied.")
        print(f"[INFO] Usage: python {sys.argv[0]} <url>")
        sys.exit(1) # Exit the script with an error code

    # Assign arguments to meaningful variables
    url_path = sys.argv[1]
    output_filename = sys.argv[2]

    return url_path, output_filename


def generate_vcard_qr(data, filename="vcard_qr.png"):
    # 2. Configure the QR Code generator
    # We use a higher error correction (ERROR_CORRECT_H) because vCard data
    # strings can be quite long, making the QR dense.
    qr = qrcode.QRCode(
        version=None,  # None allows the library to auto-size based on the data length
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,   # Controls the size of each pixel box
        border=4,      # Thickness of the white border (minimum recommended is 4)
    )

    # 3. Add the vCard string into the QR object
    qr.add_data(data)
    qr.make(fit=True)

    # 4. Generate and save the image
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"[INFO] Success! Your vCard QR code has been saved as '{filename}'.")

    return

def get_system_font(font_size):
    """Detects the operating system and loads a high-quality scalable font."""
    system = platform.system()

    # Common font paths across different Operating Systems
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
        #font_dir = "/usr/share/fonts/truetype"
        font_dir = "/home/mheidir/.local/share/fonts/o"

    # Try to load an available system font
    for name in font_names:
        full_path = (
            name if os.path.isabs(name) else os.path.join(font_dir, name)
        )
        if os.path.exists(full_path) or name == "Arial.ttf":
            try:
                #return ImageFont.truetype(full_path, font_size)
                return ImageFont.truetype(full_path, 56)
            except IOError:
                continue

    # Fallback if no true type font files are found
    print("[WARN] Warning: Could not find system TTF fonts. Using default font.")
    return ImageFont.load_default()

def generate_framed_qr(vcard_data, output_filename="framed_qr.png", label_text="SCAN TO SAVE MY CONTACT"
):
    # 1. Generate the styled QR Code base
    box_size = 10
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=4,
    )
    qr.add_data(vcard_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert(
        "RGB"
    )
    qr_w, qr_h = qr_img.size

    # Apply the rounded eye styling from the previous step
    border_offset = 4 * box_size
    eye_size = 7 * box_size
    corner_radius = int(eye_size * 0.35)
    qr_draw = ImageDraw.Draw(qr_img)

    positions = [
        (border_offset, border_offset),
        (qr_w - border_offset - eye_size, border_offset),
        (border_offset, qr_h - border_offset - eye_size),
    ]

    #for pos_x, pos_y in positions:
    #    draw_rounded_eye(
    #        qr_draw, pos_x, pos_y, eye_size, box_size, radius=corner_radius
    #    )

    # 2. Design the Custom Frame Dimensions
    frame_padding = 40  # Spaces between QR code and the frame line
    bottom_space = 80  # Extra room at the bottom for text
    line_thickness = 6  # Thickness of the frame border line

    # Calculate overall final canvas size
    canvas_w = qr_w + (frame_padding * 2)
    canvas_h = qr_h + (frame_padding * 2) + bottom_space

    # Create new blank white canvas
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    canvas_draw = ImageDraw.Draw(canvas)

    # 3. Paste the QR code onto the center of the canvas
    canvas.paste(qr_img, (frame_padding, frame_padding))

    # 4. Draw the Outer Framed Rounded Boundary Box
    # Define coordinate constraints for the bounding rectangle
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

    # 5. Add Custom Text Label
    try:
        # Tries to load standard default system font, scales to size 24
        font = ImageFont.load_default()
    except IOError:
        font = ImageFont.load_default()

    # Calculate centered position for text using text bbox
    text_box = canvas_draw.textbbox((0, 0), label_text, font=font)
    text_w = text_box[2] - text_box[0]

    # Center horizontal coordinate, position vertical coordinate near the bottom
    text_x = (canvas_w - text_w) // 2
    text_y = canvas_h - bottom_space

    canvas_draw.text((text_x, text_y), label_text, fill="black", font=font)

    # Save final framed output
    canvas.save(output_filename)
    print(f"[INFO] Framed QR Code exported successfully to '{output_filename}'")

def generate_framed_qrborder(vcard_data, output_filename="framed_qr.png",label_text="SCAN TO SAVE CONTACT"):
    # 1. Generate the styled QR Code base
    box_size = 10
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=4,
    )
    qr.add_data(vcard_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert(
        "RGB"
    )
    qr_w, qr_h = qr_img.size

    # Apply the rounded eye styling
    border_offset = 4 * box_size
    eye_size = 7 * box_size
    corner_radius = int(eye_size * 0.35)
    qr_draw = ImageDraw.Draw(qr_img)

    positions = [
        (border_offset, border_offset),
        (qr_w - border_offset - eye_size, border_offset),
        (border_offset, qr_h - border_offset - eye_size),
    ]
    #for pos_x, pos_y in positions:
    #    draw_rounded_eye(
    #        qr_draw, pos_x, pos_y, eye_size, box_size, radius=corner_radius
    #    )

    # 2. Design the Custom Frame Dimensions (Increased space for text)
    frame_padding = 20  # Spaces between QR code and the frame line
    bottom_space = 80  # Extra room at the bottom for larger text
    line_thickness = 20  # Thickness of the frame border line
    font_size = 12  # 👈 Adjust this number to make the text larger or smaller

    # Calculate overall final canvas size
    canvas_w = qr_w + (frame_padding * 2)
    canvas_h = qr_h + (frame_padding * 2) + bottom_space

    # Create new blank white canvas
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    canvas_draw = ImageDraw.Draw(canvas)

    # 3. Paste the QR code onto the canvas
    canvas.paste(qr_img, (frame_padding, frame_padding))

    # 4. Draw the Outer Framed Rounded Boundary Box
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

    # 5. Load and Apply the Large Custom Font
    font = get_system_font(font_size)

    # Calculate centered position for text using text bounding box
    text_box = canvas_draw.textbbox((0, 0), label_text, font=font)
    text_w = text_box[2] - text_box[0]
    text_h = text_box[3] - text_box[1]

    # Center horizontally, place in the middle of the bottom space buffer
    text_x = (canvas_w - text_w) // 2
    """
    text_y = (
        qr_h + (frame_padding * 2) + (bottom_space - text_h) // 2 - 10
    )  # Adjusted offset
    """
    text_y = (
        qr_h + (frame_padding * 2) + (bottom_space - 160) // 2 - 10
    )  # Adjusted offset

    canvas_draw.text((text_x, text_y), label_text, fill="black", font=font)

    # Save final framed output
    canvas.save(output_filename)
    print(
        f"[INFO] Framed QR Code with large text exported successfully to '{output_filename}'"
    )

if __name__ == "__main__":
    # 1. Validate arguments first
    url_path, output_filename = check_arguments()
    print(f"[INFO] URL retrieved: {url_path}")

    try:
        # 3. Save the data to the specified output filename (saving as JSON here)
        #generate_vcard_qr(data, output_path)
        generate_framed_qrborder(url_path, output_filename, label_text="Md. Heidir")

        print(f"[INFO] Success! Successfully parsed 1 url into '{output_filename}'.")

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        sys.exit(1)

sys.exit(0)
