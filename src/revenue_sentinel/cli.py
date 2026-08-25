from __future__ import annotations

import argparse
import json

from .demo import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit an opportunity queue without taking external action.")
    parser.add_argument("fixture", help="JSON array of opportunity records")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    result = run_demo(args.fixture)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))


if __name__ == "__main__":
    main()
