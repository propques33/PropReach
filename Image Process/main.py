import os
from PIL import Image, ExifTags
import argparse

def correct_image_orientation(image):
    """Corrects image orientation based on EXIF data."""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        
        exif = image._getexif()
        if exif is not None:
            orientation = exif.get(orientation)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(-90, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # If there's no EXIF data or orientation tag, skip correction
        pass
    return image

def crop_to_square(image):
    """Crops the image to the largest possible square."""
    width, height = image.size
    min_dimension = min(width, height)
    left = (width - min_dimension) / 2
    top = (height - min_dimension) / 2
    right = (width + min_dimension) / 2
    bottom = (height + min_dimension) / 2
    return image.crop((left, top, right, bottom))

def process_images(image_folder):
    """Reads all images from a folder, corrects orientation, crops to square, resizes to 960x960, and renames them."""
    images = [f for f in os.listdir(image_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    for i, image_file in enumerate(images, 1):
        image_path = os.path.join(image_folder, image_file)
        img = Image.open(image_path)
        
        # Correct the image orientation based on EXIF
        img = correct_image_orientation(img)
        
        # Crop to square
        img_cropped = crop_to_square(img)
        
        # Resize to 960x960
        img_resized = img_cropped.resize((960, 960))
        
        # Save the image with a new name
        new_image_name = f"{i}.jpg"
        img_resized.save(os.path.join(image_folder, new_image_name))
        print(f"Processed {image_file} and saved as {new_image_name}")


if __name__ == "__main__":
    # Use argparse to handle command-line arguments
    parser = argparse.ArgumentParser(description="Process images in a folder.")
    parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        default='images',
        help='Path to the folder containing images to process. Default is "images".'
    )
    args = parser.parse_args()

    # Get the image folder from command-line arguments
    image_folder = args.image_folder

    # Call the function
    process_images(image_folder)