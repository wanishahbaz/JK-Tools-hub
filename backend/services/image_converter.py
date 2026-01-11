"""
Image Format Conversion Service

This module provides functionality to convert images between various formats,
including common formats like JPEG, PNG, WebP, BMP, GIF, and TIFF.

Dependencies:
    - PIL (Pillow): For image processing and format conversion
    - logging: For service logging and debugging

Author: JK-Tools-hub
Date: 2026-01-11
"""

import logging
import os
from typing import Optional, Tuple
from PIL import Image
from io import BytesIO


# Configure logging
logger = logging.getLogger(__name__)


class ImageConverter:
    """
    A service class for converting images between different formats.
    
    Supported formats:
        - JPEG (.jpg, .jpeg)
        - PNG (.png)
        - WebP (.webp)
        - BMP (.bmp)
        - GIF (.gif)
        - TIFF (.tiff, .tif)
    """
    
    SUPPORTED_FORMATS = ['JPEG', 'PNG', 'WEBP', 'BMP', 'GIF', 'TIFF']
    FORMAT_EXTENSIONS = {
        'JPEG': '.jpg',
        'PNG': '.png',
        'WEBP': '.webp',
        'BMP': '.bmp',
        'GIF': '.gif',
        'TIFF': '.tiff'
    }
    
    @staticmethod
    def convert_image(
        input_path: str,
        output_path: str,
        output_format: str,
        quality: int = 85,
        resize: Optional[Tuple[int, int]] = None,
        optimize: bool = True
    ) -> bool:
        """
        Convert an image from one format to another.
        
        Args:
            input_path (str): Path to the input image file
            output_path (str): Path where the converted image will be saved
            output_format (str): Target format (e.g., 'JPEG', 'PNG', 'WEBP')
            quality (int): Output quality (1-100), default is 85. Only applies to JPEG and WEBP
            resize (Optional[Tuple[int, int]]): Tuple of (width, height) to resize the image
            optimize (bool): Whether to optimize the output file size, default is True
            
        Returns:
            bool: True if conversion successful, False otherwise
            
        Raises:
            ValueError: If the output format is not supported
            FileNotFoundError: If the input file does not exist
        """
        try:
            # Validate output format
            output_format = output_format.upper()
            if output_format not in ImageConverter.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported format: {output_format}. "
                    f"Supported formats: {', '.join(ImageConverter.SUPPORTED_FORMATS)}"
                )
            
            # Check if input file exists
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Open the image
            with Image.open(input_path) as img:
                logger.info(f"Opened image: {input_path} (Format: {img.format}, Size: {img.size})")
                
                # Convert RGBA to RGB if converting to JPEG
                if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = rgb_img
                    logger.info("Converted image mode to RGB for JPEG compatibility")
                
                # Resize image if specified
                if resize:
                    img = img.resize(resize, Image.Resampling.LANCZOS)
                    logger.info(f"Resized image to {resize}")
                
                # Prepare output directory
                output_dir = os.path.dirname(output_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    logger.info(f"Created output directory: {output_dir}")
                
                # Save with format-specific parameters
                save_kwargs = {'format': output_format}
                
                if output_format in ['JPEG', 'WEBP']:
                    save_kwargs['quality'] = max(1, min(100, quality))
                    save_kwargs['optimize'] = optimize
                elif output_format == 'PNG':
                    save_kwargs['optimize'] = optimize
                elif output_format == 'GIF':
                    # GIF doesn't support quality parameter
                    pass
                
                img.save(output_path, **save_kwargs)
                logger.info(f"Successfully converted and saved image to: {output_path}")
                
                return True
                
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid format: {e}")
            raise
        except Exception as e:
            logger.error(f"Error converting image: {e}")
            return False
    
    @staticmethod
    def convert_image_bytes(
        input_bytes: bytes,
        input_format: Optional[str],
        output_format: str,
        quality: int = 85,
        resize: Optional[Tuple[int, int]] = None,
        optimize: bool = True
    ) -> Optional[bytes]:
        """
        Convert image bytes from one format to another.
        
        Args:
            input_bytes (bytes): Input image as bytes
            input_format (Optional[str]): Input format (can be None, will be auto-detected)
            output_format (str): Target format (e.g., 'JPEG', 'PNG', 'WEBP')
            quality (int): Output quality (1-100), default is 85
            resize (Optional[Tuple[int, int]]): Tuple of (width, height) to resize the image
            optimize (bool): Whether to optimize the output file size, default is True
            
        Returns:
            Optional[bytes]: Converted image as bytes, or None if conversion failed
        """
        try:
            output_format = output_format.upper()
            
            if output_format not in ImageConverter.SUPPORTED_FORMATS:
                raise ValueError(
                    f"Unsupported format: {output_format}. "
                    f"Supported formats: {', '.join(ImageConverter.SUPPORTED_FORMATS)}"
                )
            
            # Open image from bytes
            img = Image.open(BytesIO(input_bytes))
            logger.info(f"Opened image from bytes (Format: {img.format}, Size: {img.size})")
            
            # Convert RGBA to RGB if converting to JPEG
            if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = rgb_img
                logger.info("Converted image mode to RGB for JPEG compatibility")
            
            # Resize if specified
            if resize:
                img = img.resize(resize, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {resize}")
            
            # Save to bytes buffer
            output_buffer = BytesIO()
            save_kwargs = {'format': output_format}
            
            if output_format in ['JPEG', 'WEBP']:
                save_kwargs['quality'] = max(1, min(100, quality))
                save_kwargs['optimize'] = optimize
            elif output_format == 'PNG':
                save_kwargs['optimize'] = optimize
            
            img.save(output_buffer, **save_kwargs)
            output_buffer.seek(0)
            result = output_buffer.getvalue()
            
            logger.info(f"Successfully converted image to {output_format}")
            return result
            
        except Exception as e:
            logger.error(f"Error converting image bytes: {e}")
            return None
    
    @staticmethod
    def get_image_info(image_path: str) -> Optional[dict]:
        """
        Get information about an image file.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            Optional[dict]: Dictionary containing image information or None if error
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            with Image.open(image_path) as img:
                file_size = os.path.getsize(image_path)
                info = {
                    'format': img.format,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'file_size_bytes': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'dpi': img.info.get('dpi', None),
                    'is_animated': getattr(img, 'is_animated', False)
                }
                logger.info(f"Retrieved image info for: {image_path}")
                return info
                
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting image info: {e}")
            return None
    
    @staticmethod
    def batch_convert(
        input_directory: str,
        output_directory: str,
        output_format: str,
        quality: int = 85,
        file_pattern: str = "*"
    ) -> Tuple[int, int]:
        """
        Batch convert all images in a directory to a specified format.
        
        Args:
            input_directory (str): Directory containing images to convert
            output_directory (str): Directory where converted images will be saved
            output_format (str): Target format for all images
            quality (int): Output quality for JPEG/WEBP, default is 85
            file_pattern (str): File pattern to match (e.g., "*.jpg"), default is "*"
            
        Returns:
            Tuple[int, int]: (successful_conversions, failed_conversions)
        """
        try:
            output_format = output_format.upper()
            
            if output_format not in ImageConverter.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {output_format}")
            
            if not os.path.exists(input_directory):
                raise FileNotFoundError(f"Input directory not found: {input_directory}")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_directory, exist_ok=True)
            
            successful = 0
            failed = 0
            
            # Get list of image files
            import glob
            pattern = os.path.join(input_directory, file_pattern)
            image_files = glob.glob(pattern)
            
            logger.info(f"Found {len(image_files)} files matching pattern '{file_pattern}' in {input_directory}")
            
            for input_file in image_files:
                if not os.path.isfile(input_file):
                    continue
                
                try:
                    # Generate output filename
                    base_name = os.path.splitext(os.path.basename(input_file))[0]
                    output_file = os.path.join(
                        output_directory,
                        f"{base_name}{ImageConverter.FORMAT_EXTENSIONS[output_format]}"
                    )
                    
                    # Convert image
                    if ImageConverter.convert_image(input_file, output_file, output_format, quality):
                        successful += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to convert {input_file}: {e}")
                    failed += 1
            
            logger.info(f"Batch conversion complete: {successful} successful, {failed} failed")
            return (successful, failed)
            
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Batch conversion error: {e}")
            raise
    
    @staticmethod
    def get_supported_formats() -> list:
        """
        Get list of supported image formats.
        
        Returns:
            list: List of supported format strings
        """
        return ImageConverter.SUPPORTED_FORMATS.copy()


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Image Converter Service")
    print(f"Supported formats: {ImageConverter.get_supported_formats()}")
