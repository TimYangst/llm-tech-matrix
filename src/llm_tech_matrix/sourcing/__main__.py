"""Subpackage entry point: `python -m llm_tech_matrix.sourcing <subcmd>`."""

import sys

from llm_tech_matrix.sourcing.fetch import main

if __name__ == "__main__":
    sys.exit(main())
