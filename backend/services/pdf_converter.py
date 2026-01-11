"""
PDF Conversion Service Module

This module provides functionality for converting various file formats to PDF
and performing PDF-related operations like merging, splitting, and compression.

Author: JK-Tools-hub Team
Date: 2026-01-11
"""

import os
import logging
from typing import Optional, List, Tuple
from pathlib import Path
import io

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
except ImportError:
    raise ImportError("reportlab is required. Install it using: pip install reportlab")

try:
    from PyPDF2 import PdfMerger, PdfReader, PdfWriter
except ImportError:
    raise ImportError("PyPDF2 is required. Install it using: pip install PyPDF2")

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow is required. Install it using: pip install Pillow")

# Configure logging
logger = logging.getLogger(__name__)


class PDFConverterError(Exception):
    """Custom exception for PDF conversion errors."""
    pass


class PDFConverter:
    """
    A comprehensive PDF conversion service that handles various file formats
    and PDF operations.
    """

    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Supported document formats (would require additional libraries for full support)
    SUPPORTED_DOCUMENT_FORMATS = {'.txt', '.md'}

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the PDF Converter.

        Args:
            temp_dir (Optional[str]): Temporary directory for processing files.
                                     Defaults to system temp directory.
        """
        self.temp_dir = temp_dir or "./temp"
        self._ensure_temp_dir()
        logger.info(f"PDFConverter initialized with temp_dir: {self.temp_dir}")

    def _ensure_temp_dir(self) -> None:
        """Ensure temporary directory exists."""
        os.makedirs(self.temp_dir, exist_ok=True)

    def images_to_pdf(
        self,
        image_paths: List[str],
        output_path: str,
        page_size: Tuple[float, float] = letter,
        margin: int = 10
    ) -> bool:
        """
        Convert a list of images to a single PDF file.

        Args:
            image_paths (List[str]): List of paths to image files.
            output_path (str): Path where the PDF will be saved.
            page_size (Tuple[float, float]): PDF page size (default: letter).
            margin (int): Margin in points (default: 10).

        Returns:
            bool: True if conversion successful, False otherwise.

        Raises:
            PDFConverterError: If conversion fails.
        """
        try:
            if not image_paths:
                raise PDFConverterError("No image paths provided")

            # Validate image files
            valid_images = []
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    logger.warning(f"Image not found: {img_path}")
                    continue
                
                ext = Path(img_path).suffix.lower()
                if ext not in self.SUPPORTED_IMAGE_FORMATS:
                    logger.warning(f"Unsupported image format: {ext}")
                    continue
                
                valid_images.append(img_path)

            if not valid_images:
                raise PDFConverterError("No valid images found to convert")

            # Create PDF
            c = canvas.Canvas(output_path, pagesize=page_size)
            page_width, page_height = page_size

            for img_path in valid_images:
                try:
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    
                    # Calculate dimensions to fit on page with margin
                    available_width = page_width - (2 * margin)
                    available_height = page_height - (2 * margin)
                    
                    # Scale image to fit
                    aspect_ratio = img_width / img_height
                    if available_width / available_height < aspect_ratio:
                        new_width = available_width
                        new_height = available_width / aspect_ratio
                    else:
                        new_height = available_height
                        new_width = available_height * aspect_ratio
                    
                    # Center image on page
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2
                    
                    # Draw image
                    img_reader = ImageReader(img_path)
                    c.drawImage(img_reader, x, y, width=new_width, height=new_height)
                    c.showPage()
                    
                except Exception as e:
                    logger.error(f"Error processing image {img_path}: {str(e)}")
                    raise PDFConverterError(f"Failed to process image: {img_path}")

            c.save()
            logger.info(f"Successfully created PDF: {output_path}")
            return True

        except PDFConverterError as e:
            logger.error(f"PDF conversion error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during image to PDF conversion: {str(e)}")
            raise PDFConverterError(f"Unexpected error: {str(e)}")

    def text_to_pdf(
        self,
        text_content: str,
        output_path: str,
        page_size: Tuple[float, float] = letter,
        font_name: str = "Helvetica",
        font_size: int = 12
    ) -> bool:
        """
        Convert text content to PDF.

        Args:
            text_content (str): Text content to convert.
            output_path (str): Path where the PDF will be saved.
            page_size (Tuple[float, float]): PDF page size (default: letter).
            font_name (str): Font name (default: Helvetica).
            font_size (int): Font size in points (default: 12).

        Returns:
            bool: True if conversion successful, False otherwise.

        Raises:
            PDFConverterError: If conversion fails.
        """
        try:
            if not text_content:
                raise PDFConverterError("No text content provided")

            c = canvas.Canvas(output_path, pagesize=page_size)
            page_width, page_height = page_size
            margin = 40
            y_position = page_height - margin

            c.setFont(font_name, font_size)
            
            # Split text into lines and handle page breaks
            lines = text_content.split('\n')
            line_height = font_size + 4

            for line in lines:
                if y_position < margin:
                    c.showPage()
                    y_position = page_height - margin

                c.drawString(margin, y_position, line)
                y_position -= line_height

            c.save()
            logger.info(f"Successfully created PDF from text: {output_path}")
            return True

        except PDFConverterError as e:
            logger.error(f"PDF conversion error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text to PDF conversion: {str(e)}")
            raise PDFConverterError(f"Unexpected error: {str(e)}")

    def merge_pdfs(
        self,
        pdf_paths: List[str],
        output_path: str
    ) -> bool:
        """
        Merge multiple PDF files into a single PDF.

        Args:
            pdf_paths (List[str]): List of paths to PDF files to merge.
            output_path (str): Path where the merged PDF will be saved.

        Returns:
            bool: True if merge successful, False otherwise.

        Raises:
            PDFConverterError: If merge fails.
        """
        try:
            if not pdf_paths:
                raise PDFConverterError("No PDF paths provided")

            merger = PdfMerger()

            for pdf_path in pdf_paths:
                if not os.path.exists(pdf_path):
                    logger.warning(f"PDF not found: {pdf_path}")
                    continue
                
                try:
                    merger.append(pdf_path)
                except Exception as e:
                    logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
                    raise PDFConverterError(f"Failed to process PDF: {pdf_path}")

            merger.write(output_path)
            merger.close()
            logger.info(f"Successfully merged PDFs: {output_path}")
            return True

        except PDFConverterError as e:
            logger.error(f"PDF merge error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during PDF merge: {str(e)}")
            raise PDFConverterError(f"Unexpected error: {str(e)}")

    def split_pdf(
        self,
        input_path: str,
        output_dir: str,
        pages: Optional[List[int]] = None
    ) -> List[str]:
        """
        Split a PDF into separate pages or extract specific pages.

        Args:
            input_path (str): Path to the input PDF file.
            output_dir (str): Directory where split PDFs will be saved.
            pages (Optional[List[int]]): Specific page numbers to extract (1-indexed).
                                        If None, splits all pages.

        Returns:
            List[str]: List of paths to created PDF files.

        Raises:
            PDFConverterError: If split fails.
        """
        try:
            if not os.path.exists(input_path):
                raise PDFConverterError(f"Input PDF not found: {input_path}")

            os.makedirs(output_dir, exist_ok=True)

            reader = PdfReader(input_path)
            total_pages = len(reader.pages)

            if pages is None:
                pages = list(range(1, total_pages + 1))

            # Validate page numbers
            pages = [p for p in pages if 1 <= p <= total_pages]
            if not pages:
                raise PDFConverterError("No valid pages specified")

            created_files = []

            for page_num in pages:
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num - 1])
                
                output_path = os.path.join(
                    output_dir,
                    f"page_{page_num:04d}.pdf"
                )
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                created_files.append(output_path)
                logger.info(f"Created split PDF: {output_path}")

            return created_files

        except PDFConverterError as e:
            logger.error(f"PDF split error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during PDF split: {str(e)}")
            raise PDFConverterError(f"Unexpected error: {str(e)}")

    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Extract metadata and information from a PDF file.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            dict: Dictionary containing PDF information including page count,
                  metadata, and other properties.

        Raises:
            PDFConverterError: If extraction fails.
        """
        try:
            if not os.path.exists(pdf_path):
                raise PDFConverterError(f"PDF file not found: {pdf_path}")

            reader = PdfReader(pdf_path)
            
            info = {
                'page_count': len(reader.pages),
                'metadata': reader.metadata,
                'file_size': os.path.getsize(pdf_path),
                'file_path': pdf_path
            }

            logger.info(f"Extracted PDF info from: {pdf_path}")
            return info

        except PDFConverterError as e:
            logger.error(f"PDF info extraction error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during PDF info extraction: {str(e)}")
            raise PDFConverterError(f"Unexpected error: {str(e)}")

    def cleanup(self) -> None:
        """Clean up temporary files."""
        try:
            if os.path.exists(self.temp_dir):
                for file in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")


# Export main class
__all__ = ['PDFConverter', 'PDFConverterError']
