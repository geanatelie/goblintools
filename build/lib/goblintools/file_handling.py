import os
import shutil
import zipfile
import patoolib
from pathlib import Path
import logging
import rarfile
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileValidator:
    @staticmethod
    def is_empty(file_path: str) -> bool:
        """Check if file is empty and optionally delete it."""
        try:
            return os.path.getsize(file_path) == 0
        except (FileNotFoundError, PermissionError) as e:
            logger.info(f"Error checking file {file_path}: {e}")
            return False

    @staticmethod
    def is_archive(file_path: str) -> bool:
        """Check if file is a supported archive format."""
        return patoolib.is_archive(file_path)

class ArchiveHandler:
    _SUPPORTED_FORMATS: Dict[str, Callable] = {
        # ZIP formats
        '.zip': lambda f, d: zipfile.ZipFile(f).extractall(d),
        '.jar': lambda f, d: zipfile.ZipFile(f).extractall(d),
        '.cbz': lambda f, d: zipfile.ZipFile(f).extractall(d),
        '.war': lambda f, d: zipfile.ZipFile(f).extractall(d),
        '.ear': lambda f, d: zipfile.ZipFile(f).extractall(d),
        
        # RAR formats
        '.rar': lambda f, d: rarfile.RarFile(f).extractall(d),
        '.cbr': lambda f, d: rarfile.RarFile(f).extractall(d),
        
        # 7-Zip
        '.7z': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.cb7': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # Gzip/Bzip
        '.gz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.bz2': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.bz3': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.tbz2': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # Tar and variants
        '.tar': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.tgz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.txz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.cbt': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # ISO formats
        '.iso': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.udf': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # Package formats
        '.deb': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.rpm': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # Other common formats
        '.ace': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.cba': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.arj': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.cab': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.chm': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.cpio': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.dms': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.lha': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.lzh': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.lzma': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.lzo': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.xz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.zst': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        '.zoo': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),
        
        # Special cases
        '.adf': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),  # Amiga Disk File
        '.alz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),  # ALZip
        '.arc': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),  # ARC
        '.shn': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),  # Shorten
        '.rz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),   # Rzip
        '.lrz': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),  # LRzip
        '.a': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),    # Unix static library
        '.Z': lambda f, d: patoolib.extract_archive(f, outdir=d, verbosity=-1),    # Unix compress
    }

    @classmethod
    def add_format(cls, extension: str, handler: Callable):
        """Dynamically add support for new archive formats."""
        cls._SUPPORTED_FORMATS[extension.lower()] = handler

    @classmethod
    def extract(cls, file_path: str, destination: str) -> bool:
        """Extract any supported archive format."""
        if FileValidator.is_empty(file_path):
            return False

        try:
            ext = Path(file_path).suffix.lower()
            if ext in cls._SUPPORTED_FORMATS:
                cls._SUPPORTED_FORMATS[ext](file_path, destination)
            else:
                # Fallback to patoolib for all other formats
                patoolib.extract_archive(file_path, outdir=destination, verbosity=-1)
            
            os.remove(file_path)
            return True
        except Exception as e:
            logger.exception(f"Error extracting {file_path}: {e}")
            if os.path.exists(file_path):  # Clean up if extraction failed
                os.remove(file_path)
            return False

class FileManager:
    @staticmethod
    def delete_if_empty(file_path: str) -> bool:
        """Delete file if it's empty. Returns True if deleted or doesn't exist."""
        try:
            if os.path.getsize(file_path) == 0:
                os.remove(file_path)
                logger.info(f"Deleted empty file: {file_path}")
                return True
            return False
        except FileNotFoundError:
            return True
        except PermissionError:
            logger.warning(f"Permission denied deleting {file_path}")
            return False
        except Exception as e:
            logger.error(f"Error checking/deleting {file_path}: {e}")
            return False

    @staticmethod
    def delete_folder(folder_path: str) -> bool:
        """Recursively delete a folder and its contents."""
        try:
            if not os.path.exists(folder_path):
                logger.info(f"Folder not found: {folder_path}")
                return False
            shutil.rmtree(folder_path)
            return True
        except PermissionError as e:
            logger.error(f"Permission denied deleting {folder_path}: {e}")
        except Exception as e:
            logger.error(f"Error deleting {folder_path}: {e}")
        return False

    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        """Move a single file with proper error handling."""
        try:
            if FileValidator.is_empty(source):
                return False

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            
            # Handle name conflicts
            counter = 1
            base, ext = os.path.splitext(destination)
            while os.path.exists(destination):
                destination = f"{base}_{counter}{ext}"
                counter += 1

            shutil.move(source, destination)
            return True
        except Exception as e:
            logger.error(f"Error moving {source} to {destination}: {e}")
            return False

    @classmethod
    def move_files(cls, folder_path: str) -> None:
        """Organize files in a directory structure."""
        if not os.path.exists(folder_path):
            logger.error(f"Directory not found: {folder_path}")
            return

        for root, _, files in os.walk(folder_path):
            for file in files:
                source_path = os.path.join(root, file)
                if cls.delete_if_empty(source_path):
                    continue

                # Normalize filename
                file_ext = Path(file).suffix.lower()
                dest_path = os.path.join(folder_path, f"{Path(file).stem}{file_ext}")
                
                cls.move_file(source_path, dest_path)

            # Remove empty directories
            try:
                if not os.listdir(root):
                    os.rmdir(root)
            except Exception as e:
                logger.error(f"Error removing directory {root}: {e}")

    @classmethod
    def extract_files_recursive(cls, file_path: str, destination: str) -> bool:
        """Recursively extract nested archives."""
        if not os.path.exists(file_path):
            return False

        if not FileValidator.is_archive(file_path):
            return False

        if not ArchiveHandler.extract(file_path, destination):
            return False

        # Process extracted files
        for root, _, files in os.walk(destination):
            for file in files:
                source = os.path.join(root, file)
                if FileValidator.is_archive(source):
                    cls.extract_files_recursive(source, root)
        return True

    @classmethod
    def batch_extract(cls, file_paths: List[str], destination: str) -> List[bool]:
        """Process multiple archives in parallel."""
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(
                lambda path: cls.extract_files_recursive(path, destination),
                file_paths
            ))
        return results
