# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the Qt WebEngineWidgets Simple Browser example from Qt v6.x"""

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from importlib.util import find_spec
import traceback


def ensure_qt_api():
    qt_api = None
    try:
        qt_api = os.environ["QT_API"]
    except KeyError:
        spec = find_spec("PySide6")
        if spec is None:
            spec = find_spec("PyQt6")
        if spec is not None:
            qt_api = spec.name
            os.environ["QT_API"] = qt_api


def run_main():
    ensure_qt_api()

    from ensync.simple.browser import Browser

    import ensync.simple.data.rc_simplebrowser as rc_simplebrowser  # noqa: F401

    from qtpy.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
    from qtpy.QtWidgets import QApplication, QErrorMessage
    from qtpy.QtGui import QIcon
    from qtpy.QtCore import QCoreApplication, QLoggingCategory, QUrl

    parser = ArgumentParser(description="Qt Widgets Web Browser",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--single-process", "-s", action="store_true",
                        help="Run in single process mode (trouble shooting)")
    parser.add_argument("url", type=str, nargs="*", help="URL")
    ns, rest_args = parser.parse_known_args()

    QCoreApplication.setOrganizationName("ensync")
    QCoreApplication.setApplicationName("simple")

    app_args = [sys.argv[0]]
    if ns.single_process:
        app_args.extend(["--webEngineArgs", "--single-process"])
    if rest_args:
        app_args.extend(rest_args)

    app = QApplication(app_args)
    app.setWindowIcon(QIcon(":AppLogoColor.png"))
    QLoggingCategory.setFilterRules("qt.webenginecontext.debug=true")
    error_message = QErrorMessage.qtHandler()

    s = QWebEngineProfile.defaultProfile().settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)

    browser = Browser()
    window = browser.create_hidden_window()

    arg_urls = ns.url
    if arg_urls:
        content = None
        window.current_tab().deleteLater()
        for url in arg_urls:
            if url == "-":
                if content is None:
                    content = sys.stdin.read()
                    window.load_content_new_tab(content, base_url="about:", background=True)
            else:
                window.load_url_new_tab(url, True)

    window.show()
    rc = 0
    try:
        rc = app.exec()
    except BaseException:
        rc = 1
        traceback.print_exception(*sys.exc_info(), file=sys.stderr)
        app.exit(rc)
    sys.exit(rc)


if __name__ == "__main__":
    run_main()
