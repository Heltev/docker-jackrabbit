FROM openjdk:8-jre-alpine3.9

# ===============
# Alpine packages
# ===============

RUN apk update \
    && apk add --no-cache py3-pip \
    && apk add --no-cache --virtual build-deps wget

# =====
# Jetty
# =====

ARG JETTY_VERSION=9.4.24.v20191120
ARG JETTY_HOME=/opt/jetty
ARG JETTY_BASE=/opt/gluu/jetty
ARG JETTY_USER_HOME_LIB=/home/jetty/lib

# Install jetty
RUN wget -q https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-distribution/${JETTY_VERSION}/jetty-distribution-${JETTY_VERSION}.tar.gz -O /tmp/jetty.tar.gz \
    && mkdir -p /opt \
    && tar -xzf /tmp/jetty.tar.gz -C /opt \
    && mv /opt/jetty-distribution-${JETTY_VERSION} ${JETTY_HOME} \
    && rm -rf /tmp/jetty.tar.gz

# Ports required by jetty
EXPOSE 8080

# ==========
# Jackrabbit
# ==========

ARG JACKRABBIT_VERSION=2.21.1

# Install Jackrabbit
RUN wget -q https://downloads.apache.org/jackrabbit/${JACKRABBIT_VERSION}/jackrabbit-webapp-${JACKRABBIT_VERSION}.war -O /tmp/jackrabbit.war \
    && mkdir -p ${JETTY_BASE}/jackrabbit/webapps/jackrabbit \
    && unzip -qq /tmp/jackrabbit.war -d ${JETTY_BASE}/jackrabbit/webapps/jackrabbit \
    && java -jar ${JETTY_HOME}/start.jar jetty.home=${JETTY_HOME} jetty.base=${JETTY_BASE}/jackrabbit --add-to-start=server,deploy,annotations,resources,http,http-forwarded,threadpool,jsp,websocket \
    && rm -f /tmp/jackrabbit.war

# ====
# Tini
# ====

RUN wget -q https://github.com/krallin/tini/releases/download/v0.18.0/tini-static -O /usr/bin/tini \
    && chmod +x /usr/bin/tini

# ======
# rclone
# ======

ARG RCLONE_VERSION=v1.51.0
RUN wget -q https://github.com/rclone/rclone/releases/download/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip -O /tmp/rclone.zip \
    && unzip -qq /tmp/rclone.zip -d /tmp \
    && mv /tmp/rclone-${RCLONE_VERSION}-linux-amd64/rclone /usr/bin/ \
    && rm -rf /tmp/rclone-${RCLONE_VERSION}-linux-amd64 /tmp/rclone.zip

# ======
# Python
# ======

# RUN pip3 install --no-cache-dir -U pip \
#     && pip3 install --no-cache-dir webdavclient3

# =======
# Cleanup
# =======

RUN apk del build-deps \
    && rm -rf /var/cache/apk/*

# =======
# License
# =======

RUN mkdir -p /licenses
COPY LICENSE /licenses/

# ====
# misc
# ====

ENV GLUU_MAX_RAM_PERCENTAGE=75.0

LABEL name="Jackrabbit" \
    maintainer="Gluu Inc. <support@gluu.org>" \
    vendor="Gluu Federation" \
    version="4.1.1" \
    release="02" \
    summary="Jackrabbit" \
    description="A fully conforming implementation of the Content Repository for Java Technology API (JCR)"

RUN mkdir -p /deploy /opt/webdav
COPY static/jackrabbit /opt/jackrabbit/
COPY static/jetty/web.xml ${JETTY_BASE}/jackrabbit/webapps/jackrabbit/WEB-INF/
COPY static/jetty/protectedHandlersConfig.xml ${JETTY_BASE}/jackrabbit/webapps/jackrabbit/WEB-INF/
COPY static/jetty/jackrabbit.xml ${JETTY_BASE}/jackrabbit/webapps/
COPY scripts /app/scripts
RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["tini", "-e", "143", "-g", "--"]
CMD ["sh", "/app/scripts/entrypoint.sh"]
