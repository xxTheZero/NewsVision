from PIL import Image, ImageDraw, ImageFont
import os

# Label colours, feel free to change to your liking
LABEL_COLORS = {
    "Title":        "#ff0000",
    "Subheader":    "#fee08b",
    "Content":      "#ff8000",
    "Author":       "#f599e1",
    "Image":        "#D3F261",
    "Caption":      "#389E0D",
    "Summary":      "#5CDBD3",
    "Miscellaneous":"#096DD9",
    "Title2":       "#ADC6FF",
    "Content2":     "#9254DE"
}

def hex_to_rgb(hex_color):
    """Convert hex color (e.g., '#ff0000') to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2 ,4))

def draw_and_save_boxes(image, layout_results, save_path, font_path=None):
    """
    Draw labeled bounding boxes with colored background and white text inside.

    Args:
        image (PIL.Image): The input image.
        layout_results (list): List of dicts with 'bbox' and 'type'.
        save_path (str): Path to save the visualized image.
        font_path (str): Optional path to a TTF font file.
    """
    image_with_boxes = image.copy()
    draw = ImageDraw.Draw(image_with_boxes)
    margin = 4  # margin between text and box edge

    try:
        font = ImageFont.truetype(font_path, 16) if font_path else ImageFont.load_default()
    except:
        font = ImageFont.load_default()

    for res in layout_results:
        bbox = res['bbox']
        label = res['type'].capitalize()
        score = res.get('score', None)
        label_text = f"{label} ({score:.2f})" if score is not None else label
        color = hex_to_rgb(LABEL_COLORS.get(label, "#FF00FF"))  # fallback: magenta

        # Draw box outline
        draw.rectangle(bbox, outline=color, width=3)

        # Calculate label text size
        text_size = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]

        # Determine label box position (top-left inside the box with margin)
        label_x = bbox[0] + margin
        label_y = bbox[1] + margin

        # Draw filled rectangle for label background
        draw.rectangle(
            [label_x - margin, label_y - margin,
             label_x + text_width + margin, label_y + text_height + margin],
            fill=color
        )

        # Draw label text in white
        draw.text((label_x, label_y), label_text, fill='white', font=font)

    image_with_boxes.save(save_path)
    print(f"Bounding box visualization saved to: {save_path}")