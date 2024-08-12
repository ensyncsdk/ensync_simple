Simple Browser port for qtpy
============================

Original codebase: [Simple Browser - Qt for Python][1]

License: MIT license, except where otherwise stated in sources

Install and Test:
```bash
virtualenv env
./env/bin/python -m pip install --upgrade pip wheel setuptools
./env/bin/pip install -e ".[pyside6]"
QT_API=pyside6 python -m ensync.simple.main
```

[1]: https://doc.qt.io/qtforpython-6/examples/example_webenginewidgets_simplebrowser.html
