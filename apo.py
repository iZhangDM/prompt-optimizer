#!/usr/bin/env python3
"""Agent Prompt Optimizer — CLI entry point."""

from __future__ import annotations

import sys

from prompt_optimizer.cli import build_parser, run_optimize, run_pro, run_license


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "optimize":
        run_optimize(args)
    elif args.command == "pro":
        run_pro(args)
    elif args.command == "license":
        run_license(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
