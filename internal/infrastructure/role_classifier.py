"""AI-powered text role classifier using Claude CLI.

Instead of brittle heuristics, sends slide shape metadata to Claude
for intelligent role classification. Results are cached per slide content.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .pptx_adapter import classify_text_role, extract_slide_summary

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".ppt-lint-cache/roles")

# Claude CLI config
_CLAUDE_CMD = "claude"
_CLAUDE_MODEL = "claude-sonnet-4-20250514"
_CLAUDE_TIMEOUT = 45  # seconds


def classify_slide_roles(
    slide: Any,
    slide_index: int,
    user_roles: set[str] | None = None,
    use_ai: bool = True,
) -> dict[int, str]:
    """Classify all text shapes on a slide into roles.

    If use_ai is True and claude CLI is available, uses Claude for
    intelligent classification. Falls back to heuristic classifier
    if Claude is unavailable or use_ai is False.

    Returns a dict mapping shape_index → role_name.
    """
    if not use_ai:
        return _classify_heuristic(slide, user_roles)

    result = _classify_via_claude(slide, slide_index, user_roles)
    if result is not None:
        return result

    logger.info(
        "Claude CLI unavailable, falling back to heuristic "
        f"classifier for slide {slide_index}"
    )
    return _classify_heuristic(slide, user_roles)


def _classify_heuristic(
    slide: Any, user_roles: set[str] | None = None,
) -> dict[int, str]:
    """Use the built-in heuristic classifier for all shapes."""
    roles: dict[int, str] = {}
    for si, shape in enumerate(slide.shapes):
        if shape.has_text_frame and shape.text_frame.text.strip():
            roles[si] = classify_text_role(shape, slide, user_roles)
    return roles


def _claude_available() -> bool:
    """Check if claude CLI is available."""
    return shutil.which(_CLAUDE_CMD) is not None


def _classify_via_claude(
    slide: Any,
    slide_index: int,
    user_roles: set[str] | None = None,
) -> dict[int, str] | None:
    """Classify shapes using Claude CLI."""
    if not _claude_available():
        return None

    summary = extract_slide_summary(slide, slide_index)
    text_shapes = [s for s in summary["shapes"] if s.get("has_text")]
    if not text_shapes:
        return {}

    # Check cache
    cache_key = _slide_content_hash(text_shapes, user_roles)
    cached = _load_cache(cache_key)
    if cached is not None:
        logger.debug(f"Role cache hit for slide {slide_index}")
        return cached

    # Build prompt
    roles_list = sorted(user_roles) if user_roles else [
        "title", "subtitle", "body", "caption",
        "section_number", "section_title", "slide_number", "footer",
    ]

    shapes_desc = json.dumps(text_shapes, ensure_ascii=False, indent=2)

    prompt = (
        "You are a PPT layout analysis expert. Classify each text shape "
        "into exactly ONE role.\n\n"
        f"Available roles: {roles_list}\n\n"
        f"Slide: {summary['slide_width_in']}\" × {summary['slide_height_in']}\"\n\n"
        f"Shapes:\n{shapes_desc}\n\n"
        "Classification rules:\n"
        "- Decorative large numbers on divider slides (e.g. \"01\", \"02\") → section_number\n"
        "- Page numbers (e.g. \"4 / 13\") → slide_number\n"
        "- Headers/footers (institution name, date, small text at edges) → footer\n"
        "- Main slide heading → title\n"
        "- Sub-heading → section_title\n"
        "- Content paragraphs → body\n"
        "- Figure captions, small annotations → caption\n"
        "- Author info, affiliations → footer\n"
        "- TOC entries → body\n"
        "- If unclear, use \"body\"\n"
        "- Consider ALL clues: font size, position, text content, placeholder type, name\n\n"
        "Return ONLY a JSON object mapping shape index (string) to role (string).\n"
        "No explanation, no markdown fences. Example:\n"
        '{"0": "title", "1": "body", "3": "slide_number"}'
    )

    try:
        result = subprocess.run(
            [
                _CLAUDE_CMD, "--print",
                "--bare",
                "--model", _CLAUDE_MODEL,
                "--output-format", "json",
                "--dangerously-skip-permissions",
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=_CLAUDE_TIMEOUT,
        )

        if result.returncode != 0:
            logger.warning(
                f"Claude CLI failed for slide {slide_index}: "
                f"{result.stderr[:200]}"
            )
            return None

        # Parse Claude's JSON output: {"type": "result", "result": "..."}
        output = json.loads(result.stdout)
        content = output.get("result", "")

        if output.get("subtype") == "error_max_budget_usd":
            logger.warning(
                f"Claude budget exceeded for slide {slide_index}"
            )
            return None

        if not content:
            logger.warning(f"Empty Claude response for slide {slide_index}")
            return None

        # Claude wraps in markdown fences even when asked not to
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()

        role_map = json.loads(content)

        # Convert string keys to int, validate roles
        parsed: dict[int, str] = {}
        for k, v in role_map.items():
            try:
                idx = int(k)
                if isinstance(v, str) and v in roles_list:
                    parsed[idx] = v
                else:
                    logger.debug(
                        f"Slide {slide_index}: unknown role '{v}' "
                        f"for shape {idx}, using 'body'"
                    )
                    parsed[idx] = "body"
            except (ValueError, TypeError):
                continue

        _save_cache(cache_key, parsed)
        logger.info(
            f"Claude classified {len(parsed)} shapes on slide {slide_index}"
        )
        return parsed

    except subprocess.TimeoutExpired:
        logger.warning(f"Claude CLI timed out for slide {slide_index}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(
            f"Failed to parse Claude output for slide {slide_index}: {e}"
        )
        return None
    except FileNotFoundError:
        logger.warning("claude CLI not found")
        return None
    except Exception as e:
        logger.warning(f"Claude classification error for slide {slide_index}: {e}")
        return None


def _slide_content_hash(
    text_shapes: list[dict[str, Any]],
    user_roles: set[str] | None = None,
) -> str:
    """Create a content-based cache key."""
    relevant = []
    for s in text_shapes:
        relevant.append({
            "i": s["index"],
            "n": s["name"],
            "t": s.get("text_preview", "")[:60],
            "fs": s.get("max_font_size_pt"),
            "pos": (s.get("left_in"), s.get("top_in")),
            "ph": s.get("placeholder_idx"),
        })
    blob = json.dumps(relevant, sort_keys=True, ensure_ascii=False)
    roles_blob = json.dumps(sorted(user_roles)) if user_roles else ""
    combined = f"{blob}|{roles_blob}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def _load_cache(key: str) -> dict[int, str] | None:
    """Load cached role classification."""
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            return {int(k): v for k, v in data.items()}
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(key: str, roles: dict[int, str]) -> None:
    """Save role classification to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{key}.json"
    try:
        cache_file.write_text(
            json.dumps({str(k): v for k, v in roles.items()}, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning(f"Failed to write role cache: {e}")
