import os
import time

from plexapi.server import PlexServer as Plex
from qbittorrentapi import Client as Qbt

PLEX_HOST = "http://plex:32400"
QBT_HOST = "89.36.78.149"
QBT_PORT = 57419

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
    time.sleep(10)
