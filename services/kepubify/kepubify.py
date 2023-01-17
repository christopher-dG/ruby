import os
import subprocess
import time

from pathlib import Path
from tempfile import gettempdir
from threading import Thread

from flask import Flask, Response, render_template_string, send_file

app = Flask(__name__)

INDEX = """
<!doctype html>
<html lang="en">
  <body>
    <ul>
      {% for book in books %}
      <li style="margin: 10px">
        <a href="/kepubify/{{ book.id }}" style="color: black; text-decoration: none">{{ book.name }}</a>
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
    Thread(target=defer_delete, args=(kepub,)).start()
    return send_file(kepub, mimetype="application/epub+zip", as_attachment=True)


def list_books() -> list[tuple[int, Path]]:
    root = Path(os.environ["BOOKS_PATH"])
    return list(enumerate(sorted(root.glob("*/*/*.epub"))))


def render(books: list[tuple[int, Path]]) -> str:
    ctx = {"books": [{"index": i, "name": path.name} for (i, path) in books]}
    return render_template_string(INDEX, **ctx)


def convert(path: Path) -> Path:
    out = (Path(gettempdir()) / path.name).with_suffix(".kepub.epub")
    log(f"Converting {path} to {out}")
    subprocess.run(["kepubify", "--output", out, path], check=True)
    return out


def defer_delete(path: Path) -> None:
    log(f"Deleting {path} in 5 minutes")
    time.sleep(300)
    path.unlink()
    log(f"Deleted {path}")


def log(msg: str) -> bool:
    print(msg, flush=True)
    return True
