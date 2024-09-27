""" pdfcleaner.py

    Utility to clean up pdfs that have been annotated in a predictable
    way that might be able to be fixed by removing coloured annnotations

    Originally designed to remove hand written notes and solutions added
    to examination papers, to allow for re-printing and re-use without
    the notes visible

    Filtering is based primarily on RGB colour levels, although there is
    also a very basic filter based on the absolute x/y co-oprdinate to 
    allow for ignoring large parts of a page if required.

"""

from pathlib import Path
from config import settings
from pdf2image import convert_from_path
from PIL import Image


def remove_color_from_image(imput_image):

    temp_img = imput_image.convert("RGB")
    width = temp_img.size[0]
    height = temp_img.size[1]
    for i in range(0, width):  # process all pixels
        for j in range(0, height):
            data = temp_img.getpixel((i, j))
            max_col = max(data)
            min_col = min(data)
            if max_col > 200 and min_col > 200:
                output_col = (255, 255, 255)
            elif max_col > 96 and min_col < 64:  # Single dominant colour
                output_col = (255, 255, 255)
            elif max_col < 96:  # All low values, should be black pixels
                output_col = (0, 0, 0)
            elif data[0] == data[1] == data[2]:
                if min_col < 200:
                    output_col = (0, 0, 0)
                else:
                    output_col = (255, 255, 255)
            else:
                # Put white
                output_col = (255, 255, 255)

            temp_img.putpixel((i, j), output_col)

    return temp_img


def tweaked_color_from_image(imput_image):

    temp_img = imput_image.convert("RGB")
    width = temp_img.size[0]
    height = temp_img.size[1]
    print(f"Image is {width} x {height}")
    for i in range(0, width):  # process all pixels
        for j in range(0, height):
            colour_data = temp_img.getpixel((i, j))
            val_r = colour_data[0]
            val_g = colour_data[1]
            val_b = colour_data[2]
            max_col = max(colour_data)
            min_col = min(colour_data)
            # data[0] = Red,  [1] = Green, [2] = Blue
            # data[0,1,2] range = 0~255
            # if colour_data == (0, 176, 240):  # Specific colour
            if j < 2000:  # Y co-ordinate
                output_col = colour_data
            elif max_col > 200 and min_col > 200:
                output_col = (255, 255, 255)
            elif max_col > 96 and min_col < 64:  # Enough Single colour
                output_col = (255, 255, 255)
            elif max_col < 96:
                # put black
                output_col = (0, 0, 0)
            elif val_r == val_g == val_b:
                if min_col < 200:
                    output_col = (0, 0, 0)
                else:
                    output_col = (255, 255, 255)
            else:
                # Put white
                output_col = (255, 255, 255)

            temp_img.putpixel((i, j), output_col)

    return temp_img


def tweak_single_image(source_pdf_file_name):
    """Modifies a single image"""

    source_pdf = Path(source_pdf_file_name)
    input_images = convert_from_path(source_pdf, dpi=300)
    assert len(input_images) == 1, "Bad image source pdf"
    single_image = input_images[0]
    print(f"Loaded image from {source_pdf.name}")

    img_file_name = Path(settings.OUTPUT_FOLDER) / f"{source_pdf.name}_tweaked.jpg"
    clean_img = tweaked_color_from_image(single_image)
    clean_img.save(img_file_name, "JPEG")
    print(f"Saved {img_file_name.name}")


def cleanup_multipage_pdf():
    """opens a pdf, saves each page as a single images, performing some
    basic colour processing to remove annotations"""

    source_pdf = Path(settings.INPUT_PDF_FOLDER) / settings.INPUT_PDF_FILE

    assert source_pdf.is_file(), "Invalid source pdf"
    print(f"Source PDF is {source_pdf.name}")

    all_images = convert_from_path(source_pdf, dpi=300)
    print(f"Loaded {len(all_images)} images from {source_pdf.name}")

    total_images = len(all_images)
    for img_num in range(total_images):
        img_file_name = Path(settings.OUTPUT_FOLDER) / f"source_image_{img_num:03}.jpg"
        # Save pages as images in the pdf
        clean_img = remove_color_from_image(all_images[img_num])
        clean_img.save(img_file_name, "JPEG")
        print(f"Saved {img_num+1:03} of {total_images:03} to {img_file_name.name} ")
        # all_images[img_num].save(img_file_name, "JPEG")


def convert_images_to_pdf():
    """Convert sequential fixed images back into a single pdf"""

    sorted_images = list()

    for img_counter in range(0, 32):
        this_img = Image.open(
            Path(settings.INPUT_IMAGE_FOLDER) / f"source_image_{img_counter:03}.jpg"
        )
        sorted_images.append(this_img)

    pdf_path = Path(settings.OUTPUT_FOLDER) / "Recombined_output.pdf"

    sorted_images[0].save(
        pdf_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=sorted_images[1:],
    )


if __name__ == "__main__":
    # cleanup_multipage_pdf()

    # Do just one image with custom settings
    # tweak_single_image("/path/to/29_raw_input_Annotated_input.pdf")

    convert_images_to_pdf()
