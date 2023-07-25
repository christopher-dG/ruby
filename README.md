This is my home server configuration.

Services currently running:

- [Portainer](https://portainer.io): Admin console for Docker containers.
- [Caddy](https://caddyserver.com): Web server that proxies to the below services and provides a static file server.
- [WireGuard](https://wireguard.com): VPN client that other services can tunnel through.
- [qBittorrent](https://qbittorrent.org): BitTorrent client which tunnels through the VPN.
- [Radarr](https://radarr.video): Movie collection manager.
- [Sonarr](https://sonarr.tv): TV show collection manager.
- [Prowlarr](https://prowlarr.com): Indexer manager for Radarr and Sonarr.
- [Bazarr](https://www.bazarr.media): Subtitle manager.
- [Tdarr](https://https://tdarr.io): Video transcoding manager for saving disk space.
- [Plex](https://plex.tv): Media player frontend.
- [Tautulli](https://tautulli.com): Nifty metrics for the Plex server.
- [Calibre-Web](https://github.com/janeczku/calibre-web): Web frontend my Calibre book library.
- azw3: A wrapper around [ebook-convert](https://manual.calibre-ebook.com/generated/en/ebook-convert.html) for on-demand book conversion (I can skip Calibre and download books directly onto my Kindle!).

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
