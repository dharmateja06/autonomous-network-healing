FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
        iproute2 \
        iputils-ping \
        net-tools \
        tcpdump \
        curl \
        wget \
        openssh-server \
        python3 \
        python3-pip \
        && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd

CMD ["sleep", "infinity"]
