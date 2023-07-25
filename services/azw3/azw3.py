import os
import sqlite3
import subprocess
import time
import warnings

from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Cursor
from tempfile import gettempdir
from textwrap import dedent
from threading import Thread
from typing import Any, Generator

from flask import Flask, Response, render_template_string, send_file

app = Flask(__name__)
warnings.simplefilter("ignore")

BOOKS_PATH = Path(os.environ["BOOKS_PATH"])
INDEX = """
<!doctype html>
<html lang="en">
  <body>
    <ul>
      {% for book in books %}
      <li style="margin: 10px">
        <a href="/azw3/{{ book.id }}" style="color: black; text-decoration: none">{{ book.name }}</a>
      </li>
      {% endfor %}
    </ul>
  </body>
</html>
"""


@app.route("/")
@app.route("/<string:sub>")
def index(sub: str = "") -> str:
    return render_index(sub)


@app.route("/azw3/<int:book>")
def azw3(book: int) -> Response:
    path = path_of_book(book)
    output = convert(path)
    Thread(target=defer_delete, args=(output,)).start()
    # This technically is not the correct MIME type for AZW3, but Kindle requires it.
    return send_file(output, mimetype="application/x-mobipocket-ebook", as_attachment=True)


def render_index(sub: str = "") -> str:
    books = []
    with db_cursor() as cur:
        query = """
        select books.id, books.author_sort, books.title
        from books join data on books.id = data.book
        where data.format = 'EPUB'
        order by books.author_sort
        """
        for (id, author, title) in fetch_all(cur, query):
            name = f"{author} - {title}"
            if sub.lower() in name.lower():
                books.append({"id": id, "name": name})
    return render_template_string(INDEX, books=books)


def path_of_book(book: int) -> Path:
    with db_cursor() as cur:
        (dir,) = fetch_one(cur, "select path from books where id = ?", book)
        (file,) = fetch_one(
            cur, "select name from data where book = ? and format = 'EPUB'", book
        )
    return (BOOKS_PATH / dir / file).with_suffix(".epub")


def convert(path: Path) -> Path:
    out = (Path(gettempdir()) / path.name).with_suffix(".azw3")
    log(f"Converting {path} to {out}")
    args = ["ebook-convert", path, out]
    # This cover tomfoolery doesn't actually work, but oh well:
    # https://manual.calibre-ebook.com/faq.html#covers-for-books-i-send-to-my-e-ink-kindle-show-up-momentarily-and-then-are-replaced-by-a-generic-cover
    cover = path.parent / "cover.jpg"
    if cover.is_file():
        args.extend(["--cover", cover])
    subprocess.run(args, check=True)
    return out


def defer_delete(path: Path) -> None:
    log(f"Deleting {path} in 5 minutes")
    time.sleep(300)
    try:
        path.unlink()
        log(f"Deleted {path}")
    except:
        pass


def log(msg: str) -> bool:
    print(msg, flush=True)
    return True


@contextmanager
def db_cursor() -> Generator[Cursor, None, None]:
    conn = sqlite3.connect(BOOKS_PATH / "metadata.db")
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()
        conn.close()


def execute(cur: Cursor, query: str, *args: Any) -> Cursor:
    return cur.execute(dedent(query.strip()), args)


def fetch_one(cur: Cursor, query: str, *args: Any) -> tuple:
    return execute(cur, query, *args).fetchone()


def fetch_all(cur: Cursor, query: str, *args: Any) -> list[tuple]:
    return execute(cur, query, *args).fetchall()
