"""Console entry point: `vml-run experiments/<config>.toml`."""

from __future__ import annotations

import sys

from harness.runner import _main


def main() -> None:
    sys.exit(_main())


if __name__ == "__main__":
    main()
