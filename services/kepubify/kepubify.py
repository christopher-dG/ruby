import os
import subprocess

from pathlib import Path
from tempfile import gettempdir

from flask import Flask, Response, render_template_string, send_file

app = Flask(__name__)

INDEX = """
<!doctype html>
<html lang="en">
  <body>
    <ul>
      {% for book in books %}
      <li style="margin: 10px">
        <a href="/kepubify/{{ book.index }}" style="color: black">{{ book.name }}</a>
      </li>
      {% endfor %}
    </ul>
  </body>
</html>
"""


@app.route("/")
def index() -> str:
    return render(list_books())


@app.route("/<string:sub>")
def filter(sub: str) -> str:
    sub = sub.lower()
    books = []
    for (i, path) in list_books():
        if sub in path.name.lower():
            books.append((i, path))
    return render(books)


@app.route("/kepubify/<int:i>")
def kepubify(i: int) -> Response:
    path = list_books()[i][1]
    kepub = convert(path)
    resp = send_file(kepub)
    resp.call_on_close(lambda: path.unlink())
    return resp


def list_books() -> list[tuple[int, Path]]:
    root = Path(os.environ["BOOKS_PATH"])
    return list(enumerate(sorted(root.glob("*/*/*.epub"))))


def render(books: list[tuple[int, Path]]) -> str:
    ctx = {"books": [{"index": i, "name": path.name} for (i, path) in books]}
    return render_template_string(INDEX, **ctx)


def convert(path: Path) -> Path:
    out = (Path(gettempdir()) / path).with_suffix(".kepub")
    subprocess.run(["kepubify", "--output", out, path], check=True)
    return out
