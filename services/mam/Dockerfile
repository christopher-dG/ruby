FROM lscr.io/linuxserver/calibre
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY mam.py .
COPY templates templates
# The container runs as an arbitrary UID (see docker-compose.yml), so give calibredb somewhere writable.
ENV HOME=/tmp CALIBRE_CONFIG_DIRECTORY=/tmp/calibre
ENTRYPOINT []
# One worker so that there is only one import poller; threads so that searches don't block each other.
CMD ["gunicorn", "--bind", "0.0.0.0:5556", "--workers", "1", "--threads", "4", "mam:app"]
