"""
Runtime fixes for pypdf text extraction on PDFs that store font metrics as
indirect references (valid per PDF spec, not always resolved in pypdf).

Also relaxes the array-based stream output cap when the current pypdf
exposes ``MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH`` on ``pypdf.filters`` (not
all versions do).

Apply once before PdfReader/Page.extract_text via :func:`apply_pypdf_extraction_workarounds`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Union

_applied = False


def _as_float(value: Any, fallback: float = 500.0) -> float:
    try:
        from pypdf.generic import IndirectObject
    except ImportError:  # pragma: no cover
        return float(value)
    if isinstance(value, IndirectObject):
        value = value.get_object()
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def apply_pypdf_extraction_workarounds() -> None:
    """Idempotent monkey-patches for pypdf; safe to call multiple times."""
    global _applied
    if _applied:
        return

    import pypdf._font as pypdf_font
    import pypdf._text_extraction._text_extractor as te
    import pypdf.filters as pypdf_filters
    from pypdf._font import Font, FontDescriptor
    from pypdf.generic import DictionaryObject, TextStringObject

    # Not every pypdf release exposes this on pypdf.filters (AttributeError-safe).
    _stream_cap = getattr(
        pypdf_filters, "MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH", None
    )
    if _stream_cap is not None:
        pypdf_filters.MAX_ARRAY_BASED_STREAM_OUTPUT_LENGTH = max(
            int(_stream_cap), 120_000_000
        )

    def text_width(self: Any, text: str = "") -> float:
        return sum(
            _as_float(self.character_widths.get(ch, self.character_widths["default"]))
            for ch in text
        )

    pypdf_font.Font.text_width = text_width  # type: ignore[method-assign]

    import pypdf._text_extraction as pypdf_te

    def get_display_str(
        text: str,
        cm_matrix: list[float],
        tm_matrix: list[float],
        font_resource: Optional[DictionaryObject],
        font: Font,
        text_operands: str,
        font_size: float,
        rtl_dir: bool,
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
    ) -> tuple[str, bool, float]:
        """Copy of pypdf.get_display_str with indirect ``font.space_width`` resolved."""
        from pypdf._text_extraction import (
            CUSTOM_RTL_MAX,
            CUSTOM_RTL_MIN,
            CUSTOM_RTL_SPECIAL_CHARS,
        )

        widths: float = 0.0
        for x in [font.character_map.get(x, x) for x in text_operands]:
            if len(x) == 1:
                xx = ord(x)
            else:
                xx = 1
            if (
                (xx <= 0x2F)
                or 0x3A <= xx <= 0x40
                or 0x2000 <= xx <= 0x206F
                or 0x20A0 <= xx <= 0x21FF
                or xx in CUSTOM_RTL_SPECIAL_CHARS
            ):
                text = x + text if rtl_dir else text + x
            elif (
                0x0590 <= xx <= 0x08FF
                or 0xFB1D <= xx <= 0xFDFF
                or 0xFE70 <= xx <= 0xFEFF
                or CUSTOM_RTL_MIN <= xx <= CUSTOM_RTL_MAX
            ):
                if not rtl_dir:
                    rtl_dir = True
                    if visitor_text is not None:
                        visitor_text(
                            text, cm_matrix, tm_matrix, font_resource, font_size
                        )
                    text = ""
                text = x + text
            else:
                if rtl_dir:
                    rtl_dir = False
                    if visitor_text is not None:
                        visitor_text(
                            text, cm_matrix, tm_matrix, font_resource, font_size
                        )
                    text = ""
                text = text + x
            sw = _as_float(font.space_width, 250.0)
            widths += sw if x == " " else font.text_width(x)
        return text, rtl_dir, widths

    pypdf_te.get_display_str = get_display_str  # type: ignore[assignment]

    def _handle_tf(self: Any, operands: list[Any]) -> None:
        if self.text != "":
            self.output += self.text
            if self.visitor_text is not None:
                self.visitor_text(
                    self.text,
                    self.memo_cm,
                    self.memo_tm,
                    self.font_resource,
                    self.font_size,
                )
        self.text = ""
        self.memo_cm = self.cm_matrix.copy()
        self.memo_tm = self.tm_matrix.copy()
        try:
            self.font_resource = self.font_resources[operands[0]]
            self.font = self.fonts[operands[0]]
        except KeyError:
            self.font_resource = None
            font_descriptor = FontDescriptor()
            self.font = Font(
                "Unknown",
                space_width=250,
                encoding=dict.fromkeys(range(256), "\ufffd"),
                font_descriptor=font_descriptor,
                character_map={},
            )  # same fallback shape as pypdf TextExtraction._handle_tf

        self._space_width = _as_float(self.font.space_width, 250.0) / 2
        try:
            self.font_size = float(operands[1])
        except Exception:
            pass

    te.TextExtraction._handle_tf = _handle_tf  # type: ignore[method-assign]

    def _handle_tj(
        self: Any,
        text: str,
        operands: list[Union[str, TextStringObject]],
        cm_matrix: list[float],
        tm_matrix: list[float],
        font_resource: Optional[DictionaryObject],
        font: Font,
        orientations: tuple[int, ...],
        font_size: float,
        rtl_dir: bool,
        visitor_text: Optional[Callable[[Any, Any, Any, Any, Any], None]],
        actual_str_size: dict[str, float],
    ) -> tuple[str, bool, dict[str, float]]:
        from pypdf._text_extraction import get_display_str, get_text_operands

        text_operands, is_str_operands = get_text_operands(
            operands, cm_matrix, tm_matrix, font, orientations
        )
        if is_str_operands:
            text += text_operands
            sw = _as_float(font.space_width, 250.0)
            font_widths = sum(
                sw if x == " " else font.text_width(x) for x in text_operands
            )
        else:
            text, rtl_dir, font_widths = get_display_str(
                text,
                cm_matrix,
                tm_matrix,
                font_resource,
                font,
                text_operands,
                font_size,
                rtl_dir,
                visitor_text,
            )
        actual_str_size["str_widths"] += font_widths * font_size
        actual_str_size["str_height"] = font_size
        return text, rtl_dir, actual_str_size

    te.TextExtraction._handle_tj = _handle_tj  # type: ignore[method-assign]

    _applied = True
