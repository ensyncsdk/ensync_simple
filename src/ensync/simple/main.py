# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 port of the Qt WebEngineWidgets Simple Browser example from Qt v6.x"""

import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from qtpy.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QIcon
from qtpy.QtCore import QCoreApplication, QLoggingCategory, QUrl

from ensync.simple.browser import Browser

import ensync.simple.data.rc_simplebrowser as rc_simplebrowser  # noqa: F401

if __name__ == "__main__":
    parser = ArgumentParser(description="Qt Widgets Web Browser",
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument("--single-process", "-s", action="store_true",
                        help="Run in single process mode (trouble shooting)")
    parser.add_argument("url", type=str, nargs="?", help="URL")
    args = parser.parse_args()

    QCoreApplication.setOrganizationName("QtExamples")

    app_args = sys.argv
    if args.single_process:
        app_args.extend(["--webEngineArgs", "--single-process"])
    app = QApplication(app_args)
    app.setWindowIcon(QIcon(":AppLogoColor.png"))
    QLoggingCategory.setFilterRules("qt.webenginecontext.debug=true")

    s = QWebEngineProfile.defaultProfile().settings()
    s.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
    s.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)

    browser = Browser()
    window = browser.create_hidden_window()

    # url = QUrl.fromUserInput(args.url) if args.url else QUrl("https://www.qt.io")
    # window.tab_widget().set_url(url)
    window.show()
    try:
        rc = app.exec()
    except BaseException:
        raise
    sys.exit(rc)
