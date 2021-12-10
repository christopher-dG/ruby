import os
import time

from plexapi.server import PlexServer as Plex
from qbittorrentapi import Client as Qbt

PLEX_HOST = "http://plex:32400"
QBT_HOST = "89.36.78.149"
QBT_PORT = 55082

plex = Plex(PLEX_HOST, os.environ["PLEX_TOKEN"])
qbt = Qbt(host=QBT_HOST, port=QBT_PORT, username="admin", password=os.environ["QBT_PASSWORD"])
qbt.auth_log_in()

while True:
    limit = 0
    for s in plex.sessions():
        for p in s.players:
            if not p.address.startswith("192.168.0."):
                limit = 1
    qbt.transfer_set_upload_limit(limit)
    to_seed = 0
    for t in qbt.torrents_info():
        to_seed += t.total_size * (1.5 - t.ratio)
    print(f"To seed: {round(to_seed / 1_000_000_000)} GiB", flush=True)
    time.sleep(10)
