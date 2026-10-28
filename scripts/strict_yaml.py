#!/usr/bin/env python3
"""strict_yaml.py: parse a YAML document and REJECT duplicate mapping keys.

PyYAML's safe_load silently keeps the LAST duplicate key, so a sidecar saying
`classification: technique` and later `classification: tool` resolves to `tool` while a
regex that matches the first line says `technique`. scripts/open-intake-pr.mjs calls this
(stdin -> JSON on stdout) so the classification gate judges the value the YAML parser
actually resolves, not a line a regex happened to match first.

Exit codes: 0 ok (JSON document on stdout), 2 duplicate key or parse error (reason on stderr).
"""
from __future__ import annotations

import json
import sys

import yaml


class DuplicateKeyError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that raises on a duplicate key in ANY mapping, at any depth."""


def _construct_mapping(loader: StrictLoader, node: yaml.MappingNode, deep: bool = False):
    seen: set = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise DuplicateKeyError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1}"
            )
        seen.add(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep)


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_strict(text: str):
    return yaml.load(text, Loader=StrictLoader)  # noqa: S506 (SafeLoader subclass)


def main() -> int:
    text = sys.stdin.read()
    try:
        doc = load_strict(text)
    except DuplicateKeyError as e:
        print(f"strict_yaml: {e}", file=sys.stderr)
        return 2
    except yaml.YAMLError as e:
        print(f"strict_yaml: YAML parse error: {e}", file=sys.stderr)
        return 2
    json.dump(doc, sys.stdout, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
