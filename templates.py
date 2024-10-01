from PIL import Image, ImageDraw, ImageFont
import random
import os

def get_font(font_name, size):
    """
    Helper function to load a font. Tries to load the font from the local 'fonts' directory.
    If not found, falls back to default font.
    """
    try:
        # Assume fonts are stored in a 'fonts' directory next to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(current_dir, 'fonts')
        font_path = os.path.join(fonts_dir, font_name)
        font = ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Failed to load {font_name}, using default font.")
        font = ImageFont.load_default()
    return font

def template_1(image, headline, insta_handle):
    draw = ImageDraw.Draw(image)
    
    # Load fonts using the helper function
    font_large = get_font("Roboto-Bold.ttf", 50)
    font_small = get_font("Roboto-Regular.ttf", 30)

    # Create a black rectangle at the top for the headline
    rectangle_height_top = 150
    draw.rectangle([0, 0, image.width, rectangle_height_top], fill="black")
    draw.text((50, 30), headline, font=font_large, fill="white")

    # Add contact info and Instagram handle at the bottom
    rectangle_height_bottom = 80
    draw.rectangle([0, image.height - rectangle_height_bottom, image.width, image.height], fill="#1a73e8")

    contact_info = "+91 9893034016"
    website = f"@{insta_handle}"

    # Left bottom for Instagram handle
    left_margin = 50
    draw.text((left_margin, image.height - 60), website, font=font_small, fill="white")

    # Right bottom for contact info
    bbox = draw.textbbox((0, 0), contact_info, font=font_small)
    text_width = bbox[2] - bbox[0]
    right_margin = image.width - text_width - 50
    draw.text((right_margin, image.height - 60), contact_info, font=font_small, fill="white")

def template_2(image, headline, insta_handle):
    contact_info = "+91 9893034016"
    draw = ImageDraw.Draw(image)

    # Load fonts using the helper function
    font_large = get_font("Roboto-Bold.ttf", 50)
    font_small = get_font("Roboto-Regular.ttf", 30)

    # Add a semi-transparent black bar for the headline (at the top)
    rectangle_height_top = 120
    draw.rectangle([0, 0, image.width, rectangle_height_top], fill=(0, 0, 0, 160))  # Semi-transparent black

    # Draw the headline in the top left with a shadow for contrast
    headline_position = (40, 30)
    shadow_offset = 3
    draw.text((headline_position[0] + shadow_offset, headline_position[1] + shadow_offset), headline, font=font_large, fill="gray")  # Shadow
    draw.text(headline_position, headline, font=font_large, fill="white")  # Main text

    # Bottom semi-transparent rectangle for contact info and Instagram handle
    rectangle_height_bottom = 80
    draw.rectangle([0, image.height - rectangle_height_bottom, image.width, image.height], fill=(0, 0, 0, 160))  # Semi-transparent black

    # Instagram handle at the bottom-left, with better spacing
    instagram_position = (40, image.height - 55)
    draw.text(instagram_position, f"@{insta_handle}", font=font_small, fill="white")

    # Contact info at the bottom-right with proper spacing
    bbox = draw.textbbox((0, 0), contact_info, font=font_small)
    text_width = bbox[2] - bbox[0]
    right_margin = image.width - text_width - 40
    draw.text((right_margin, image.height - 55), contact_info, font=font_small, fill="white")

    # Optional: Add a subtle thin border around the image
    border_color = (255, 255, 255, 100)  # Semi-transparent white
    border_thickness = 8
    draw.rectangle([border_thickness, border_thickness, image.width - border_thickness, image.height - border_thickness], outline=border_color, width=border_thickness)

def template_3(image, headline, insta_handle):
    draw = ImageDraw.Draw(image)

    # Colors
    primary_color = "#1a73e8"  # Bold blue color for contrast and highlights
    text_color = "#ffffff"     # White color for text readability
    highlight_color = "#ffcc00"  # Accent color for small elements or highlights

    # Load fonts using the helper function
    font_large = get_font("Roboto-Bold.ttf", 60)
    font_small = get_font("Roboto-Regular.ttf", 35)

    # 1. Background is the existing image; no additional fill needed

    # 2. Use a Geometric Shape or Graphic Element at the Top
    draw.ellipse(
        [(image.width - 400, -100), (image.width + 100, 300)],  # Positioned partly offscreen for a dynamic look
        fill=primary_color
    )

    # 3. Add Headline with Bold Font (Centered)
    headline_bbox = draw.textbbox((0, 0), headline, font=font_large)
    headline_width = headline_bbox[2] - headline_bbox[0]
    draw.text(
        ((image.width - headline_width) / 2, 100),  # Position the headline centrally
        headline,
        font=font_large,
        fill=text_color
    )

    # 4. Add a Divider or a Line Under the Headline for Emphasis
    draw.line([(100, 200), (image.width - 100, 200)], fill=primary_color, width=5)

    # 5. Add Sub-Headline or Text in Modern Style Below the Headline
    sub_headline = "Visit our Website"
    sub_bbox = draw.textbbox((0, 0), sub_headline, font=font_small)
    sub_width = sub_bbox[2] - sub_bbox[0]
    draw.text(
        ((image.width - sub_width) / 2, 250),  # Positioned centrally under the headline
        sub_headline,
        font=font_small,
        fill=highlight_color
    )

    # 6. Add Social Media Handle and Contact Info at the Bottom
    contact_info = "+91 9893034016"
    draw.rectangle(
        [50, image.height - 150, image.width - 50, image.height - 50],
        fill=primary_color,
        outline=None,
        width=0
    )

    # Instagram handle - left aligned in bottom rectangle
    draw.text(
        (75, image.height - 120),
        f"@{insta_handle}",
        font=font_small,
        fill="white"
    )

    # Contact info - right aligned in bottom rectangle
    contact_bbox = draw.textbbox((0, 0), contact_info, font=font_small)
    contact_text_width = contact_bbox[2] - contact_bbox[0]
    draw.text(
        (image.width - contact_text_width - 75, image.height - 120),
        contact_info,
        font=font_small,
        fill="white"
    )

def select_template(image, headline, insta_handle):
    """Randomly select a template and apply it to the image."""
    templates = [template_1, template_2, template_3]
    chosen_template = random.choice(templates)
    chosen_template(image, headline, insta_handle)
    return image
