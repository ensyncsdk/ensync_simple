# Copyright (C) 2023 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from threading import RLock

from collections.abc import Iterator
import typing as t

from qtpy.QtWebEngineCore import (
    qWebEngineChromiumVersion, QWebEngineProfile, QWebEngineSettings
    )
from qtpy.QtCore import (
    QObject, Qt, Slot, QCoreApplication, QUrl
)

from ensync.simple.downloadmanagerwidget import DownloadManagerWidget
from ensync.simple.browserwindow import (
    BrowserWindow, DevToolsWindow, BaseBrowserWindow
)


class Browser(QObject):
    if t.TYPE_CHECKING:
        _state_lock: RLock
        _windows: dict[int, BaseBrowserWindow]
        _download_manager_widget: DownloadManagerWidget
        _profile: QWebEngineProfile

    def __init__(self, parent: t.Optional[QObject] = None):
        super().__init__(parent)
        self._state_lock = RLock()
        self._windows = {}
        self._download_manager_widget = DownloadManagerWidget()

        # Quit application if the download manager window is the only
        # remaining window
        self._download_manager_widget.setAttribute(Qt.WA_QuitOnClose, False)

        dp = QWebEngineProfile.defaultProfile()
        dp.downloadRequested.connect(
            self._download_manager_widget.download_requested)

    def configure_profile(self, profile: QWebEngineProfile, options: dict[QWebEngineSettings.WebAttribute, bool]):
        settings = profile.settings()
        for attr, state in options.items():
            settings.setAttribute(attr, state)

    def get_profile(self, private: bool = False) -> QWebEngineProfile:
        if private:
            return QWebEngineProfile.defaultProfile()

        with self._state_lock:
            try:
                return self._profile
            except AttributeError:
                pass

            name = ".".join((QCoreApplication.instance().applicationName(),
                            qWebEngineChromiumVersion()))
            profile = QWebEngineProfile(name)
            self.configure_profile(profile, {
                QWebEngineSettings.WebAttribute.PluginsEnabled: True,
                QWebEngineSettings.WebAttribute.DnsPrefetchEnabled: True,
                QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls: True,
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls: False,
                QWebEngineSettings.WebAttribute.FullScreenSupportEnabled: True,
            })
            profile.downloadRequested.connect(
                self._download_manager_widget.download_requested)
            self._profile = profile
            return profile

    def _add_window(self, window: BaseBrowserWindow):
        with self._state_lock:
            self._windows[id(window)] = window

    def create_hidden_window(self, private: bool = False) -> BrowserWindow:
        profile = self.get_profile(private)
        window = BrowserWindow(self, profile)
        self._add_window(window)
        window.about_to_close.connect(self._remove_window)
        return window

    def create_window(self, private: bool = False) -> BrowserWindow:
        window = self.create_hidden_window(private)
        window.show()
        return window

    def create_dev_tools_window(self, private: bool = False) -> BrowserWindow:
        profile = self.get_profile(private)
        window = DevToolsWindow(self, profile)
        self._add_window(window)
        window.about_to_close.connect(self._remove_window)
        window.show()
        return window

    def each_window(self) -> Iterator[BaseBrowserWindow]:
        with self._state_lock:
            yield from self._windows.values()

    def download_manager_widget(self) -> DownloadManagerWidget:
        return self._download_manager_widget

    @Slot()
    def _remove_window(self) -> t.Optional[BaseBrowserWindow]:
        with self._state_lock:
            w = self.sender()
            wid = id(w)
            return self._windows.pop(wid, None)
