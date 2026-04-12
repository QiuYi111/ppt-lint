"""Tests for domain models."""

from internal.domain.models import (
    FixAction,
    FontRule,
    LintIssue,
    Severity,
)


class TestLintIssue:
    def test_creation(self):
        issue = LintIssue(
            rule_id="test.rule",
            severity=Severity.ERROR,
            slide_index=0,
            element_desc="title",
            message="Font is wrong",
        )
        assert issue.rule_id == "test.rule"
        assert issue.severity == Severity.ERROR
        assert issue.slide_index == 0
        assert issue.fix is None

    def test_to_dict(self):
        issue = LintIssue(
            rule_id="fonts.title",
            severity=Severity.WARNING,
            slide_index=2,
            element_desc="body text",
            message="Size mismatch",
            fix=FixAction("fix font", lambda: None),
        )
        d = issue.to_dict()
        assert d["rule_id"] == "fonts.title"
        assert d["severity"] == "warning"
        assert d["slide_index"] == 2
        assert d["fixable"] is True
        assert d["fix_description"] == "fix font"

    def test_to_dict_no_fix(self):
        issue = LintIssue(
            rule_id="test",
            severity=Severity.INFO,
            slide_index=0,
            element_desc="x",
            message="y",
        )
        d = issue.to_dict()
        assert d["fixable"] is False
        assert "fix_description" not in d


class TestFontRule:
    def test_defaults(self):
        fr = FontRule()
        assert fr.family is None
        assert fr.size_pt is None
        assert fr.bold is None
        assert fr.color is None

    def test_with_values(self):
        fr = FontRule(family="微软雅黑", size_pt=14, bold=True, color="#333")
        assert fr.family == "微软雅黑"
        assert fr.size_pt == 14
        assert fr.bold is True
        assert fr.color == "#333"


class TestSeverity:
    def test_values(self):
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"

    def test_from_string(self):
        assert Severity("error") == Severity.ERROR
        assert Severity("warning") == Severity.WARNING
