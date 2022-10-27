FROM python:3.11-slim
RUN pip install requests && useradd -m qbt
USER qbt
WORKDIR /home/qbt
COPY netlify.py .
CMD python netlify.py
