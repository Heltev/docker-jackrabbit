import contextlib
import logging
import logging.config
import os
import time

import psycopg2
from pygluu.containerlib.utils import as_boolean
from pygluu.containerlib.wait import retry_on_exception

from settings import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("wait")


@retry_on_exception
def wait_for_postgres(manager, **kwargs):
    pg_user = os.environ.get("GLUU_POSTGRES_USER", "postgres")
    pg_password_file = os.environ.get("GLUU_POSTGRES_PASSWORD_FILE", "/etc/gluu/conf/postgres_password")

    pg_password = ""
    with contextlib.suppress(FileNotFoundError):
        with open(pg_password_file) as f:
            pg_password = f.read().strip()

    pg_host = os.environ.get("GLUU_POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("GLUU_POSTGRES_PORT", "5432")
    pg_database = os.environ.get("GLUU_POSTGRES_DATABASE", "jackrabbit")

    conn = psycopg2.connect(
        user=pg_user,
        password=pg_password,
        host=pg_host,
        port=pg_port,
        database=pg_database,
    )
    conn.close()

    # delay to wait for PG readiness
    time.sleep(5)


def main():
    is_cluster = as_boolean(os.environ.get("GLUU_JACKRABBIT_CLUSTER", False))
    if not is_cluster:
        return

    wait_for_postgres(None, **{"label": "Postgres"})


if __name__ == "__main__":
    main()
