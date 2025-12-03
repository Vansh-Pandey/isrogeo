"""
Image utility functions for downloading and processing images
"""
import requests
from PIL import Image
from io import BytesIO
from typing import Union
import os
from pathlib import Path


def download_image(image_url: str, timeout: int = 30) -> Image.Image:
    """
    Download image from URL and return as PIL Image
    
    Args:
        image_url: URL of the image to download
        timeout: Request timeout in seconds
        
    Returns:
        PIL Image object
        
    Raises:
        Exception: If download fails or image is invalid
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(image_url, timeout=timeout, headers=headers)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download image from {image_url}: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to process image: {str(e)}")


def save_temp_image(image: Image.Image, filename: str) -> str:
    """
    Save image to temporary directory
    
    Args:
        image: PIL Image object
        filename: Desired filename
        
    Returns:
        Path to saved image
    """
    temp_dir = Path("/tmp/geonli_images")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = temp_dir / filename
    image.save(filepath)
    
    return str(filepath)


def cleanup_temp_image(filepath: str):
    """
    Delete temporary image file
    
    Args:
        filepath: Path to image file
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Failed to cleanup temp image {filepath}: {e}")


def validate_image_dimensions(image: Image.Image, expected_width: int, expected_height: int) -> bool:
    """
    Validate image dimensions match expected values
    
    Args:
        image: PIL Image object
        expected_width: Expected width in pixels
        expected_height: Expected height in pixels
        
    Returns:
        True if dimensions match, False otherwise
    """
    width, height = image.size
    return width == expected_width and height == expected_height