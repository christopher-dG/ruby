FROM python:3.11-slim
RUN useradd -m azw3 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      dbus \
      fcitx-rime \
      fonts-wqy-microhei \
      jq \
      libnss3 \
      libopengl0 \
      libqpdf28 \
      libxkbcommon-x11-0 \
      libxcb-icccm4 \
      libxcb-image0 \
      libxcb-keysyms1 \
      libxcb-randr0 \
      libxcb-render-util0 \
      libxcb-xinerama0 \
      poppler-utils \
      ttf-wqy-zenhei \
      xz-utils && \
    version="$(curl -s https://api.github.com/repos/kovidgoyal/calibre/releases/latest | jq -r .tag_name | cut -c2-)" && \
    # curl -Lo calibre.txz "https://download.calibre-ebook.com/$version/calibre-$version-x86_64.txz" && \
    curl -Lo calibre.txz "https://github.com/kovidgoyal/calibre/releases/download/v$version/calibre-$version-x86_64.txz" && \
    mkdir /opt/calibre && \
    tar xvf calibre.txz -C /opt/calibre && \
    /opt/calibre/calibre_postinstall && \
    rm calibre.txz
COPY requirements.txt .
RUN pip install -r requirements.txt
USER azw3
WORKDIR /home/azw3
COPY azw3.py .
CMD gunicorn --bind 0.0.0.0:5555 azw3:app
