FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev make socat \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /challenge

COPY Makefile ret2win.c ./
RUN make clean all \
    && useradd -r -u 10001 -m pwn \
    && chown -R root:root /challenge \
    && chmod 755 /challenge /challenge/ret2win

ENV BYTESEC_PWN_FLAG=BYTESEC{a18dc4f20b5e9a77}

EXPOSE 9001

USER pwn
CMD ["socat", "-dd", "TCP-LISTEN:9001,reuseaddr,fork", "EXEC:/challenge/ret2win,stderr"]
