from paddleocr import PaddleOCR, PPStructure
import os
from PIL import Image
import numpy as np
from visualize_boxes import draw_and_save_boxes

# Settings
languages = 'ch'  # Use 'en' for English, 'ch' for Chinese
input_dir = 'Input'
output_dir = 'Output'
model_dir = "Models/newsvision 2.0"
filename_suffix = "_extract.txt"
image_suffix = "_bboxes.jpg"
font_path = './fonts/simfang.ttf'  # Update this to a valid font file path if needed
config_path = os.path.join(model_dir, "infer_cfg.yml")
labels_path = os.path.join(model_dir, "labels.txt")
separator = "\n----------------\n\n"
debug_mode = False

# Define the desired order of labels
label_order = [
    "Title", "Author", "Summary", 
    "Subheader", "Content", 
    "Title2", "Content2", 
    "Image", "Caption", "Miscellaneous"
]

# Initialize the PaddleOCR and PPStructure models
ocr = PaddleOCR(use_angle_cls=True, use_space_char=True, lang=languages, use_gpu=True)
layout_engine = PPStructure(
    layout_model_dir = model_dir,  # Custom layout model
    layout_model_config = config_path,
    layout_dict_path = labels_path,
    lang="ch",
    layout_score_threshold=0.6,
    use_gpu=True
)

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def group_and_sort_bounding_boxes(boxes):
    """
    Group bounding boxes into columns and sort by position in reading order.
    """
    grouped_boxes = []

    # Sort boxes top-to-bottom and then left-to-right
    boxes = sorted(boxes, key=lambda b: (b['bbox'][1], b['bbox'][0]))

    def belongs_to_column(box, column):
        """Check if a box belongs to an existing column."""
        x_center = (box['bbox'][0] + box['bbox'][2]) / 2
        for col_box in column:
            col_x_min, col_y_min, col_x_max, col_y_max = col_box['bbox']
            if col_x_min <= x_center <= col_x_max or (
                box['bbox'][0] <= col_x_max and box['bbox'][2] >= col_x_min
            ):
                return True
        return False

    # Group boxes into columns
    for box in boxes:
        added = False
        for column in grouped_boxes:
            if belongs_to_column(box, column):
                column.append(box)
                added = True
                break
        if not added:
            grouped_boxes.append([box])  # Start a new column

    # Sort columns left-to-right by their x_min
    grouped_boxes.sort(key=lambda column: min(b['bbox'][0] for b in column))

    # Sort boxes within each column top-to-bottom
    sorted_groups = [sorted(column, key=lambda b: b['bbox'][1]) for column in grouped_boxes]

    # Flatten the sorted groups into a single list
    flat_sorted_boxes = [box for column in sorted_groups for box in column]

    return flat_sorted_boxes

def process_and_group_boxes(label_content, group_labels):
    """Group and sort bounding boxes for specified labels."""
    boxes = [
        {'type': label, 'bbox': item['bbox'], 'text': item['text']}
        for label in group_labels
        for item in label_content[label]
    ]
    if boxes:
        return group_and_sort_bounding_boxes(boxes)
    return []

for filename in os.listdir(input_dir):
    if filename.lower().endswith(('.jpg', '.png')):
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + filename_suffix
        output_path = os.path.join(output_dir, output_filename)

        # Open and process the image
        image = Image.open(input_path).convert('RGB')
        image_array = np.array(image)
        print(f"Processing {filename}, image shape: {image_array.shape}")
        layout_results = layout_engine(image_array)

        if debug_mode:
            # Save the bounding box visualization
            visual_output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + image_suffix)
            draw_and_save_boxes(image, layout_results, visual_output_path)

        label_content = {label: [] for label in label_order}
        output_lines = []

        for res in layout_results:
            region_type = res['type'].capitalize()
            bbox = res['bbox']
            cropped_array = np.array(image.crop((bbox[0], bbox[1], bbox[2], bbox[3])))
            results = ocr.ocr(cropped_array, cls=True)
            
            if results and results[0]:
                text = "\n".join([line[1][0] for line in results[0]])
                if text:
                    label_content[region_type].append({'bbox': bbox, 'text': text})
            else:
                print(f"No OCR results for bbox {bbox}")

        # Process grouped labels dynamically
        label_groups = [
            (["Title"], "Title"),
            (["Author"], "Author"),
            (["Summary"], "Summary"),
            (["Subheader", "Content"], "Content"),
            (["Title2", "Content2"], "Additional Content"),
        ]

        for group_labels, header in label_groups:
            grouped_boxes = process_and_group_boxes(label_content, group_labels)
            if grouped_boxes:
                if header == "Title" or header == "Author" or header == "Summary":
                    output_lines.append(f"{header}:\n")
                    for box in grouped_boxes:
                        output_lines.append(f"{box['text']}\n")
                elif header == "Content" or header == "Additional Content":
                    for i, box in enumerate(grouped_boxes):                        
                            if i > 0:
                                output_lines.append(f"\n")
                            if debug_mode:
                                output_lines.append(f"{box['type']}:{box['bbox']}\n{box['text']}\n")
                            else:
                                output_lines.append(f"{box['type']}:\n{box['text']}\n")
                output_lines.append(separator)

        # Handle other content
        for label in ["Image", "Caption", "Miscellaneous"]:
            if label_content[label]:
                output_lines.append(f"{label}:\n")
                output_lines.extend([f"{item['text']}\n" for item in label_content[label]])
                output_lines.append(separator)

        # Write the ordered and formatted content to the file
        final_output = "".join(output_lines).strip()
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(final_output)

        print(f"OCR processed and saved to: {output_filename}")