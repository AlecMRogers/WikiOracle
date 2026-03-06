#!/usr/bin/env python3
"""Convert ChatGPT/Claude conversation JSON exports to WikiOracle XML.

Usage::

    python bin/migrate_conversations_to_xml.py                  # convert data/conversations/*.json → all.xml
    python bin/migrate_conversations_to_xml.py --dry-run        # preview without writing
    python bin/migrate_conversations_to_xml.py file1.json ...   # convert specific files

Delegates to data/conversations/convert.py.
Output: data/conversations/all.xml (WikiOracle State XML).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    convert_py = Path(__file__).resolve().parent.parent / "data" / "conversations" / "convert.py"
    if not convert_py.exists():
        print(f"ERROR: {convert_py} not found.", file=sys.stderr)
        sys.exit(1)
    raise SystemExit(subprocess.call([sys.executable, str(convert_py)] + sys.argv[1:]))


if __name__ == "__main__":
    main()
