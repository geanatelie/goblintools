#!/usr/bin/env python3
"""
Dev helper: extract an archive, then recursively extract nested archives inside.

Pass the archive path as the first argument (relative or absolute). If ``--out`` is
omitted, files go under ``dev_extract/<archive_stem>/`` at the project root.

Usage:
  python scripts/dev_extract_nested.py edital.zip
  python scripts/dev_extract_nested.py /path/to/other.zip --out /tmp/out
  python scripts/dev_extract_nested.py edital.zip --skip-text
  python scripts/dev_extract_nested.py edital.zip --ocr
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from goblintools.file_handling import FileManager
from goblintools import TextExtractor


def _default_out_for_archive(archive: Path) -> Path:
    return PROJECT_ROOT / "dev_extract" / archive.resolve().stem


def _print_tree(root: Path, max_files: int = 200) -> None:
    root = root.resolve()
    print(f"\nExtracted files under {root}:\n")
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        rel = Path(dirpath).relative_to(root)
        depth = len(rel.parts) if rel != Path(".") else 0
        indent = "  " * depth
        name = "." if rel == Path(".") else rel.name
        print(f"{indent}{name}/")
        for f in filenames:
            if count >= max_files:
                print(f"{indent}  ... ({max_files}+ files, listing truncated)")
                return
            print(f"{indent}  {f}")
            count += 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract a zip (or other archive) and nested archives for local testing."
    )
    parser.add_argument(
        "archive",
        type=Path,
        help="path to the archive (.zip, .rar, etc.)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        metavar="DIR",
        help="destination directory (default: dev_extract/<name_without_suffix>/ under project root)",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="after extraction, run FileManager.move_files (same as production flatten step)",
    )
    parser.add_argument(
        "--skip-text",
        action="store_true",
        help="do not run TextExtractor.extract_from_folder on the output directory",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="pass ocr_handler=True to TextExtractor (scanned PDFs)",
    )
    args = parser.parse_args()

    archive = args.archive.expanduser().resolve()
    if args.out is not None:
        out = args.out.expanduser().resolve()
    else:
        out = _default_out_for_archive(archive)

    if not archive.is_file():
        print(f"Archive not found: {archive}", file=sys.stderr)
        return 1

    out.mkdir(parents=True, exist_ok=True)

    fm = FileManager(suppress_warnings=True)
    ok = fm.extract_files_recursive(str(archive), str(out))
    if not ok:
        print(f"extract_files_recursive failed for {archive}", file=sys.stderr)
        return 2

    if args.flatten:
        fm.move_files(str(out))

    _print_tree(out)
    print(f"\nDone. Root output: {out}")

    if not args.skip_text:
        extractor = TextExtractor(
            ocr_handler=args.ocr,
            suppress_warnings=True,
        )
        text = extractor.extract_from_folder(str(out))
        print("\n" + "=" * 72)
        print("TextExtractor.extract_from_folder() return value (full string):")
        print("=" * 72 + "\n")
        if text:
            print(text)
        else:
            print("(empty string — no file_path_pwd blocks, e.g. no parseable text)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
