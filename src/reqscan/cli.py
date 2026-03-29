from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from reqscan import __version__
from reqscan.core import run_check
from reqscan.reporter import render_json, render_results


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--requirements",
    "-r",
    multiple=True,
    metavar="FILE",
    help="Override requirements file path (can be repeated).",
)
@click.option(
    "--ignore-package",
    multiple=True,
    metavar="PKG",
    help="Treat a package as always-used, hiding it from the unused report.",
)
@click.option(
    "--ignore-import",
    multiple=True,
    metavar="MODULE",
    help="Ignore an import name in the undeclared report.",
)
@click.option("--include-dev", is_flag=True, help="Include dev/optional dependencies.")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON.")
@click.option("--no-color", is_flag=True, help="Disable colored output.")
@click.version_option(__version__, "--version", "-V")
def main(
    path: str,
    requirements: tuple[str, ...],
    ignore_package: tuple[str, ...],
    ignore_import: tuple[str, ...],
    include_dev: bool,
    output_json: bool,
    no_color: bool,
) -> None:
    """Check for unused and undeclared Python dependencies.

    PATH is the root directory of the project to scan (default: current directory).
    """
    console = Console(no_color=no_color)

    try:
        result = run_check(
            path=path,
            requirements_files=list(requirements) if requirements else None,
            ignore_packages=list(ignore_package) if ignore_package else None,
            ignore_imports=list(ignore_import) if ignore_import else None,
            include_dev=include_dev,
        )
    except Exception as exc:
        Console(stderr=True).print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(2)

    if output_json:
        click.echo(render_json(result))
    else:
        render_results(result, console, path=str(Path(path).resolve()))

    sys.exit(1 if result.has_issues else 0)
