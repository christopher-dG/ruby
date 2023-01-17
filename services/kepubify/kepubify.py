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

from ebooklib import epub
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
        <a href="/kepubify/{{ book.id }}" style="color: black; text-decoration: none">{{ book.name }}</a>
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


@app.route("/kepubify/<int:book>")
def kepubify(book: int) -> Response:
    path = path_of_book(book)
    kepub = convert(fix_metadata(book, path))
    Thread(target=defer_delete, args=(kepub,)).start()
    return send_file(kepub, mimetype="application/epub+zip", as_attachment=True)


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


def fix_metadata(book: int, path: Path) -> Path:
    data = epub.read_epub(path)
    with db_cursor() as cur:
        (title,) = fetch_one(cur, "select title from books where id = ?", book)
        query = """
        select a.name, a.sort
        from books_authors_link as l join authors as a on l.author = a.id
        where l.book = ?
        """
        authors = fetch_all(cur, query, book)
    ns = "http://purl.org/dc/elements/1.1/"
    data.metadata[ns]["title"] = []
    data.metadata[ns]["creator"] = []
    data.set_title(title)
    log(f"Setting title to '{title}'")
    for (author, sort) in authors:
        log(f"Adding author '{author}'")
        data.add_author(author, file_as=sort)
    out = Path(gettempdir()) / path.name
    epub.write_epub(out, data)
    Thread(target=defer_delete, args=(out,)).start()
    return out


def convert(path: Path) -> Path:
    out = (Path(gettempdir()) / path.name).with_suffix(".kepub.epub")
    log(f"Converting {path} to {out}")
    subprocess.run(["kepubify", "--output", out, path], check=True)
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
