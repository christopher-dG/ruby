# Chris's server: info for users

---

## Contents

- [Plex](#plex-plexcdgdev)
- [Calibre-Web](#calibre-web-bookscdgdev)
- [Kepubify](#kepubify-kepubifycdgdev)

---

## Plex (plex.cdg.dev)

Plex is for watching TV and movies.
It plays personal libraries like mine, and also has its own library of free content.
My Plex server's name is "ruby", so if you see references to that, you know it's mine.

### Getting access

- Make an account at https://plex.tv/sign-up.
- Tell me either your username or the email you used, and I will send an invite via email.

### Optimizing settings

The default settings are not great.
They make it hard to find my library instead of their own library of content, and will limit your default streaming quality.
You'll want to:

Here are some useful guides to configure some reasonable settings.
If any of these links are broken, please let me know!

- [A comprehensive guide on all settings](https://imgur.com/a/plexplainers-reupload-ZeyElPK)
- [A specific guide on setting default quality on any device](https://redd.it/mora8f)

### Installing Plex on your devices

Plex has apps for most smart TVs, mobile devices, and TV streaming devices, and installation will vary depending on what you have.
If you have no idea where to start, ask me and I can help.
For the best performance, I recommend not using a TV app and instead using some kind of external streaming device.

### Making requests

To request shows/movies to be added to Plex, you have two options:

1. Ask me to add it for you.
2. Use [Overseerr](#overseerr) to add it yourself.

#### Overseerr

[Overseerr](https://overseerr.dev) is a system for request management.
You can log in at https://overseerr.cdg.dev with your Plex account.
Then just type in the search bar to find what you're looking for.
If you've requested something a while ago but it's still not on Plex, let me know.

### Troubleshooting

#### Playback is buffering/freezing a lot

Your connection might be too slow for the original quality, in which case you will want to change the quality.
Where this setting is found differs between devices, but I believe in you to find it.
The important thing to look at is the *bitrate*, which will be expressed in Megabits per second (Mbps).
Lower numbers should play more smoothly, but will look worse.

#### Everything you stream is really low quality

Chances are your Internet connection or your settings are causing the media to be converted to a low quality.
Make sure you've followed the instructions in [Optimizing settings](#optimizing-settings) to change your default streaming quality.

#### A movie/TV show is corrupt or otherwise not playing

Let me know what you're trying to watch, and I'll make sure to download a working version.
If *nothing* is playing, you probably have other issues and I might be able to help you solve them.

#### A movie/TV show is bad quality

Lots of stuff is stored in relatively low quality to save disk space, especially if I won't be watching it myself.
Let me know what you're watching, and I can download a better version.

---

## Calibre-Web (books.cdg.dev)

[Calibre-Web](https://github.com/janeczku/calibre-web) is a system for managing ebook libraries.
You can log in at https://books.cdg.dev to download ebooks for use on a Kindle, Kobo or similar ereader.
If you have a Kobo, you might be interested in using [kepubify](#kepubify-kepubifycdgdev) instead.

### Getting access

Ask Chris for access.

### Downloading books

It's pretty self-explanatory: click on a book, then click the "Download" icon and then EPUB in the drop-down menu.
I would recommend using [Calibre](https://calibre-ebook.com/download) on your computer to get the ebook onto your device.

### Making requests

Ask Chris for any books you want added.

---

## Kepubify (kepubify.cdg.dev)

This is a service specifically for downloading ebooks onto Kobo devices from the Kobo web browser, so that you can avoid connecting your Kobo to a computer.

### Downloading books

- Connect your Kobo to WiFi, then go to "Beta features", then "Experimental web browser".
- Navigate to https://kepubify.cdg.dev.
  You should see a long list of books.
  These books come from [Calibre-Web](#calibre-web-bookscdgdev), so if you don't see what you want, follow the instructions in that section for requesting it.
- To filter books, add part of the title or author to the URL.
  You should then be able to find the book you're looking for without scrolling.
  For example, https://kepubify.cdg.dev/tchaik should show you books by Adrian Tchaikovsky and not much else.
- Click the book (you might need to pinch to zoom in), then follow the prompts to download it. The book will now be available in your Kobo's library.

<!--
## Immich (immich.cdg.dev)

Immich is a photo and video hosting service.
I have not yet decided if I will share this service, so don't ask me about it yet.

*TODO*
-->
