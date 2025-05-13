# NewsVision

**Final Year Project 2024/25 – NTU EEE**  
**Author:** Gan Wei Jie

## Overview

NewsVision is a Python-based image analysis tool designed to process and extract information from news article images. It uses Optical Character Recognition (OCR) to identify and analyze text regions in images. The project supports multiple OCR engines, including optional integration with Tesseract OCR.

## Features

- Image input processing for news articles  
- Text detection and extraction using OCR  
- Optional Tesseract OCR integration  
- Debug mode to visualize bounding boxes  
- Sample outputs provided in the Output directory

## Getting Started

Follow the instructions below to set up and run the project.

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/NewsVision.git
    cd NewsVision
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. (Optional) Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) if you want to use the Tesseract version.

### Usage

1. Place input images in the `Input/` directory.

2. Run the main script:
    ```bash
    python Code/NewsVision.py
    ```

3. Output results will be saved in the `Output/` directory.

### Debug Mode

To enable debug mode and output bounding boxes, open `Code/NewsVision.py` and set:

```python
debug_mode = True
```
### Sample Output

Example processed images and OCR results can be found in the `Output/` directory.