#!/usr/bin/env python3
"""Publish the one-sentence pitch for the make.fun bounty
"Ridiculous at First Glance, Real by the Second".

The pitch is stored in ``entry.txt`` beside this file. The program
loads it, enforces the bounty gate (one line of UTF-8 text, between
1 and 200 characters, not blank), and publishes the exact bytes as
``entry.txt`` in the output directory. It then reads the published
file back and refuses to exit cleanly unless it matches, so a bad
write can never pass silently.

Output goes to ``$MAKEFUN_OUTPUT_DIR`` when that variable is set,
otherwise to ``/output``. Pass ``--output-dir <dir>`` to choose it on
the command line instead, or ``--verify-only`` to check the pitch
without writing anything. Only the standard library is used: no
network, no clock, no randomness, so every run publishes the same
bytes.
"""

import argparse
import os
import sys
from pathlib import Path

LIMIT = 200


def read_pitch() -> str:
    source = Path(__file__).resolve().parent / "entry.txt"
    return source.read_text(encoding="utf-8").strip()


def check_pitch(text: str) -> None:
    if not text.strip():
        raise SystemExit("pitch is blank")
    if len(text) > LIMIT:
        raise SystemExit(f"pitch is {len(text)} chars, limit is {LIMIT}")
    if any(ch in text for ch in "\r\n"):
        raise SystemExit("pitch must fit on one line")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=None,
                        help="directory to write entry.txt into")
    parser.add_argument("--verify-only", action="store_true",
                        help="validate the pitch without writing it")
    return parser.parse_args(argv)


def publish(text: str, output_dir=None) -> Path:
    directory = Path(output_dir or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "entry.txt"
    target.write_text(text, encoding="utf-8")
    if target.read_text(encoding="utf-8") != text:
        raise SystemExit("published pitch differs from entry.txt")
    return target


def main(argv=None) -> int:
    args = parse_args(argv)
    pitch = read_pitch()
    check_pitch(pitch)
    if args.verify_only:
        print(f"Valid: {len(pitch)}-character pitch")
        return 0
    target = publish(pitch, args.output_dir)
    print(f"Published {len(pitch)}-character pitch to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
