This is my home server configuration.

Services currently running:

- [Portainer](https://portainer.io): An admin console for Docker containers.
- [Caddy](https://caddyserver.com): A web server that proxies to the below services.
- [WireGuard](https://wireguard.com): A VPN client that other services can tunnel through.
- [qBittorrent](https://qbittorrent.org): BitTorrent client which tunnels through the VPN.
- [Plex](https://plex.tv): A media player frontend for the BitTorrent downloads.
- [Guacamole](https://guacamole.apache.org): A gateway for accessing desktop applications over a web browser.
- [Calibre](https://calibre-ebook.com): A book library manager accessed via Guacamole.
- [Calibre-Web](https://github.com/janeczku/calibre-web): A web frontend for the Calibre library.

Directory structure requirements:

```
.
├── config
│   └── wireguard
│       └── wg0.conf
└── data
    ├── books
    └── torrents
        ├── movies
        └── tv
```
