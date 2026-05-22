"""CLI sub-command for diffing two env files."""
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envoy_config_lint.differ import diff_env_files
from envoy_config_lint.formatter import OutputFormat
from envoy_config_lint.formatter_diff import format_diff
from envoy_config_lint.parser import parse_env_file


def build_diff_parser(subparsers=None) -> ArgumentParser:
    """Build the argument parser for the diff sub-command."""
    description = "Compare two .env files and report key differences."
    if subparsers is not None:
        parser = subparsers.add_parser("diff", help=description, description=description)
    else:
        parser = ArgumentParser(prog="envoy-diff", description=description)

    parser.add_argument("base", metavar="BASE_FILE",
                        help="Reference .env file (e.g. .env.example)")
    parser.add_argument("compare", metavar="COMPARE_FILE",
                        help=".env file to compare against the base")
    parser.add_argument(
        "--format", "-f",
        choices=[f.value for f in OutputFormat],
        default=OutputFormat.TEXT.value,
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )
    return parser


def run_diff(args: Namespace) -> int:
    """Execute the diff command and return an exit code."""
    base_path = Path(args.base)
    compare_path = Path(args.compare)

    for path in (base_path, compare_path):
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    base_result = parse_env_file(base_path.read_text(encoding="utf-8"))
    compare_result = parse_env_file(compare_path.read_text(encoding="utf-8"))

    diff = diff_env_files(
        base_result, compare_result,
        base_name=str(base_path),
        compare_name=str(compare_path),
    )

    fmt = OutputFormat(args.format)
    print(format_diff(diff, fmt))

    if args.exit_code and diff.has_differences:
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_diff_parser()
    args = parser.parse_args()
    sys.exit(run_diff(args))


if __name__ == "__main__":  # pragma: no cover
    main()
