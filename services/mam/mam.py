import html
import json
import os
import re
import subprocess
import tempfile
import threading
import time
import warnings

from pathlib import Path
from typing import Any

import requests

from flask import Flask, abort, jsonify, render_template, request
from qbittorrentapi import Client, TorrentDictionary

app = Flask(__name__)
warnings.simplefilter("ignore")

MAM_URL = "https://www.myanonamouse.net"
MAM_EBOOKS_CATEGORY = "14"
USER_AGENT = "ruby-mam-books"

BOOKS_PATH = os.environ["BOOKS_PATH"]
STATE_DIR = Path(os.environ["STATE_DIR"])
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

QBT_CATEGORY = os.environ.get("QBT_CATEGORY", "Books")
TAG_PENDING = "pending-import"
TAG_IMPORTED = "imported"
TAG_FAILED = "import-failed"
OUR_TAGS = (TAG_PENDING, TAG_IMPORTED, TAG_FAILED)

CALIBRE_TAG = "unorganized"

# These are converted to EPUB on import, and only the EPUB is added to the library.
CONVERT_TO_EPUB = (".azw3", ".mobi", ".azw", ".fb2", ".docx", ".rtf")
# When a torrent has a book in more than one format, the earliest one in this list is imported.
# PDFs are imported as-is because converting them to EPUB gives poor results.
FORMAT_PRIORITY = (".epub", *CONVERT_TO_EPUB, ".pdf")


class MamError(Exception):
    pass


class Mam:
    """
    Talks to MAM using a mam_id session cookie.

    MAM can hand back a new mam_id in any response, so the latest value is saved to disk and
    reused after a restart. If MAM_ID is changed in the environment (e.g. after creating a new
    session), the saved value is discarded in favour of the new one.
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.state_file = STATE_DIR / "mam_id.json"
        self.initial = os.environ["MAM_ID"]
        self.mam_id = self.initial
        try:
            state = json.loads(self.state_file.read_text())
            if state.get("initial") == self.initial and state.get("current"):
                self.mam_id = state["current"]
        except (OSError, ValueError):
            pass

    def search(self, query: str, epub_only: bool = True) -> list[dict[str, Any]]:
        params = {
            "tor[text]": query,
            "tor[srchIn][title]": "true",
            "tor[srchIn][author]": "true",
            "tor[srchIn][series]": "true",
            "tor[searchType]": "all",
            "tor[searchIn]": "torrents",
            "tor[main_cat][]": MAM_EBOOKS_CATEGORY,
            "tor[sortType]": "default",
            "tor[startNumber]": "0",
            "perpage": "100",
        }
        resp = self.get("/tor/js/loadSearchJSONbasic.php", params)
        try:
            body = resp.json()
        except ValueError:
            raise MamError("MAM did not return JSON. Is MAM_ID valid for this IP?")
        if "error" in body:
            if str(body["error"]).startswith("Nothing returned"):
                return []
            raise MamError(f"MAM search failed: {body['error']}")
        results = [parse_result(row) for row in body.get("data", [])]
        if epub_only:
            results = [r for r in results if "epub" in r["filetypes"]]
        return results

    def torrent_file(self, tid: int) -> bytes:
        resp = self.get("/tor/download.php", {"tid": str(tid)})
        # A .torrent file is a bencoded dictionary, so it always starts with "d".
        if not resp.content.startswith(b"d"):
            raise MamError("MAM did not return a torrent file. Is MAM_ID valid for this IP?")
        return resp.content

    def get(self, path: str, params: dict[str, str]) -> requests.Response:
        with self.lock:
            resp = requests.get(
                f"{MAM_URL}{path}",
                params=params,
                cookies={"mam_id": self.mam_id},
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            new_id = resp.cookies.get("mam_id")
            if new_id and new_id != self.mam_id:
                self.save(new_id)
        if resp.status_code != 200:
            raise MamError(f"MAM returned HTTP {resp.status_code}")
        return resp

    def save(self, mam_id: str) -> None:
        self.mam_id = mam_id
        try:
            state = {"initial": self.initial, "current": mam_id}
            self.state_file.write_text(json.dumps(state))
        except OSError as e:
            log(f"Could not save the new mam_id, it will be lost on restart: {e}")


def parse_result(row: dict[str, Any]) -> dict[str, Any]:
    tid = row["id"]
    series = []
    for value in json_field(row.get("series_info")).values():
        if isinstance(value, list) and value:
            name = html.unescape(str(value[0]))
            index = str(value[1]) if len(value) > 1 and value[1] not in ("", None) else ""
            series.append(f"{name} #{index}" if index else name)
    return {
        "id": tid,
        # Titles can be numeric (e.g. 1984), so always coerce to a string.
        "title": html.unescape(str(row.get("title", ""))),
        "authors": [html.unescape(str(a)) for a in json_field(row.get("author_info")).values()],
        "series": series,
        "lang": row.get("lang_code") or "",
        "size": row.get("size") or "",
        "filetypes": str(row.get("filetype") or "").lower().split(),
        "seeders": row.get("seeders"),
        "leechers": row.get("leechers"),
        "snatches": row.get("times_completed"),
        "added": row.get("added") or "",
        "free": truthy(row.get("free")) or truthy(row.get("personal_freeleech")),
        "vip": truthy(row.get("vip")),
        "snatched": truthy(row.get("my_snatched")),
        "url": f"{MAM_URL}/t/{tid}",
    }


def json_field(value: Any) -> dict[str, Any]:
    # MAM returns some fields (e.g. author_info) as JSON-encoded strings.
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def truthy(value: Any) -> bool:
    return str(value).strip().lower() not in ("", "0", "false", "none")


mam = Mam()
_qbt: Client | None = None


def qbt() -> Client:
    global _qbt
    if _qbt is None:
        _qbt = Client(
            host=os.environ["QBT_HOST"],
            port=os.environ["QBT_PORT"],
            username=os.environ["QBT_USERNAME"],
            password=os.environ["QBT_PASSWORD"],
            REQUESTS_ARGS={"timeout": 30},
        )
    return _qbt


def add_torrent(tid: int) -> None:
    data = mam.torrent_file(tid)
    client = qbt()
    if QBT_CATEGORY not in client.torrents_categories():
        client.torrents_create_category(QBT_CATEGORY)
    result = client.torrents_add(
        torrent_files={f"{tid}.torrent": data},
        category=QBT_CATEGORY,
        tags=TAG_PENDING,
    )
    if result == "Fails.":
        raise MamError("qBittorrent rejected the torrent. Has it already been added?")
    log(f"Added MAM torrent {tid} to qBittorrent")


def import_completed() -> None:
    """Import every finished torrent tagged as pending into Calibre."""
    for t in qbt().torrents_info(category=QBT_CATEGORY, tag=TAG_PENDING):
        if t.amount_left > 0 or t.state.startswith("checking") or t.state == "moving":
            continue
        try:
            import_torrent(t)
        except Exception as e:
            log(f"Failed to import {t.name}: {e}")
            t.remove_tags(TAG_PENDING)
            t.add_tags(TAG_FAILED)
        else:
            t.remove_tags(TAG_PENDING)
            t.add_tags(TAG_IMPORTED)


def import_torrent(t: TorrentDictionary) -> None:
    # The torrent's files stay where they are so that it keeps seeding; calibredb makes a copy.
    files = choose_files([Path(t.save_path) / f.name for f in t.files])
    if not files:
        raise MamError("the torrent has no supported ebook files")
    for path in files:
        if not path.is_file():
            raise MamError(f"{path} does not exist. Is the torrents directory mounted?")
    errors = []
    for path in files:
        try:
            import_file(path)
        except Exception as e:
            errors.append(f"{path.name}: {e}")
    if errors:
        raise MamError("; ".join(errors))


def choose_files(paths: list[Path]) -> list[Path]:
    """
    Pick the best format of each book in a torrent.

    Files with the same name but different extensions (e.g. Book.mobi and Book.pdf, even in
    different folders) are treated as one book, so that it isn't added twice.
    """
    books: dict[str, list[Path]] = {}
    for path in paths:
        if path.suffix.lower() in FORMAT_PRIORITY:
            books.setdefault(path.stem.lower(), []).append(path)
    chosen = []
    for candidates in books.values():
        best = min(FORMAT_PRIORITY.index(p.suffix.lower()) for p in candidates)
        chosen.extend(p for p in candidates if FORMAT_PRIORITY.index(p.suffix.lower()) == best)
    return sorted(chosen)


def import_file(path: Path) -> None:
    if path.suffix.lower() not in CONVERT_TO_EPUB:
        book_id = calibredb_add(path)
        log(f"Imported {path.name} as book {book_id}")
        return
    # Only the EPUB goes into the library. The converted copy lives in a temporary directory, and
    # the original is left alone because it belongs to the torrent.
    with tempfile.TemporaryDirectory() as tmp:
        epub = Path(tmp) / f"{path.stem}.epub"
        run(["ebook-convert", str(path), str(epub)], timeout=900)
        book_id = calibredb_add(epub)
    log(f"Converted {path.name} to EPUB and imported it as book {book_id}")


def calibredb_add(path: Path) -> int:
    cmd = ["calibredb", "add", "--with-library", BOOKS_PATH, "--tags", CALIBRE_TAG, str(path)]
    output = run(cmd)
    # calibredb exits successfully when it skips duplicates, so check that something was added.
    match = re.search(r"Added book ids: (\d+)", output)
    if not match:
        raise MamError(f"calibredb did not add it (already in the library?): {output}")
    return int(match.group(1))


def run(cmd: list[str], timeout: int = 300) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0:
        # ebook-convert is very chatty, so only keep the end of its output.
        tail = "\n".join(output.splitlines()[-10:])
        raise MamError(f"{Path(cmd[0]).name} exited with {proc.returncode}: {tail}")
    return output


def poll_forever() -> None:
    while True:
        try:
            import_completed()
        except Exception as e:
            log(f"Import poll failed: {e}")
        time.sleep(POLL_INTERVAL)


def recent_torrents() -> list[dict[str, Any]]:
    torrents = []
    for t in qbt().torrents_info(category=QBT_CATEGORY, sort="added_on", reverse=True):
        tags = [tag.strip() for tag in t.tags.split(",")]
        status = next((tag for tag in OUR_TAGS if tag in tags), None)
        if status:
            torrents.append(
                {
                    "name": t.name,
                    "progress": round(t.progress * 100),
                    "state": t.state,
                    "status": status,
                }
            )
    return torrents[:25]


@app.route("/")
def index() -> str:
    query = request.args.get("q", "").strip()
    all_formats = request.args.get("formats") == "all"
    results, error, status_error = None, None, None
    if query:
        try:
            results = mam.search(query, epub_only=not all_formats)
        except (MamError, requests.RequestException) as e:
            error = str(e)
    try:
        torrents = recent_torrents()
    except Exception as e:
        torrents, status_error = [], f"Could not reach qBittorrent: {e}"
    return render_template(
        "index.html",
        query=query,
        all_formats=all_formats,
        results=results,
        error=error,
        torrents=torrents,
        status_error=status_error,
    )


@app.route("/download/<int:tid>", methods=["POST"])
def download(tid: int) -> Any:
    # Browsers can't send this header cross-site without a CORS preflight, so this stops other
    # websites from triggering downloads with a plain form post.
    if request.headers.get("X-Requested-With") != "fetch":
        abort(403)
    try:
        add_torrent(tid)
    except Exception as e:
        log(f"Failed to add MAM torrent {tid}: {e}")
        return jsonify(error=str(e)), 502
    return jsonify(ok=True)


def log(msg: str) -> None:
    print(msg, flush=True)


threading.Thread(target=poll_forever, daemon=True).start()
