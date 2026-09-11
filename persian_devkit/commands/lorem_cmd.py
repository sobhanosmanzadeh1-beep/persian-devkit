"""دستور pdev lorem — تولید متن نمونهٔ فارسی."""
from __future__ import annotations

import typer
from rich.console import Console

from persian_devkit.utils.fake_utils import (
    lorem_ipsum,
    random_paragraph,
    random_sentence,
    random_words,
)

app = typer.Typer(help="تولید متن نمونهٔ فارسی.", no_args_is_help=True)
console = Console()


@app.command("paragraph")
def paragraph_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=100),
    sentences: int = typer.Option(4, "--sentences", "-s", min=1, max=20),
) -> None:
    """تولید پاراگراف متن نمونه."""
    for i in range(count):
        if i > 0:
            console.print()
        console.print(random_paragraph(sentences))


@app.command("sentence")
def sentence_cmd(
    count: int = typer.Option(1, "--count", "-c", min=1, max=100),
) -> None:
    """تولید جملهٔ تصادفی."""
    for _ in range(count):
        console.print(random_sentence())


@app.command("words")
def words_cmd(
    count: int = typer.Option(5, "--count", "-c", min=1, max=200),
) -> None:
    """تولید چند کلمهٔ تصادفی فارسی."""
    console.print(random_words(count))


@app.command("all")
def all_cmd(
    paragraphs: int = typer.Option(3, "--paragraphs", "-p", min=1, max=20),
    sentences: int = typer.Option(4, "--sentences", "-s", min=1, max=20),
) -> None:
    """تولید چند پاراگراف متن کامل."""
    console.print(lorem_ipsum(paragraphs=paragraphs, sentences_per_paragraph=sentences))