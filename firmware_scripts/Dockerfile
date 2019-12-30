FROM jedie/micropython:latest

ARG DOCKER_UID
ENV DOCKER_UID $DOCKER_UID

ARG DOCKER_UGID
ENV DOCKER_UGID $DOCKER_UGID

USER root

RUN set -x \
    && id \
    && rm /etc/passwd \
    && rm /etc/group \
    && addgroup --system -gid 0 root \
    && adduser --system --uid 0 -gid 0 root \
    && addgroup --system -gid $DOCKER_UGID mpy \
    && adduser --system --shell="/bin/bash" --uid $DOCKER_UID -gid $DOCKER_UGID mpy \
    && mkdir -p /mpy/firmware_scripts/ \
    && chown mpy:mpy -Rf /mpy/firmware_scripts/ \
    && mkdir -p /mpy/micropython/ports/esp8266/src/ \
    && chown mpy:mpy -Rf /mpy/micropython/ports/esp8266/src/ \
    && mkdir -p /build/ \
    && chown mpy:mpy -Rf /build/

USER mpy
