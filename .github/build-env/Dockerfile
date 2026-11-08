# Build environment for the twrp-5.1 (Android 5.1) source tree.
# Android 5.1 requires Java 7 and an old host toolchain, which modern Ubuntu lacks,
# so the compile runs inside Ubuntu 14.04. Source download happens on the host.
FROM ubuntu:14.04
RUN (apt-get update || ( \
      sed -i 's|http://archive.ubuntu.com|http://old-releases.ubuntu.com|g; s|http://security.ubuntu.com|http://old-releases.ubuntu.com|g' /etc/apt/sources.list \
      && apt-get update )) \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openjdk-7-jdk git-core gnupg flex bison gperf build-essential zip curl \
      zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev \
      x11proto-core-dev libx11-dev lib32z-dev libgl1-mesa-dev libxml2-utils \
      xsltproc unzip python bc rsync \
 && rm -rf /var/lib/apt/lists/*
ENV USER=root LANG=C.UTF-8

