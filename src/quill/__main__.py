"""Lightweight CLI; querying version or help does not initialize services."""

import argparse

from quill import __version__


def main() -> int:
    """Parse CLI arguments without starting desktop services."""
    parser = argparse.ArgumentParser(prog="quill", description="Assistente desktop Quill")
    parser.add_argument("--version", action="version", version=__version__)
    parser.parse_args()
    from quill.bootstrap import main as desktop_main

    return desktop_main()


if __name__ == "__main__":
    raise SystemExit(main())
