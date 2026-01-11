"""
Image Resizer Service Module

This module provides utilities for image resizing, format conversion, and optimization.
Supports common image formats like JPEG, PNG, WebP, and GIF.
"""

import os
import io
from typing import Tuple, Optional, Union
from pathlib import Path
from PIL import Image


class ImageResizer:
    """
    A utility class for resizing and optimizing images.
    
    Supports various image formats and provides methods for:
    - Resizing with aspect ratio preservation
    - Format conversion
    - Quality optimization
    - Thumbnail generation
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'JPEG', 'PNG', 'WEBP', 'GIF', 'BMP', 'TIFF'}
    
    # Default quality settings
    DEFAULT_QUALITY = 85
    THUMBNAIL_QUALITY = 80
    
    def __init__(self, quality: int = DEFAULT_QUALITY):
        """
        Initialize the ImageResizer.
        
        Args:
            quality (int): Default quality for image compression (1-100).
                          Defaults to 85.
        """
        self.quality = max(1, min(100, quality))
    
    @staticmethod
    def get_image_dimensions(image_path: Union[str, Path]) -> Tuple[int, int]:
        """
        Get the dimensions of an image.
        
        Args:
            image_path (Union[str, Path]): Path to the image file.
            
        Returns:
            Tuple[int, int]: (width, height) of the image.
            
        Raises:
            FileNotFoundError: If image file doesn't exist.
            IOError: If unable to open the image.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception as e:
            raise IOError(f"Failed to open image: {e}")
    
    @staticmethod
    def calculate_aspect_ratio_dimensions(
        original_size: Tuple[int, int],
        target_size: Tuple[int, int]
    ) -> Tuple[int, int]:
        """
        Calculate new dimensions while preserving aspect ratio.
        
        Args:
            original_size (Tuple[int, int]): Original (width, height).
            target_size (Tuple[int, int]): Target (max_width, max_height).
            
        Returns:
            Tuple[int, int]: New (width, height) maintaining aspect ratio.
        """
        orig_width, orig_height = original_size
        target_width, target_height = target_size
        
        # Calculate aspect ratio
        aspect_ratio = orig_width / orig_height
        
        # Determine scaling based on which dimension is the constraint
        if orig_width > target_width or orig_height > target_height:
            if target_width / target_height > aspect_ratio:
                # Height is the constraint
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            else:
                # Width is the constraint
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            
            return (new_width, new_height)
        
        return original_size
    
    def resize(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
        size: Tuple[int, int],
        maintain_aspect_ratio: bool = True,
        format: Optional[str] = None,
        quality: Optional[int] = None
    ) -> bool:
        """
        Resize an image.
        
        Args:
            image_path (Union[str, Path]): Path to source image.
            output_path (Union[str, Path]): Path to save resized image.
            size (Tuple[int, int]): Target (width, height).
            maintain_aspect_ratio (bool): Whether to maintain aspect ratio.
            format (Optional[str]): Output format (e.g., 'JPEG', 'PNG'). 
                                   Defaults to original format.
            quality (Optional[int]): Quality level (1-100). Defaults to self.quality.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if needed for JPEG
                if img.mode in ('RGBA', 'LA', 'P'):
                    if format == 'JPEG' or (format is None and image_path.suffix.lower() == '.jpg'):
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = rgb_img
                
                # Calculate new size
                if maintain_aspect_ratio:
                    new_size = self.calculate_aspect_ratio_dimensions(img.size, size)
                else:
                    new_size = size
                
                # Resize the image
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Determine output format
                output_format = format or image_path.suffix[1:].upper()
                if output_format == 'JPG':
                    output_format = 'JPEG'
                
                # Save the image
                save_kwargs = {'format': output_format}
                if output_format in ('JPEG', 'WEBP'):
                    save_kwargs['quality'] = quality or self.quality
                    save_kwargs['optimize'] = True
                
                resized_img.save(output_path, **save_kwargs)
                return True
                
        except Exception as e:
            print(f"Error resizing image: {e}")
            return False
    
    def create_thumbnail(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
        size: Tuple[int, int] = (150, 150),
        format: Optional[str] = None
    ) -> bool:
        """
        Create a thumbnail from an image.
        
        Args:
            image_path (Union[str, Path]): Path to source image.
            output_path (Union[str, Path]): Path to save thumbnail.
            size (Tuple[int, int]): Thumbnail (width, height). Defaults to (150, 150).
            format (Optional[str]): Output format. Defaults to original format.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.resize(
            image_path,
            output_path,
            size,
            maintain_aspect_ratio=True,
            format=format,
            quality=self.THUMBNAIL_QUALITY
        )
    
    def convert_format(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
        format: str,
        quality: Optional[int] = None
    ) -> bool:
        """
        Convert an image to a different format.
        
        Args:
            image_path (Union[str, Path]): Path to source image.
            output_path (Union[str, Path]): Path to save converted image.
            format (str): Target format (e.g., 'PNG', 'WEBP', 'JPEG').
            quality (Optional[int]): Quality level for lossy formats.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with Image.open(image_path) as img:
                # Normalize format
                format = format.upper()
                if format == 'JPG':
                    format = 'JPEG'
                
                # Convert RGBA to RGB for JPEG
                if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = rgb_img
                
                # Save with appropriate settings
                save_kwargs = {'format': format}
                if format in ('JPEG', 'WEBP'):
                    save_kwargs['quality'] = quality or self.quality
                    save_kwargs['optimize'] = True
                
                img.save(output_path, **save_kwargs)
                return True
                
        except Exception as e:
            print(f"Error converting image format: {e}")
            return False
    
    @staticmethod
    def is_supported_format(file_path: Union[str, Path]) -> bool:
        """
        Check if a file is a supported image format.
        
        Args:
            file_path (Union[str, Path]): Path to the file.
            
        Returns:
            bool: True if format is supported, False otherwise.
        """
        file_path = Path(file_path)
        extension = file_path.suffix[1:].upper()
        return extension in ImageResizer.SUPPORTED_FORMATS


# Convenience functions for quick usage
def resize_image(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    size: Tuple[int, int],
    quality: int = ImageResizer.DEFAULT_QUALITY
) -> bool:
    """
    Resize an image with default settings.
    
    Args:
        image_path: Path to source image.
        output_path: Path to save resized image.
        size: Target (width, height).
        quality: Quality level (1-100).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    resizer = ImageResizer(quality=quality)
    return resizer.resize(image_path, output_path, size)


def create_thumbnail(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    size: Tuple[int, int] = (150, 150)
) -> bool:
    """
    Create a thumbnail with default settings.
    
    Args:
        image_path: Path to source image.
        output_path: Path to save thumbnail.
        size: Thumbnail (width, height).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    resizer = ImageResizer()
    return resizer.create_thumbnail(image_path, output_path, size)


def convert_image_format(
    image_path: Union[str, Path],
    output_path: Union[str, Path],
    format: str,
    quality: int = ImageResizer.DEFAULT_QUALITY
) -> bool:
    """
    Convert an image to a different format with default settings.
    
    Args:
        image_path: Path to source image.
        output_path: Path to save converted image.
        format: Target format (e.g., 'PNG', 'WEBP', 'JPEG').
        quality: Quality level (1-100).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    resizer = ImageResizer(quality=quality)
    return resizer.convert_format(image_path, output_path, format, quality)
