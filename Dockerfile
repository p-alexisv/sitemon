FROM python:3-slim
MAINTAINER avillalon@vmware.com

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY app.py ./

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED 1
ENV SITEMON_METRICSPORT 8000
ENV SITEMON_URLS "https://httpstat.us/503,https://httpstat.us/200"
ENV SITEMON_INTERVAL 60
CMD [ "python", "./app.py" ]

