"""Subpackage entry point: `python -m llm_oss_summary.sourcing <subcmd>`."""

import sys

from llm_oss_summary.sourcing.fetch import main

if __name__ == "__main__":
    sys.exit(main())
