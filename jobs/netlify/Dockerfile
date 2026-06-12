FROM python:3.14-slim
RUN pip install requests && useradd -m qbt
USER qbt
WORKDIR /home/qbt
COPY netlify.py .
CMD python netlify.py
