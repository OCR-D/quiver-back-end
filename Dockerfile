FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get -y install make && \
    apt-get -y install git

COPY . .

RUN pip install -r requirements.txt && \
     pip install .

ENTRYPOINT [ "make", "all" ]
#ENTRYPOINT [ "bash" ]