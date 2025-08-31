from pathlib import Path
from PIL import Image


IMAGE_VARIANTS = {
    "original": None,
    "thumbnail": 100,
    "small": 300,
    "medium": 500,
    "large": 700,
}


def get_image_variants(
    base_dir: str, file_id: str, extention: str, base_url: str
) -> dict[str, tuple[str, str, int]]:
    """
    Returns a dictionary containing the file paths for the different image variants.
    """
    data = {}
    for category, width in IMAGE_VARIANTS.items():
        output_dir = Path(f"{base_dir}/{file_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        data[category] = (
            f"{output_dir}/{category}.{extention}",
            f"{base_url}/{file_id}/{category}.{extention}",
            width,
        )
    return data


def format_image_to_png(image: Image.Image) -> Image.Image:
    """
    Formats the input image to be suitable for saving as PNG.
    Ensures the image is in RGB or RGBA mode.

    Parameters:
        image (Image.Image): Input image.

    Returns:
        Image.Image: Formatted image.
    """
    if image.mode in ("RGBA", "P"):  # If image has transparency or palette
        return image.convert("RGBA")
    else:
        return image.convert("RGB")  # For non-transparent images


def resize_image(image: Image.Image, width: int) -> Image.Image:
    """
    Resizes the image to the specified width while maintaining the aspect ratio.

    Parameters:
        image (Image.Image): Input image.
        width (int): Desired width of the resized image.

    Returns:
        Image.Image: Resized image.
    """
    width = min(width, image.width)
    if width == image.width:
        return image
    aspect_ratio = image.height / image.width
    height = int(width * aspect_ratio)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_image_as_png(image: Image.Image, filepath: str) -> None:
    """
    Saves the image in PNG format to the specified filepath.

    Parameters:
        image (Image.Image): Input image.
        filepath (str): Destination file path (should end with .png).

    Returns:
        None
    """
    image.save(filepath, format="PNG", optimize=True)
