import contextlib
import logging.config
import os
import time

from pygluu.containerlib.document import RClone

from settings import LOGGING_CONFIG

ROOT_DIR = "/repository/default"
SYNC_DIR = "/opt/webdav"

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("webdav")


def wait_for_jackrabbit(client):
    elapsed_time = 0
    ready = False

    while elapsed_time < 300:
        ready = client.ready()
        if ready:
            break
        time.sleep(10)
        elapsed_time += 10

    if not ready:
        logger.warning(f"Remote directory is not ready after 300 seconds; exiting process ...")
    return ready


def sync_to_webdav(client):
    client.copy_to("/", SYNC_DIR)


def main():
    url = "http://localhost:8080"

    admin_id = "admin"
    admin_id_file = os.environ.get("GLUU_JACKRABBIT_ADMIN_ID_FILE", "/etc/gluu/conf/jackrabbit_admin_id")
    with contextlib.suppress(FileNotFoundError):
        with open(admin_id_file) as f:
            admin_id = f.read().strip()

    username = admin_id
    password = admin_id

    client = RClone(url, username, password)
    client.configure()

    ready = wait_for_jackrabbit(client)
    if not ready:
        return

    sync_to_webdav(client)


if __name__ == "__main__":
    main()
