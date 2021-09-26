This is my home server configuration.

Services currently running:

- [Portainer](https://portainer.io): An admin console for Docker containers.
- [Caddy](https://caddyserver.com): A web server that proxies to the below services and provides a static file server.
- [WireGuard](https://wireguard.com): A VPN client that other services can tunnel through.
- [qBittorrent](https://qbittorrent.org): BitTorrent client which tunnels through the VPN.
- [Radarr](https://radarr.video): Movie collection manager.
- [Sonarr](https://sonarr.tv): TV show collection manager.
- [Plex](https://plex.tv): A media player frontend.
- [Calibre-Web](https://github.com/janeczku/calibre-web): A web frontend my Calibre book library.

Directory structure requirements:

```
.
├── config
│   └── wireguard
│       └── wg0.conf
└── data
    ├── books
    └── torrents
```

---

TODO: Automate this better (fstab?).

Mount Kobo inside container:

```sh
docker-compose exec calibre-desktop bash
mount -t vfat -o gid=$PGID,uid=$PUID /dev/sdc /mnt
```
