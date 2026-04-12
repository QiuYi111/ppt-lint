"""CLI entry point for ppt-lint."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import click

from internal.domain.rules import parse_rules
from internal.infrastructure.compiler import compile_rules
from internal.infrastructure.engine import fix_file, lint_file
from internal.infrastructure.reporter import (
    report_html,
    report_json,
    report_terminal,
)


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


@click.group()
@click.version_option(version="0.1.0", prog_name="ppt-lint")
def cli() -> None:
    """ppt-lint — Configuration-driven PowerPoint format checker and auto-fixer."""
    pass


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--rules", "-r", required=True, type=click.Path(exists=True),
              help="Path to rules.yaml")
@click.option("--fix", is_flag=True, help="Auto-fix issues")
@click.option("--dry-run", is_flag=True, help="Preview fixes without modifying file")
@click.option("--output", "-o", type=click.Choice(["terminal", "json", "html"]),
              default="terminal", help="Output format")
@click.option("--report", "report_path", type=click.Path(), help="Write report to file")
@click.option("--output-file", type=click.Path(), help="Output fixed file path (with --fix)")
@click.option("--no-ai", is_flag=True, help="Skip AI rule compilation")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def check(
    file: str,
    rules: str,
    fix: bool,
    dry_run: bool,
    output: str,
    report_path: str | None,
    output_file: str | None,
    no_ai: bool,
    verbose: bool,
) -> None:
    """Check a PowerPoint file against formatting rules."""
    _setup_logging(verbose)

    try:
        rule_set = parse_rules(rules)
    except Exception as e:
        click.echo(f"Error loading rules: {e}", err=True)
        sys.exit(2)

    try:
        compiled = compile_rules(rule_set, use_ai=not no_ai)
    except Exception as e:
        click.echo(f"Error compiling rules: {e}", err=True)
        sys.exit(2)

    if fix or dry_run:
        result = fix_file(
            file,
            compiled,
            output_path=output_file,
            dry_run=dry_run,
            use_ai=not no_ai,
        )
        if dry_run and result.fixable:
            click.echo(
                f"[Dry Run] Would fix {len(result.fixable)} issues",
                err=True,
            )
    else:
        result = lint_file(file, compiled, use_ai=not no_ai)

    if output == "terminal":
        report_terminal(result)
    elif output == "json":
        report_content = report_json(result)
        click.echo(report_content)
    elif output == "html":
        report_content = report_html(result)
        if report_path:
            Path(report_path).write_text(report_content, encoding="utf-8")
        else:
            click.echo("HTML report generated. Use --report <file> to save.")

    # Exit code
    if result.errors:
        sys.exit(1)
    elif result.warnings:
        sys.exit(0)
    else:
        sys.exit(0)


@cli.command()
@click.option("--output", "-o", type=click.Path(), default="rules.yaml", help="Output file path")
def init(output: str) -> None:
    """Scaffold an example rules.yaml file."""
    example = '''# ppt-lint 规则配置文件
# 详细文档: https://github.com/QiuYi111/ppt-lint

meta:
  name: "默认规范"
  version: "1.0"

# ── 字体规则 ──
fonts:
  title:
    family: "微软雅黑"
    size_pt: 28
    bold: true
    color: "#1F2D3D"
  body:
    family: "微软雅黑"
    size_pt: 14
    bold: false
    color: "#333333"
  caption:
    family: "微软雅黑"
    size_pt: 10
    color: "#666666"

# ── 颜色规则 ──
colors:
  allowed_text: ["#1F2D3D", "#333333", "#666666", "#FFFFFF"]
  allowed_background: ["#FFFFFF", "#F5F5F5", "#1F2D3D"]
  accent: "#2B7FE1"

# ── 对齐规则 ──
alignment:
  title: "left"
  body: "left"

# ── 间距规则 ──
spacing:
  line_spacing: 1.2

# ── 页码规则 ──
slide_number:
  visible: true

# ── 图表规则 ──
charts:
  require_title: true

# ── AI 规则（需要 ANTHROPIC_API_KEY）──
ai_rules:
  - id: "no_orphan_text"
    description: "每张 slide 的正文文字块不应该只有一行孤行，至少要有两行或者干脆没有"
    severity: warning
'''
    out_path = Path(output)
    if out_path.exists():
        if not click.confirm(f"{output} already exists. Overwrite?", default=False):
            click.echo("Aborted.")
            return

    out_path.write_text(example, encoding="utf-8")
    click.echo(f"Created {output}")


if __name__ == "__main__":
    cli()
