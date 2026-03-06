from .file_handling import FileValidator, ArchiveHandler, FileManager
from .parser import TextExtractor
from .text_cleaner import TextCleaner
from .config import GoblinConfig, OCRConfig
from .ocr_parser import OCRProcessor

__all__ = ['FileValidator', 'ArchiveHandler', 'FileManager', 
           'TextExtractor', 'TextCleaner', 'GoblinConfig', 'OCRConfig', 'OCRProcessor']
__version__ = '0.6.4'
