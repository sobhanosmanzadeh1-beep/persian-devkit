"""دستور pdev scaffold — ساخت ساختار پروژه از قالب."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()

# قالب‌های پروژه: {filepath: content}
_SCAFFOLDS: dict[str, dict[str, str]] = {
    "python": {
        "README.md": "# {name}\n\nتوضیح پروژه...\n",
        "pyproject.toml": """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
{name} = "{name}.main:main"
""",
        "requirements.txt": "",
        "src/{name}/__init__.py": '"""پکیج {name}."""\n\n__version__ = "0.1.0"\n',
        "src/{name}/main.py": '''"""نقطهٔ ورود {name}."""


def main() -> None:
    """تابع اصلی."""
    print("سلام از {name}!")


if __name__ == "__main__":
    main()
''',
        "tests/__init__.py": "",
        "tests/test_main.py": '''"""تست‌های {name}."""
from {name}.main import main


def test_main_runs(capsys):
    main()
    captured = capsys.readouterr()
    assert "{name}" in captured.out
''',
        ".gitignore": "__pycache__/\n*.pyc\n.venv/\nvenv/\ndist/\nbuild/\n*.egg-info/\n",
    },
    "node": {
        "README.md": "# {name}\n\nتوضیح پروژه...\n",
        "package.json": """{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "",
  "main": "src/index.js",
  "scripts": {{
    "start": "node src/index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": [],
  "author": "",
  "license": "MIT"
}}
""",
        "src/index.js": "console.log('سلام از {name}!');\n",
        ".gitignore": "node_modules/\ndist/\n.env\n.env.local\n",
    },
    "minimal": {
        "README.md": "# {name}\n",
        ".gitignore": "__pycache__/\n.venv/\n.env\n",
    },
}


def _create_files(root: Path, name: str, scaffold: dict[str, str]) -> list[Path]:
    """فایل‌های قالب را می‌سازد و لیست مسیرها را برمی‌گرداند."""
    created: list[Path] = []
    for rel, content in scaffold.items():
        path = root / rel.format(name=name)
        path.parent.mkdir(parents=True, exist_ok=True)
        rendered = content.format(name=name)
        path.write_text(rendered, encoding="utf-8")
        created.append(path)
    return created


def scaffold_command(
    kind: Optional[str] = typer.Argument(
        None, help="نوع قالب: python، node، minimal."
    ),
    name: Optional[str] = typer.Argument(None, help="نام پروژه."),
    target: Path = typer.Option(
        Path("."), "--target", "-t", help="پوشهٔ مقصد (پیش‌فرض: جاری)."
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="اجرای اجباری روی پوشه‌های موجود."
    ),
    list_templates: bool = typer.Option(
        False, "--list", "-l", help="نمایش قالب‌های موجود."
    ),
) -> None:
    """ساخت ساختار پروژه از قالب.

    مثال:
      pdev scaffold python myproject
      pdev scaffold node myapp --target ./projects
      pdev scaffold --list
    """
    # حالت --list: نمایش قالب‌ها و خروج
    if list_templates:
        console.print("قالب‌های پروژه:")
        for tname in _SCAFFOLDS:
            console.print(f"  • {tname}")
        return

    if kind is None or name is None:
        console.print("[red]✗ خطا:[/red] نوع قالب و نام پروژه الزامی است.")
        console.print("برای دیدن قالب‌ها: [bold]pdev scaffold --list[/bold]")
        raise typer.Exit(1)

    key = kind.lower()
    if key not in _SCAFFOLDS:
        console.print(
            f"[red]✗ خطا:[/red] قالب ناشناخته: {kind}. "
            f"موجود: {', '.join(_SCAFFOLDS.keys())}"
        )
        raise typer.Exit(1)

    if not name or "/" in name or "\\" in name:
        console.print(f"[red]✗ خطا:[/red] نام پروژه نامعتبر: {name}")
        raise typer.Exit(1)

    root = target.resolve() / name
    if root.exists() and not force:
        console.print(
            f"[red]✗ خطا:[/red] پوشهٔ مقصد وجود دارد: {root} (از --force استفاده کن)"
        )
        raise typer.Exit(1)

    root.mkdir(parents=True, exist_ok=True)
    created = _create_files(root, name, _SCAFFOLDS[key])

    console.print(f"[green]✓ پروژه ساخته شد:[/green] {root}")
    for p in created:
        rel = p.relative_to(root)
        console.print(f"  • {rel}")
    console.print(f"\n[cyan]قدم بعدی:[/cyan] cd {root}")

