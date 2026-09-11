"""تست‌های ابزارهای پروژه (license, gitignore, scaffold, template)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persian_devkit.commands.template_cmd import (
    find_variables,
    render_template,
    template_command,
)
from persian_devkit.main import app
from persian_devkit.utils.gitignore_data import (
    GITIGNORES,
    combine_gitignores,
    list_gitignores,
)
from persian_devkit.utils.license_data import (
    LICENSES,
    list_licenses,
    render_license,
)

runner = CliRunner()


#license


def test_render_mit():
    text = render_license("MIT", "علی رضایی", 2024)
    assert "علی رضایی" in text
    assert "2024" in text
    assert "MIT License" in text


def test_render_invalid_license():
    with pytest.raises(ValueError):
        render_license("NOPE", "x", 2024)


def test_list_licenses_count():
    assert len(list_licenses()) >= 5


def test_cli_license_list():
    r = runner.invoke(app, ["license", "list"])
    assert r.exit_code == 0
    assert "MIT" in r.stdout


def test_cli_license_show():
    r = runner.invoke(app, ["license", "show", "MIT", "-a", "Ali"])
    assert r.exit_code == 0
    assert "Ali" in r.stdout


def test_cli_license_new(tmp_path: Path):
    out = tmp_path / "LICENSE"
    r = runner.invoke(
        app,
        ["license", "new", "MIT", "-a", "Sara", "-o", str(out)],
    )
    assert r.exit_code == 0
    assert out.exists()
    assert "Sara" in out.read_text(encoding="utf-8")


def test_cli_license_new_exists(tmp_path: Path):
    out = tmp_path / "LICENSE"
    out.write_text("old", encoding="utf-8")
    r = runner.invoke(app, ["license", "new", "MIT", "-o", str(out)])
    assert r.exit_code == 1


def test_cli_license_new_force(tmp_path: Path):
    out = tmp_path / "LICENSE"
    out.write_text("old", encoding="utf-8")
    r = runner.invoke(app, ["license", "new", "MIT", "-o", str(out), "-f"])
    assert r.exit_code == 0


def test_cli_license_invalid():
    r = runner.invoke(app, ["license", "show", "NOPE"])
    assert r.exit_code == 1


#gitignore


def test_combine_gitignores():
    text = combine_gitignores(["python", "node"])
    assert "Python" in text
    assert "Node" in text


def test_combine_invalid():
    with pytest.raises(ValueError):
        combine_gitignores(["nope"])


def test_list_gitignores_contains_common():
    names = list_gitignores()
    for key in ("python", "node", "go", "rust"):
        assert key in names


def test_cli_gitignore_list():
    r = runner.invoke(app, ["gitignore", "list"])
    assert r.exit_code == 0
    assert "python" in r.stdout


def test_cli_gitignore_show():
    r = runner.invoke(app, ["gitignore", "show", "python"])
    assert r.exit_code == 0
    assert "__pycache__" in r.stdout


def test_cli_gitignore_new(tmp_path: Path):
    out = tmp_path / ".gitignore"
    r = runner.invoke(
        app, ["gitignore", "new", "python", "node", "-o", str(out)]
    )
    assert r.exit_code == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "__pycache__" in content
    assert "node_modules" in content


def test_cli_gitignore_new_exists(tmp_path: Path):
    out = tmp_path / ".gitignore"
    out.write_text("old", encoding="utf-8")
    r = runner.invoke(app, ["gitignore", "new", "python", "-o", str(out)])
    assert r.exit_code == 1


def test_cli_gitignore_append(tmp_path: Path):
    out = tmp_path / ".gitignore"
    out.write_text("# old\n", encoding="utf-8")
    r = runner.invoke(
        app, ["gitignore", "new", "python", "-o", str(out), "--append"]
    )
    assert r.exit_code == 0
    content = out.read_text(encoding="utf-8")
    assert "# old" in content
    assert "__pycache__" in content


#scaffold


def test_cli_scaffold_python(tmp_path: Path):
    r = runner.invoke(
        app, ["scaffold", "python", "myproj", "-t", str(tmp_path)]
    )
    assert r.exit_code == 0
    root = tmp_path / "myproj"
    assert (root / "pyproject.toml").exists()
    assert (root / "src" / "myproj" / "main.py").exists()
    assert (root / "tests" / "test_main.py").exists()


def test_cli_scaffold_node(tmp_path: Path):
    r = runner.invoke(
        app, ["scaffold", "node", "app", "-t", str(tmp_path)]
    )
    assert r.exit_code == 0
    root = tmp_path / "app"
    assert (root / "package.json").exists()
    assert (root / "src" / "index.js").exists()


def test_cli_scaffold_invalid_kind(tmp_path: Path):
    r = runner.invoke(
        app, ["scaffold", "nope", "proj", "-t", str(tmp_path)]
    )
    assert r.exit_code == 1


def test_cli_scaffold_exists(tmp_path: Path):
    (tmp_path / "proj").mkdir()
    r = runner.invoke(
        app, ["scaffold", "python", "proj", "-t", str(tmp_path)]
    )
    assert r.exit_code == 1


def test_cli_scaffold_force(tmp_path: Path):
    (tmp_path / "proj").mkdir()
    r = runner.invoke(
        app, ["scaffold", "python", "proj", "-t", str(tmp_path), "-f"]
    )
    assert r.exit_code == 0


def test_cli_scaffold_list():
    r = runner.invoke(app, ["scaffold", "--list"])
    assert r.exit_code == 0
    assert "python" in r.stdout
    assert "node" in r.stdout


def test_cli_scaffold_missing_args():
    r = runner.invoke(app, ["scaffold"])
    assert r.exit_code == 1


#template


def test_render_template_simple():
    result = render_template("Hello {{ name }}!", {"name": "Ali"})
    assert result == "Hello Ali!"


def test_render_template_no_spaces():
    result = render_template("Hi {{name}}", {"name": "Sara"})
    assert result == "Hi Sara"


def test_render_template_missing_kept():
    result = render_template("Hello {{ missing }}", {})
    assert "{{ missing }}" in result


def test_render_template_multiple():
    result = render_template(
        "{{a}} {{b}} {{a}}", {"a": "1", "b": "2"}
    )
    assert result == "1 2 1"


def test_find_variables():
    vars = find_variables("{{a}} {{ b }} {{a}} {{c}}")
    assert vars == ["a", "b", "c"]


def test_find_variables_empty():
    assert find_variables("no vars here") == []


def test_cli_template_render(tmp_path: Path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("Hello {{name}} from {{city}}", encoding="utf-8")
    r = runner.invoke(
        app,
        ["template", str(tpl), "-D", "name=Ali", "-D", "city=Tehran"],
    )
    assert r.exit_code == 0
    assert "Ali" in r.stdout
    assert "Tehran" in r.stdout


def test_cli_template_output(tmp_path: Path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("x={{x}}", encoding="utf-8")
    out = tmp_path / "out.txt"
    r = runner.invoke(
        app, ["template", str(tpl), "-D", "x=42", "-o", str(out)]
    )
    assert r.exit_code == 0
    assert out.read_text(encoding="utf-8") == "x=42"


def test_cli_template_missing_file():
    r = runner.invoke(app, ["template", "no-file.txt"])
    assert r.exit_code == 1


def test_cli_template_bad_var(tmp_path: Path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("x", encoding="utf-8")
    r = runner.invoke(app, ["template", str(tpl), "-D", "nope"])
    assert r.exit_code == 1


def test_cli_template_vars(tmp_path: Path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("{{a}} {{b}}", encoding="utf-8")
    r = runner.invoke(app, ["template", str(tpl), "--vars"])
    assert r.exit_code == 0
    assert "a" in r.stdout
    assert "b" in r.stdout


def test_cli_template_vars_empty(tmp_path: Path):
    tpl = tmp_path / "t.txt"
    tpl.write_text("no vars", encoding="utf-8")
    r = runner.invoke(app, ["template", str(tpl), "--vars"])
    assert r.exit_code == 0