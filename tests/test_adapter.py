"""Tests for the pptx_adapter module."""

from pptx.dml.color import RGBColor

from internal.infrastructure.pptx_adapter import (
    _emu_to_pt,
    hex_to_rgb,
    rgb_to_hex_safe,
)


class TestHexToRgb:
    def test_basic(self):
        rgb = hex_to_rgb("#1F2D3D")
        assert rgb == RGBColor(0x1F, 0x2D, 0x3D)

    def test_without_hash(self):
        rgb = hex_to_rgb("FF0000")
        assert rgb == RGBColor(0xFF, 0x00, 0x00)


class TestRgbToHexSafe:
    def test_valid(self):
        rgb = RGBColor(0x1F, 0x2D, 0x3D)
        result = rgb_to_hex_safe(type('', (), {'rgb': rgb})())
        assert result is not None

    def test_none(self):
        assert rgb_to_hex_safe(None) is None


class TestEmuToPt:
    def test_none(self):
        assert _emu_to_pt(None) is None

    def test_conversion(self):
        # 1pt = 12700 EMU
        assert _emu_to_pt(12700) == 1.0
