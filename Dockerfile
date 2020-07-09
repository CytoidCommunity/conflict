FROM python

COPY . /app

RUN cd /app && \
    pip install --no-cache-dir .[mirai] && \
    mkdir data

WORKDIR /app/data
