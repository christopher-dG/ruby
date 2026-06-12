FROM python:3.14-slim
RUN pip install requests qbittorrent-api && useradd -m qbt
USER qbt
WORKDIR /home/qbt
COPY qbt.py .
CMD python qbt.py
