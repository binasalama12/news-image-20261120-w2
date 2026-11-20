#!/usr/bin/env python3
"""Publisher for "The World in One Day" - Friday 20 November 2026.

The artwork for this entry ships inside the repository as entry.png,
already rendered at 1024 by 1024 pixels. This program is intentionally
small and uses only the Python standard library: it validates the
bundled image and copies it into the output directory the grader
provides.
"""

import os
import shutil
import sys
from pathlib import Path

DESIGN_TITLE = "The World in One Day"
DESIGN_DATE = "Friday 20 November 2026"
MAX_BYTES = 1048576  # competition limit: 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def find_artwork() -> Path:
    here = Path(__file__).resolve().parent
    return here / "entry.png"


def validate(path: Path) -> int:
    if not path.is_file():
        print(f"error: artwork not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if not (head.startswith(PNG_MAGIC) or head.startswith(JPEG_MAGIC)):
        print("error: artwork is neither PNG nor JPEG", file=sys.stderr)
        raise SystemExit(1)
    if size > MAX_BYTES:
        print(f"error: artwork is {size} bytes, over the {MAX_BYTES} limit",
              file=sys.stderr)
        raise SystemExit(1)
    return size


def publish(source: Path) -> Path:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    return target


def main() -> int:
    artwork = find_artwork()
    size = validate(artwork)
    target = publish(artwork)
    print(f"{DESIGN_TITLE} -- {DESIGN_DATE}")
    print(f"published {size} bytes -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
