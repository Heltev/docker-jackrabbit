import logging.config
import os
import time

from webdav3.client import Client
from webdav3.exceptions import RemoteResourceNotFound
from webdav3.exceptions import NoConnection

from settings import LOGGING_CONFIG

ROOT_DIR = "/repository/default"
SYNC_DIR = "/opt/webdav"

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("webdav")


def wait_for_jackrabbit(client):
    elapsed_time = 0
    ready = False

    while elapsed_time < 300:
        try:
            client.list()
            ready = True
            break
        except (RemoteResourceNotFound, NoConnection) as exc:
            logger.warning(f"Unable to connect to remote directory; reason={exc} ... retrying in 10 seconds")
        time.sleep(10)
        elapsed_time += 10

    if not ready:
        logger.warning(f"Remote directory is not ready; exiting process ...")
    return ready


def sync_to_webdav(client):
    for subdir, _, files in os.walk(SYNC_DIR):
        dir_ = subdir.replace(SYNC_DIR, "")

        if not dir_:
            continue

        # logger.info(f"creating {dir_} directory (if not exist)")
        client.mkdir(dir_)

        for file_ in files:
            remote = os.path.join(dir_, file_)
            local = f"{SYNC_DIR}{remote}"
            logger.info(f"uploading {remote} file")
            client.upload(remote, local)

    # except (RemoteResourceNotFound, NoConnection) as exc:
    #     logger.warning(f"Unable to sync files from remote directory {url}{ROOT_DIR}{SYNC_DIR}; reason={exc}")


def main():
    url = "http://localhost:8080"
    username = os.environ.get("GLUU_JCA_USERNAME", "admin")
    password = "admin"

    password_file = os.environ.get("GLUU_JCA_PASSWORD_FILE", "/etc/gluu/conf/jca_password")
    if os.path.isfile(password_file):
        with open(password_file) as f:
            password = f.read().strip()

    options = {
        "webdav_hostname": url,
        "webdav_login": username,
        "webdav_password": password,
        "webdav_root": ROOT_DIR,
    }
    client = Client(options)

    ready = wait_for_jackrabbit(client)
    if not ready:
        return

    sync_to_webdav(client)


if __name__ == "__main__":
    main()
