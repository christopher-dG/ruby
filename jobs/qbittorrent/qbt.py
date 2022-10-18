import os

import requests

from qbittorrentapi import Client

DATA_DIR = os.environ["DATA_DIR"]
ARR_CATAGORIES = ["Movies", "TV"]  # Managed by Radarr/Sonarr/etc.


def iter_torrents(qbt):
    to_upload = 0
    for t in qbt.torrents.info():
        to_upload += t.total_size * (t.max_ratio - t.ratio)
        if t.category in ARR_CATAGORIES:
            continue
        if t.amount_left == 0:
            dest_dir = os.path.join(DATA_DIR, t.category.lower(), t.name)
            if not os.path.isdir(dest_dir):
                os.mkdir(dest_dir)
            for f in t.files:
                src_file = os.path.join(t.save_path, f.name)
                dest_file = os.path.join(dest_dir, os.path.basename(f.name))
                if not os.path.isfile(dest_file):
                    print(f"Moving {src_file} -> {dest_file}")
                    os.link(src_file, dest_file)
        if t.ratio >= t.max_ratio:
            t.delete(delete_files=True)
    print(f"To upload: {round(to_upload / 1_000_000_000)} GiB", flush=True)


def check_ip(qbt):
    current_ip = requests.get("https://httpbin.org/ip").json()["origin"]
    key = "bypass_auth_subnet_whitelist"
    configured_ip = qbt.app.preferences[key].split("/")[0]
    if current_ip != configured_ip:
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
