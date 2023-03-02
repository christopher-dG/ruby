import os
import re

from datetime import timedelta

import requests

from qbittorrentapi import Client

DATA_DIR = os.environ["DATA_DIR"]
ARR_CATAGORIES = ["Books", "Movies", "TV"]  # Managed by *arr apps, we can skip them.


def iter_torrents(qbt):
    for t in qbt.torrents.info():
        if t.category in ARR_CATAGORIES:
            continue
        if t.amount_left == 0:
            dest_dir = os.path.join(DATA_DIR, t.category.lower(), t.name)
            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)
            for f in t.files:
                src_file = os.path.join(t.save_path, f.name)
                dest_file = os.path.join(dest_dir, os.path.basename(f.name))
                if not os.path.isfile(dest_file) and not has_been_converted(dest_file):
                    print(f"Linking {src_file} -> {dest_file}", flush=True)
                    os.link(src_file, dest_file)
            if is_finished(t):
                print(f"Deleting {t.name}", flush=True)
                t.delete(delete_files=True)


def has_been_converted(path):
    if not path.endswith(".mp4"):
        return False
    return os.path.isfile(re.sub(r"\.mp4$", ".mkv", path))


def is_finished(t):
    if t.amount_left > 0:
        return False
    if t.max_ratio > 0:
        if t.ratio >= t.max_ratio:
            return True
    if t.max_seeding_time > 0:
        seeding_time = timedelta(seconds=t.seeding_time)
        max_seeding_time = timedelta(minutes=t.max_seeding_time)
        if seeding_time >= max_seeding_time:
            return True
    return False


def check_ip(qbt):
    current_ip = requests.get("https://httpbin.org/ip").json()["origin"]
    key = "bypass_auth_subnet_whitelist"
    configured_ip = qbt.app.preferences[key].split("/")[0]
    if current_ip != configured_ip:
        print(f"Updating home IP to {current_ip}", flush=True)
        qbt.app.set_preferences({key: f"{current_ip}/32"})


if __name__ == "__main__":
    qbt = Client(
        host=os.environ["QBT_HOST"],
        port=os.environ["QBT_PORT"],
        username=os.environ["QBT_USERNAME"],
        password=os.environ["QBT_PASSWORD"],
    )
    qbt.auth.log_in()
    iter_torrents(qbt)
    check_ip(qbt)
