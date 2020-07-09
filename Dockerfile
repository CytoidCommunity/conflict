FROM python

COPY . /app

RUN cd /app && \
    pip install --no-cache-dir . && \
    mkdir data

WORKDIR /app/data
