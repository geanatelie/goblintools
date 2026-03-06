#!/usr/bin/env python3
"""
Simple local test script: reads a .zip or document from the project root,
extracts (if archive) or copies (if document), parses the contents, and prints.
File paths in output are shown as path inside the zip (e.g. folder/doc.pdf).
"""
import argparse
import shutil
import sys
from pathlib import Path

from goblintools import FileManager, TextExtractor, FileValidator


def _find_input(root: Path) -> Path | None:
    """Find first .zip or parseable document in project root."""
    for z in root.glob("*.zip"):
        return z
    for ext in FileValidator.PARSEABLE_EXTENSIONS:
        for f in root.glob(f"*{ext}"):
            return f
    return None


def main():
    root = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Extract and parse a zip or document from the project root"
    )
    parser.add_argument(
        "input_path",
        nargs="?",
        default=None,
        help="Path to .zip or document (default: first .zip or doc found in project root)",
    )
    args = parser.parse_args()

    if args.input_path:
        input_path = Path(args.input_path)
    else:
        input_path = _find_input(root)
        if not input_path:
            print(
                "No .zip or supported document found in project root. "
                "Place one there or pass a path.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Using: {input_path}")

    if not input_path.exists():
        print(f"File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    extract_dir = root / f"{input_path.stem}_extracted"
    extract_dir.mkdir(exist_ok=True)

    # For archives, copy first so extraction doesn't delete the original
    if FileValidator.is_archive(str(input_path)):
        copy_path = extract_dir / input_path.name
        shutil.copy2(input_path, copy_path)
        work_path = copy_path
    else:
        work_path = input_path

    try:
        if not FileManager.extract_files_recursive(str(work_path), str(extract_dir)):
            print(
                "File is neither a supported archive nor a parseable document.",
                file=sys.stderr,
            )
            sys.exit(1)

        extractor = TextExtractor()
        content = extractor.extract_from_folder(str(extract_dir))

        # Rewrite paths to be path inside zip only (e.g. folder/doc.pdf)
        if content:
            extract_root = str(Path(extract_dir).resolve()) + "/"
            content = content.replace(extract_root, "")
            content = content.replace(str(Path(extract_dir).resolve()) + "\\", "")

        if content:
            print(content)
        else:
            print("No parseable text content found in the archive.")
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
