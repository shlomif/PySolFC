#!/bin/sh
set -e

# install as root

apt-get install -y \
  git \
  openjdk-8-jdk \
  cython3 \
  python3-pip \
  python3-yaml \
  virtualenv \
  pkg-config \
  automake autoconf libtool \
  zlib1g-dev \
  libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
  libtinfo5 \
  lld

update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
