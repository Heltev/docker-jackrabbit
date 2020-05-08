#!/bin/sh
set -e

if [ ! -f /deploy/touched ]; then
    python3 /app/scripts/entrypoint.py
    touch /deploy/touched
fi

python3 /app/scripts/jca_sync.py &

cd /opt/gluu/jetty/jackrabbit
exec java \
    -server \
    -Xms1024m \
    -Xmx1024m \
    -XX:MaxMetaspaceSize=256m \
    -XX:+DisableExplicitGC \
    -XX:+UseContainerSupport \
    -XX:MaxRAMPercentage=$GLUU_MAX_RAM_PERCENTAGE \
    -Dserver.base=/opt/gluu/jetty/jackrabbit \
    -Dlog.base=/opt/gluu/jetty/jackrabbit \
    -Djava.io.tmpdir=/tmp \
    -jar /opt/jetty/start.jar
