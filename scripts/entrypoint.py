import base64
import contextlib
import os
import socket

from pygluu.containerlib.utils import as_boolean
from pygluu.containerlib.utils import safe_render

import re


def modify_jetty_xml():
    fn = "/opt/jetty/etc/jetty.xml"
    with open(fn) as f:
        txt = f.read()

    # disable contexts
    updates = re.sub(
        r'<New id="DefaultHandler" class="org.eclipse.jetty.server.handler.DefaultHandler"/>',
        r'<New id="DefaultHandler" class="org.eclipse.jetty.server.handler.DefaultHandler">\n\t\t\t\t <Set name="showContexts">false</Set>\n\t\t\t </New>',
        txt,
        flags=re.DOTALL | re.M,
    )

    # disable Jetty version info
    updates = re.sub(
        r'(<Set name="sendServerVersion"><Property name="jetty.httpConfig.sendServerVersion" deprecated="jetty.send.server.version" default=")true(" /></Set>)',
        r'\1false\2',
        updates,
        flags=re.DOTALL | re.M,
    )

    with open(fn, "w") as f:
        f.write(updates)


def modify_webdefault_xml():
    fn = "/opt/jetty/etc/webdefault.xml"
    with open(fn) as f:
        txt = f.read()

    # disable dirAllowed
    updates = re.sub(
        r'(<param-name>dirAllowed</param-name>)(\s*)(<param-value>)true(</param-value>)',
        r'\1\2\3false\4',
        txt,
        flags=re.DOTALL | re.M,
    )

    with open(fn, "w") as f:
        f.write(updates)


def render_repository_xml():
    is_cluster = as_boolean(os.environ.get("GLUU_JACKRABBIT_CLUSTER", False))
    pg_user = os.environ.get("GLUU_JACKRABBIT_POSTGRES_USER", "postgres")
    pg_password_file = os.environ.get("GLUU_JACKRABBIT_POSTGRES_PASSWORD_FILE", "/etc/gluu/conf/postgres_password")

    pg_password = ""
    with contextlib.suppress(FileNotFoundError):
        with open(pg_password_file) as f:
            pg_password = f.read().strip()

    pg_host = os.environ.get("GLUU_JACKRABBIT_POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("GLUU_JACKRABBIT_POSTGRES_PORT", "5432")
    pg_database = os.environ.get("GLUU_JACKRABBIT_POSTGRES_DATABASE", "jackrabbit")

    anon_id = "anonymous"
    anon_id_file = os.environ.get("GLUU_JACKRABBIT_ANONYMOUS_ID_FILE", "/etc/gluu/conf/jackrabbit_anonymous_id")
    with contextlib.suppress(FileNotFoundError):
        with open(anon_id_file) as f:
            anon_id = f.read().strip()

    admin_id = "admin"
    admin_id_file = os.environ.get("GLUU_JACKRABBIT_ADMIN_ID_FILE", "/etc/gluu/conf/jackrabbit_admin_id")
    with contextlib.suppress(FileNotFoundError):
        with open(admin_id_file) as f:
            admin_id = f.read().strip()

    ctx = {
        "node_name": socket.getfqdn(),
        "pg_host": pg_host,
        "pg_port": pg_port,
        "pg_database": pg_database,
        "pg_password": base64.b64encode(pg_password.encode()).decode(),
        "pg_user": pg_user,
        "jackrabbit_anonymous_id": anon_id,
        "jackrabbit_admin_id": admin_id,
    }

    if is_cluster:
        src = "/app/templates/repository.cluster.xml.tmpl"
    else:
        src = "/app/templates/repository.standalone.xml.tmpl"
    dest = "/opt/jackrabbit/repository.xml"

    with open(src) as f:
        txt = f.read()

    with open(dest, "w") as f:
        f.write(safe_render(txt, ctx))


def main():
    render_repository_xml()
    modify_jetty_xml()
    modify_webdefault_xml()


if __name__ == "__main__":
    main()
