"""Tests for rule parsing."""

from pathlib import Path

import pytest

from internal.domain.models import Severity
from internal.domain.rules import RuleParseError, parse_rules

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseRules:
    def test_parse_example_rules(self):
        rules = parse_rules(Path(__file__).parent.parent / "rules.yaml")
        assert rules.meta_name == "导师组规范 v1"
        assert rules.meta_version == "1.0"
        assert "title" in rules.fonts
        assert rules.fonts["title"].family == "微软雅黑"
        assert rules.fonts["title"].size_pt == 28
        assert rules.fonts["title"].bold is True
        assert rules.fonts["title"].color == "#1F2D3D"
        assert "body" in rules.fonts
        assert rules.colors.allowed_text
        assert rules.colors.accent == "#2B7FE1"
        assert rules.alignment.title == "left"
        assert rules.spacing.line_spacing == 1.2
        assert rules.slide_number.visible is True
        assert rules.charts.require_title is True
        assert len(rules.ai_rules) == 3

    def test_missing_file(self):
        with pytest.raises(RuleParseError, match="not found"):
            parse_rules("/nonexistent/rules.yaml")

    def test_minimal_rules(self, tmp_path):
        rules_file = tmp_path / "minimal.yaml"
        rules_file.write_text("meta:\n  name: test\n")
        rules = parse_rules(rules_file)
        assert rules.meta_name == "test"
        assert len(rules.fonts) == 0
        assert len(rules.ai_rules) == 0

    def test_ai_rule_severity(self, tmp_path):
        rules_file = tmp_path / "ai.yaml"
        rules_file.write_text("""
ai_rules:
  - id: "test_error"
    description: "test"
    severity: error
  - id: "test_warning"
    description: "test2"
    severity: warning
  - id: "test_info"
    description: "test3"
    severity: info
  - id: "test_default"
    description: "test4"
""")
        rules = parse_rules(rules_file)
        assert rules.ai_rules[0].severity == Severity.ERROR
        assert rules.ai_rules[1].severity == Severity.WARNING
        assert rules.ai_rules[2].severity == Severity.INFO
        assert rules.ai_rules[3].severity == Severity.WARNING  # default
