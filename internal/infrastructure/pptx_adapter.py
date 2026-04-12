"""python-pptx adapter — wraps PPTX operations for linting and fixing."""

from __future__ import annotations

import logging
from typing import Any

from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

logger = logging.getLogger(__name__)

# Map alignment string names to PP_ALIGN enum
ALIGNMENT_MAP: dict[str, PP_ALIGN] = {
    "left": PP_ALIGN.LEFT,
    "center": PP_ALIGN.CENTER,
    "right": PP_ALIGN.RIGHT,
    "justify": PP_ALIGN.JUSTIFY,
}


def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert a hex color string like '#1F2D3D' to RGBColor."""
    h = hex_str.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def rgb_to_hex(rgb: RGBColor) -> str:
    """Convert RGBColor to hex string."""
    return f"#{rgb}"


def rgb_to_hex_safe(color_obj: Any) -> str | None:
    """Safely extract hex string from a color object."""
    try:
        if color_obj is None:
            return None
        rgb = color_obj.rgb
        return f"#{rgb}"
    except (AttributeError, TypeError):
        return None


def get_text_runs(slide: Any) -> list[dict[str, Any]]:
    """Extract all text runs with their formatting from a slide.

    Returns list of dicts with keys:
        shape_index, shape_name, text_frame_index, para_index, run_index,
        text, font_name, font_size_pt, bold, color_hex
    """
    runs = []
    for si, shape in enumerate(slide.shapes):
        if not shape.has_text_frame:
            continue
        for tfi, text_frame in enumerate(  # noqa: F841
            shape.text_frame.paragraphs,
        ):
            # Re-iterate properly
            pass

    # Redo properly
    for si, shape in enumerate(slide.shapes):
        if not shape.has_text_frame:
            continue
        text_frame = shape.text_frame
        for pi, para in enumerate(text_frame.paragraphs):
            for ri, run in enumerate(para.runs):
                font = run.font
                color_hex = rgb_to_hex_safe(font.color)
                runs.append({
                    "shape_index": si,
                    "shape_name": shape.name,
                    "text_frame_index": 0,
                    "para_index": pi,
                    "run_index": ri,
                    "text": run.text,
                    "font_name": font.name,
                    "font_size_pt": _emu_to_pt(font.size) if font.size else None,
                    "bold": font.bold,
                    "color_hex": color_hex,
                    "paragraph_alignment": _align_to_str(para.alignment),
                    "shape_left": shape.left,
                    "shape_top": shape.top,
                    "shape_width": shape.width,
                    "shape_height": shape.height,
                    "line_spacing": para.line_spacing,
                })
    return runs


def get_shapes_with_fill(slide: Any) -> list[dict[str, Any]]:
    """Get all shapes with background fill colors."""
    shapes = []
    for si, shape in enumerate(slide.shapes):
        fill_color = None
        try:
            if shape.fill.type is not None:
                fill_color = rgb_to_hex_safe(shape.fill.fore_color)
        except Exception:
            pass
        if fill_color:
            shapes.append({
                "shape_index": si,
                "shape_name": shape.name,
                "fill_color": fill_color,
                "shape_type": str(shape.shape_type),
            })
    return shapes


def get_slide_number_shapes(slide: Any) -> list[dict[str, Any]]:
    """Detect shapes that likely represent slide numbers."""
    candidates = []
    # Get slide width for position heuristics
    try:
        _sw = (
            slide.slide_layout.slide_master.slide_width
            if slide.slide_layout and hasattr(slide.slide_layout.slide_master, "slide_width")
            else Emu(9144000)
        )
    except AttributeError:
        _sw = Emu(9144000)
    for si, shape in enumerate(slide.shapes):
        if not shape.has_text_frame:
            continue
        text = shape.text_frame.text.strip()
        # Slide number detection: numeric text in bottom area
        if text.isdigit() or text == str(slide.slide_id):
            candidates.append({
                "shape_index": si,
                "shape_name": shape.name,
                "text": text,
                "left": shape.left,
                "top": shape.top,
                "width": shape.width,
                "height": shape.height,
                "font_size_pt": _emu_to_pt(shape.text_frame.paragraphs[0].runs[0].font.size)
                if shape.text_frame.paragraphs and shape.text_frame.paragraphs[0].runs
                else None,
            })
    return candidates


def get_chart_shapes(slide: Any) -> list[dict[str, Any]]:
    """Get all chart shapes on a slide."""
    charts = []
    for si, shape in enumerate(slide.shapes):
        if shape.has_chart:
            chart = shape.chart
            has_title = (
                chart.has_title
                and chart.chart_title.has_text_frame
                and chart.chart_title.text_frame.text.strip()
            )
            charts.append({
                "shape_index": si,
                "shape_name": shape.name,
                "has_title": bool(has_title),
                "title_text": chart.chart_title.text_frame.text if has_title else None,
                "chart_type": str(chart.chart_type) if hasattr(chart, "chart_type") else "unknown",
            })
    return charts


def classify_text_role(shape: Any, slide: Any) -> str:
    """Classify a text shape as title, body, caption, or other.

    Heuristic: uses shape name, position, and size.
    """
    name = shape.name.lower()
    # Title placeholders
    if "title" in name and "subtitle" not in name:
        return "title"
    if "subtitle" in name:
        return "body"
    # Check if it's a placeholder
    if hasattr(shape, "is_placeholder") and shape.is_placeholder:
        ph_idx = getattr(shape, "placeholder_format", None)
        if ph_idx and hasattr(ph_idx, "idx"):
            # Index 0 = title, 1 = body/subtitle
            if ph_idx.idx == 0:
                return "title"
            return "body"
    # Size heuristic: large text near top = title
    if hasattr(shape, "top") and shape.top is not None:
        if shape.top < Emu(1143000):  # < ~1 inch from top
            return "title"
    # Small font = caption
    if shape.has_text_frame and shape.text_frame.paragraphs:
        first_para = shape.text_frame.paragraphs[0]
        if first_para.runs:
            font_size = (
                _emu_to_pt(first_para.runs[0].font.size)
                if first_para.runs[0].font.size
                else None
            )
            if font_size and font_size <= 11:
                return "caption"
    return "body"


def apply_font_fix(run: Any, family: str | None = None, size_pt: float | None = None,
                   bold: bool | None = None, color: str | None = None) -> None:
    """Apply font fixes to a run."""
    font = run.font
    if family:
        font.name = family
    if size_pt is not None:
        font.size = Pt(size_pt)
    if bold is not None:
        font.bold = bold
    if color:
        font.color.rgb = hex_to_rgb(color)


def apply_alignment_fix(para: Any, alignment: str) -> None:
    """Apply alignment fix to a paragraph."""
    if alignment in ALIGNMENT_MAP:
        para.alignment = ALIGNMENT_MAP[alignment]


def apply_line_spacing_fix(para: Any, line_spacing: float) -> None:
    """Apply line spacing fix to a paragraph."""
    para.line_spacing = Pt(line_spacing) if line_spacing else None


def _emu_to_pt(emu: Any) -> float | None:
    """Convert EMU to points."""
    if emu is None:
        return None
    try:
        return float(emu) / 12700
    except (TypeError, ValueError):
        return None


def _align_to_str(align: Any) -> str | None:
    """Convert PP_ALIGN enum to string."""
    if align is None:
        return None
    mapping = {v: k for k, v in ALIGNMENT_MAP.items()}
    return mapping.get(align)


def _align_to_enum(align_str: str | None) -> PP_ALIGN | None:
    """Convert string to PP_ALIGN enum."""
    if align_str is None:
        return None
    return ALIGNMENT_MAP.get(align_str)
