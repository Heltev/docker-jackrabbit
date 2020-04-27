# import base64

# from pygluu.containerlib import get_manager
# from pygluu.containerlib.utils import safe_render


# def render_repository_xml(manager):
#     jca_pw = manager.secret.get("jca_pw") or "admin"
#     ctx = {
#         "b64_password": base64.b64encode(jca_pw),
#     }

#     with open("/opt/jackrabbit/repository.xml") as f:
#         txt = f.read()

#     with open("/opt/jackrabbit/repository.xml", "w") as f:
#         f.write(safe_render(txt, ctx))

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


def main():
    # manager = get_manager()
    # render_repository_xml(manager)

    modify_jetty_xml()
    modify_webdefault_xml()


if __name__ == "__main__":
    main()
