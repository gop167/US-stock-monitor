#!/usr/bin/env python3
"""Backward-compatible entrypoint for the weekly pullback monitor."""

from monitor import main


if __name__ == "__main__":
    raise SystemExit(main())
