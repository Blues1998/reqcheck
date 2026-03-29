from __future__ import annotations

import json

from rich.console import Console

from reqcheck.models import ScanResult


def render_results(result: ScanResult, console: Console, *, path: str = ".") -> None:
    """Print a human-readable report of scan results to the console."""
    console.print(f"Scanning: [dim]{path}/**/*.py[/dim]")
    console.print(
        f"Scanned [bold]{result.scanned_files}[/bold] file(s) "
        f"using {len(result.requirements_sources)} requirements source(s)\n"
    )

    if result.unused_deps:
        console.print(
            "[bold yellow]Unused dependencies[/bold yellow] "
            "(listed in requirements but never imported):"
        )
        for pkg in result.unused_deps:
            console.print(f"  [yellow]•[/yellow] {pkg}")
        console.print()

    if result.undeclared_imports:
        console.print(
            "[bold red]Undeclared imports[/bold red] "
            "(imported in code but not in requirements):"
        )
        for imp in result.undeclared_imports:
            console.print(f"  [red]•[/red] {imp}")
        console.print()

    if not result.has_issues:
        console.print("[bold green]✓ No issues found[/bold green]")
    else:
        n = result.issue_count
        console.print(
            f"[bold red]✗ Found {n} issue{'s' if n != 1 else ''}[/bold red]"
        )


def render_json(result: ScanResult) -> str:
    """Return a JSON string representation of the scan result."""
    return json.dumps(
        {
            "unused_deps": result.unused_deps,
            "undeclared_imports": result.undeclared_imports,
            "scanned_files": result.scanned_files,
            "requirements_sources": result.requirements_sources,
            "has_issues": result.has_issues,
            "issue_count": result.issue_count,
        },
        indent=2,
    )
