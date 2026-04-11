"""AI rule cache manager — handles Claude API calls and caching."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_CACHE_DIR = Path(".ppt-lint-cache")
METADATA_FILE = "cache_metadata.json"


class AICache:
    """Manages cache for AI-compiled rules."""

    def __init__(self, cache_dir: Path | str = DEFAULT_CACHE_DIR) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_path = self.cache_dir / METADATA_FILE
        self._metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        if self.metadata_path.exists():
            try:
                return json.loads(self.metadata_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_metadata(self) -> None:
        self.metadata_path.write_text(
            json.dumps(self._metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _content_hash(rule_id: str, description: str, severity: str) -> str:
        content = f"{rule_id}:{description}:{severity}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(self, rule_id: str, description: str, severity: str) -> str | None:
        """Get cached compiled code for a rule.

        Returns the Python code string if cache is valid, None otherwise.
        """
        hash_key = self._content_hash(rule_id, description, severity)
        entry = self._metadata.get(rule_id)

        if entry and entry.get("hash") == hash_key:
            cache_file = self.cache_dir / f"{rule_id}.py"
            if cache_file.exists():
                logger.debug(f"Cache hit for rule {rule_id}")
                return cache_file.read_text(encoding="utf-8")

        return None

    def put(self, rule_id: str, description: str, severity: str, code: str) -> None:
        """Store compiled code in cache."""
        hash_key = self._content_hash(rule_id, description, severity)
        cache_file = self.cache_dir / f"{rule_id}.py"

        cache_file.write_text(code, encoding="utf-8")
        self._metadata[rule_id] = {
            "hash": hash_key,
            "description": description,
            "severity": severity,
            "cached_at": datetime.now().isoformat(),
        }
        self._save_metadata()
        logger.debug(f"Cached rule {rule_id}")

    def invalidate(self, rule_id: str | None = None) -> None:
        """Invalidate cache for a specific rule or all rules."""
        if rule_id:
            self._metadata.pop(rule_id, None)
            cache_file = self.cache_dir / f"{rule_id}.py"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all
            for f in self.cache_dir.glob("*.py"):
                f.unlink()
            self._metadata = {}
        self._save_metadata()

    @property
    def api_key(self) -> str | None:
        return os.environ.get("ANTHROPIC_API_KEY")

    def compile_rule(self, rule_id: str, description: str, severity: str) -> str | None:
        """Compile an AI rule via Claude API.

        Returns the generated Python code, or None on failure.
        """
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set, cannot compile AI rules")
            return None

        try:
            import anthropic  # noqa: F401
        except ImportError:
            logger.warning("anthropic package not installed")
            return None

        prompt = f"""You are a python-pptx expert. Compile this rule into a Python function.

Rule description: {description}
Severity: {severity}

Function signature:
def check_{rule_id}(slide, slide_index) -> list:
    ...

Return a list of dicts with keys: rule_id, severity, slide_index, element_desc, message, fix.
Use rule_id="{rule_id}", severity="{severity}".
The `slide` parameter is a python-pptx Slide object.
fix should always be None.
Return ONLY Python code. No imports needed (modules are already available)."""

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            code = response.content[0].text.strip()
            # Extract code from markdown if present
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()

            self.put(rule_id, description, severity, code)
            return code
        except Exception as e:
            logger.error(f"Claude API call failed for rule {rule_id}: {e}")
            return None
