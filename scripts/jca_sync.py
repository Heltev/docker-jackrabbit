import subprocess
import shlex
import logging.config
import os
import time
from typing import Tuple

from settings import LOGGING_CONFIG

ROOT_DIR = "/repository/default"
SYNC_DIR = "/opt/webdav"

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("webdav")


def exec_cmd(cmd: str) -> Tuple[bytes, bytes, int]:
    args = shlex.split(cmd)
    popen = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = popen.communicate()
    retcode = popen.returncode
    return stdout.strip(), stderr.strip(), retcode


class RClone(object):
    def __init__(self, url, username, password):
        self.url = f"{url}/repository/default"
        self.username = username
        self.password = password

    def configure(self):
        conf_file = os.path.expanduser("~/.config/rclone/rclone.conf")
        if os.path.isfile(conf_file):
            return

        cmd = f"rclone config create jackrabbit webdav vendor other pass {self.password} user admin url {self.url}"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.warning(f"Unable to create webdav config; reason={errors}")

    def copy_from(self, remote, local):
        cmd = f"rclone copy jackrabbit:{remote} {local} --create-empty-src-dirs"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug(f"Unable to sync files from remote directories; reason={errors}")

    def copy_to(self, remote, local):
        cmd = f"rclone copy {local} jackrabbit:{remote} --create-empty-src-dirs"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug(f"Unable to sync files to remote directories; reason={errors}")

    def ready(self, path="/"):
        cmd = "rclone lsd jackrabbit:/"
        _, err, code = exec_cmd(cmd)

        if code != 0:
            errors = err.decode().splitlines()
            logger.debug(f"Unable to list remote directory {path}; reason={errors}")
            return False
        return True


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
    username = os.environ.get("GLUU_JCA_USERNAME", "admin")
    password = "admin"

    password_file = os.environ.get("GLUU_JCA_PASSWORD_FILE", "/etc/gluu/conf/jca_password")
    if os.path.isfile(password_file):
        with open(password_file) as f:
            password = f.read().strip()

    client = RClone(url, username, password)
    client.configure()

    ready = wait_for_jackrabbit(client)
    if not ready:
        return

    sync_to_webdav(client)


if __name__ == "__main__":
    main()
