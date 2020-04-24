import base64

from pygluu.containerlib import get_manager
from pygluu.containerlib.utils import safe_render


def render_repository_xml(manager):
    jca_pw = manager.secret.get("jca_pw") or "admin"
    ctx = {
        "b64_password": base64.b64encode(jca_pw),
    }

    with open("/opt/jackrabbit/repository.xml") as f:
        txt = f.read()

    with open("/opt/jackrabbit/repository.xml", "w") as f:
        f.write(safe_render(txt, ctx))


def main():
    manager = get_manager()
    render_repository_xml(manager)


if __name__ == "__main__":
    main()
