This is my home server configuration.

Services currently running:

- [Portainer](https://portainer.io): Admin console for Docker containers.
- [Caddy](https://caddyserver.com): Web server that proxies to the below services and provides a static file server.
- [WireGuard](https://wireguard.com): VPN client that other services can tunnel through.
- [qBittorrent](https://qbittorrent.org): BitTorrent client which tunnels through the VPN.
- [Radarr](https://radarr.video): Movie collection manager.
- [Sonarr](https://sonarr.tv): TV show collection manager.
- [Plex](https://plex.tv): Media player frontend.
- [Tautulli](https://tautulli.com): Nifty metrics for the Plex server.
- [Calibre-Web](https://github.com/janeczku/calibre-web): Web frontend my Calibre book library.
- [Heimdall](https://heimdall.site): Web homepage with links to all the above services on my local network.

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
