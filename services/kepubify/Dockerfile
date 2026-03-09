FROM lscr.io/linuxserver/calibre
RUN useradd -m kepubify && \
    curl -Lo /usr/local/bin/kepubify https://github.com/pgaskin/kepubify/releases/latest/download/kepubify-linux-64bit && \
    chmod +x /usr/local/bin/kepubify
COPY requirements.txt .
RUN pip install -r requirements.txt
USER kepubify
WORKDIR /home/kepubify
COPY kepubify.py .
ENTRYPOINT []
CMD ["gunicorn", "--bind", "0.0.0.0:5555", "kepubify:app"]
