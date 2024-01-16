# Pdf-Image-Remover
Remove specific image from pdf file. It matches the image with same size and pattern.

## Script Overview
# Objective
The Python script performs various image processing tasks, including converting a PDF to images, modifying the images, and creating a new PDF. Additionally, it removes specified logos from the images using template matching.

# Components
The script consists of the following major components:

PDF to Images Conversion (read_pdf function)

Converts each page of a PDF file into a series of images.
Modifies the images by adjusting dimensions and saving them.
Logo Removal from Images (remove_logo function)

Utilizes template matching to identify and remove logos from images.
Supports multiple logo templates for removal.
Images to PDF Conversion (convert_images_to_pdf function)

Combines modified images into a single PDF document.
Adjusts page size to A4 dimensions.
Main Processing Loop (main function)

Iterates through a folder of images.
Applies logo removal and modification operations.
Converts the modified images to a final PDF.
Usage
Image Modification

The script reads a PDF file and converts its pages into images.
It modifies the images by adjusting dimensions and saving them.
Logo Removal

The script removes specified logos from the images based on template matching.
Multiple logo templates can be provided.
PDF Generation

The modified images are combined into a single PDF document.
The output PDF is created with A4 page dimensions.
Configuration
Input PDF file: pdf_file variable.
Logo templates: logo_template_path list.
Output PDF file: output_pdf variable.
Dependencies
Python packages: pdf2image, cv2, numpy, Pillow, reportlab.
External tools: Poppler (used by pdf2image for PDF conversion).
Note
The script should be adapted and configured according to the specific requirements and file paths in the user's environment.
Feel free to adjust the documentation based on additional details or specific usage instructions relevant to your application.
