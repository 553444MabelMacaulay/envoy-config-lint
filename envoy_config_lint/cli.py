"""Command-line interface for envoy-config-lint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envoy_config_lint.formatter import OutputFormat, format_report
from envoy_config_lint.linter import lint_file


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envoy-config-lint",
        description="Static analysis for dotenv / environment-variable files.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to lint.",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        help="Output format (default: text).",
    )
    p.add_argument(
        "--no-warnings",
        action="store_true",
        help="Suppress warnings; only report errors.",
    )
    return p


def run(argv: list[str] | None = None) -> int:
    """Entry-point; returns an exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    fmt = OutputFormat(args.fmt)

    exit_code = 0

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"error: file not found: {filepath}", file=sys.stderr)
            exit_code = 2
            continue

        report = lint_file(path)

        if args.no_warnings:
            report = report._replace(
                issues=[i for i in report.issues if i.severity == "error"]
            )

        output = format_report(report, fmt)
        if output:
            if len(args.files) > 1:
                print(f"==> {filepath} <==")
            print(output)

        if report.has_errors:
            exit_code = 1

    return exit_code


def main() -> None:  # pragma: no cover
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
