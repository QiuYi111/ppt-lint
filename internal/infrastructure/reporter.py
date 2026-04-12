"""Reporter — outputs lint results in various formats."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from internal.domain.models import LintIssue, Severity
from internal.infrastructure.engine import LintResult

console = Console()

SEVERITY_ICON = {
    Severity.ERROR: "[bold red]✗[/bold red]",
    Severity.WARNING: "[bold yellow]⚠[/bold yellow]",
    Severity.INFO: "[bold blue]ℹ[/bold blue]",
}

SEVERITY_LABEL = {
    Severity.ERROR: "ERROR",
    Severity.WARNING: "WARN",
    Severity.INFO: "INFO",
}


def report_terminal(result: LintResult) -> str:
    """Generate terminal report with rich formatting."""

    # Header
    console.print()
    console.rule(f"[bold]{Path(result.file_path).name}[/bold]")
    console.print()

    if result.passed:
        console.print("[bold green]✓ No issues found![/bold green]")
        console.print()
        return ""

    # Summary
    console.print(
        f"  {SEVERITY_ICON[Severity.ERROR]} {len(result.errors)} errors   "
        f"{SEVERITY_ICON[Severity.WARNING]} {len(result.warnings)} warnings   "
        f"{SEVERITY_ICON[Severity.INFO]} {len(result.infos)} info"
    )
    if result.fixable:
        console.print(f"  [dim]💡 {len(result.fixable)} issues can be auto-fixed with --fix[/dim]")
    console.print()

    # Group by slide
    from collections import defaultdict
    by_slide: dict[int, list[LintIssue]] = defaultdict(list)
    for issue in result.issues:
        by_slide[issue.slide_index].append(issue)

    for slide_idx in sorted(by_slide.keys()):
        issues = by_slide[slide_idx]
        console.print(f"[bold]Slide {slide_idx + 1}[/bold] ({len(issues)} issues)")

        table = Table(show_header=True, header_style="bold", padding=(0, 1))
        table.add_column("Rule", style="cyan", max_width=25)
        table.add_column("Severity", max_width=8)
        table.add_column("Element", max_width=25)
        table.add_column("Message")
        table.add_column("Fix?", max_width=5)

        for issue in issues:
            fix_str = "✓" if issue.fix else ""
            table.add_row(
                issue.rule_id,
                SEVERITY_LABEL[issue.severity],
                issue.element_desc,
                issue.message,
                fix_str,
            )

        console.print(table)
        console.print()

    return ""


def report_json(result: LintResult) -> str:
    """Generate JSON report."""
    data = {
        "file": result.file_path,
        "summary": {
            "total": result.total,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "info": len(result.infos),
            "fixable": len(result.fixable),
            "passed": result.passed,
        },
        "issues": [issue.to_dict() for issue in result.issues],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def report_html(result: LintResult) -> str:
    """Generate self-contained HTML report."""
    issues_html = ""
    from collections import defaultdict
    by_slide: dict[int, list[LintIssue]] = defaultdict(list)
    for issue in result.issues:
        by_slide[issue.slide_index].append(issue)

    for slide_idx in sorted(by_slide.keys()):
        issues = by_slide[slide_idx]
        issues_html += f"<h3>Slide {slide_idx + 1} ({len(issues)} issues)</h3>\n"
        issues_html += (
            "<table><tr><th>Rule</th><th>Severity</th>"
            "<th>Element</th><th>Message</th><th>Fix?</th></tr>\n"
        )
        for issue in issues:
            sev_map = {"error": "#dc3545", "warning": "#ffc107", "info": "#0d6efd"}
            sev_color = sev_map.get(issue.severity.value, "#666")
            fix_str = "✓" if issue.fix else ""
            issues_html += (
                f"<tr>"
                f"<td><code>{issue.rule_id}</code></td>"
                f'<td style="color:{sev_color};font-weight:bold">'
                f"{issue.severity.value.upper()}</td>"
                f"<td>{issue.element_desc}</td>"
                f"<td>{issue.message}</td>"
                f"<td>{fix_str}</td>"
                f"</tr>\n"
            )
        issues_html += "</table>\n"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>ppt-lint Report — {Path(result.file_path).name}</title>
<style>
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  max-width: 1000px; margin: 2em auto; padding: 0 1em; color: #333;
}}
h1 {{ color: #1F2D3D; }}
.summary {{ background: #f8f9fa; padding: 1em; border-radius: 8px; margin-bottom: 1em; }}
.summary .passed {{ color: #28a745; font-weight: bold; font-size: 1.2em; }}
.summary .failed {{ color: #dc3545; font-weight: bold; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2em; }}
th {{ background: #1F2D3D; color: white; padding: 0.5em; text-align: left; }}
td {{ padding: 0.5em; border-bottom: 1px solid #dee2e6; }}
tr:hover {{ background: #f5f5f5; }}
code {{ background: #e9ecef; padding: 0.1em 0.3em; border-radius: 3px; font-size: 0.9em; }}
</style>
</head>
<body>
<h1>📋 ppt-lint Report</h1>
<p><strong>File:</strong> {result.file_path}</p>
<div class="summary">
{_passed_html(result) if result.passed else _failed_html(result)}
</div>
{issues_html}
</body>
</html>"""
    return html


def _passed_html(result: LintResult) -> str:
    return "<p class='passed'>✓ No issues found!</p>"


def _failed_html(result: LintResult) -> str:
    err_count = len(result.errors)
    warn_count = len(result.warnings)
    info_count = len(result.infos)
    fix_count = len(result.fixable)
    return (
        f'<p class="failed">✗ {result.total} issues found</p>\n'
        f"<p>❌ {err_count} errors &nbsp; ⚠️ {warn_count} warnings "
        f"&nbsp; ℹ️ {info_count} info</p>\n"
        f"<p>💡 {fix_count} can be auto-fixed</p>"
    )


def report(result: LintResult, format: str = "terminal", output_path: str | None = None) -> str:
    """Generate a report in the specified format.

    Args:
        result: LintResult to report
        format: One of "terminal", "json", "html"
        output_path: If provided, write report to this file

    Returns:
        The report as a string
    """
    reporters = {
        "terminal": report_terminal,
        "json": report_json,
        "html": report_html,
    }
    reporter_fn = reporters.get(format, report_terminal)
    content = reporter_fn(result)

    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")

    return content
