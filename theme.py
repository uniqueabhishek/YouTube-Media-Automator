"""
Windows 7 Aero Blue Theme Stylesheet
Maintained in a separate file to keep main_window.py clean.
"""

MAIN_STYLESHEET = """
QWidget {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3a7bd5, stop:1 #245edc);
    color: #ffffff;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 11px;
    border-radius: 8px;
}

QLabel {
    background: transparent;
    color: #ffffff;
    padding: 2px;
}

QLineEdit {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #7eb4ea;
    border-top: 1.5px solid #5a8ec4;
    border-left: 1.5px solid #5a8ec4;
    border-radius: 3px;
    padding: 5px 8px;
    selection-background-color: #3399ff;
}

QLineEdit:focus {
    border: 1px solid #00a2ed;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #fefefe, stop:0.4 #e8e8e8, stop:0.5 #d0d0d0, stop:1 #c8c8c8);
    color: #000000;
    border: 1px solid #707070;
    border-radius: 3px;
    padding: 5px 15px;
    min-width: 75px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e5f3fb, stop:0.4 #c4e5f6, stop:0.5 #98d1ef, stop:1 #68c3ea);
    border: 1px solid #3c7fb1;
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d0e9f7, stop:0.4 #a9d9f0, stop:0.5 #7ac2e5, stop:1 #5eb6db);
    border: 1px solid #2c628b;
    margin-top: 1px;
    margin-left: 1px;
}

QPushButton:disabled {
    background: #f4f4f4;
    color: #838383;
    border: 1px solid #adb2b5;
}

QProgressBar {
    background-color: #e6e6e6;
    border: 1px solid #bcbcbc;
    border-radius: 3px;
    text-align: center;
    color: #000000;
    height: 18px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #37b44a, stop:0.5 #2a9d3c, stop:1 #1e8a30);
    border-radius: 2px;
}

QComboBox {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #7eb4ea;
    border-radius: 3px;
    padding: 4px 8px;
    min-width: 120px;
}

QComboBox:hover {
    border: 1px solid #00a2ed;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #000000;
    selection-background-color: #3399ff;
    selection-color: white;
    border: 1px solid #7eb4ea;
}

QListWidget {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #7eb4ea;
    border-top: 1.5px solid #5a8ec4;
    border-left: 1.5px solid #5a8ec4;
    border-radius: 3px;
    padding: 2px;
}

QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #e0e0e0;
}

QListWidget::item:selected {
    background-color: #3399ff;
    color: white;
}

QListWidget::item:hover {
    background-color: #e5f3fb;
}

QMessageBox {
    background-color: #f0f0f0;
}

QMessageBox QLabel {
    color: #000000;
}

QMessageBox QPushButton {
    min-width: 70px;
}

/* Green Button - Add/Download actions */
QPushButton#greenButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #5cb85c, stop:0.5 #449d44, stop:1 #398439);
    color: white;
    border: 1px solid #255625;
    font-weight: bold;
}

QPushButton#greenButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6ed36e, stop:0.5 #5cb85c, stop:1 #449d44);
    border: 1px solid #398439;
}

QPushButton#greenButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #398439, stop:0.5 #2d6a2d, stop:1 #255625);
}

/* Cyan Button - Paste/Fetch actions */
QPushButton#blueButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #00c9d8, stop:0.5 #00a8b8, stop:1 #0090a0);
    color: white;
    border: 1px solid #007080;
    font-weight: bold;
}

QPushButton#blueButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #20e0f0, stop:0.5 #00c9d8, stop:1 #00a8b8);
    border: 1px solid #0090a0;
}

QPushButton#blueButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0090a0, stop:0.5 #007888, stop:1 #006070);
}

/* Orange Button - Folder selection */
QPushButton#orangeButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f0ad4e, stop:0.5 #ec971f, stop:1 #d58512);
    color: white;
    border: 1px solid #985f0d;
    font-weight: bold;
}

QPushButton#orangeButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f5c879, stop:0.5 #f0ad4e, stop:1 #ec971f);
    border: 1px solid #d58512;
}

QPushButton#orangeButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d58512, stop:0.5 #c77c0f, stop:1 #985f0d);
}

/* Red Button - Cancel actions */
QPushButton#redButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d9534f, stop:0.5 #c9302c, stop:1 #ac2925);
    color: white;
    border: 1px solid #761c19;
    font-weight: bold;
}

QPushButton#redButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e67573, stop:0.5 #d9534f, stop:1 #c9302c);
    border: 1px solid #ac2925;
}

QPushButton#redButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ac2925, stop:0.5 #96231f, stop:1 #761c19);
}

QPushButton#redButton:disabled {
    background: #e0a0a0;
    color: #888888;
    border: 1px solid #c08080;
}

/* Custom Title Bar */
QWidget#titleBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4a90d9, stop:0.5 #2d6fc4, stop:1 #245edc);
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    min-height: 32px;
}

/* Content Area - matches title bar */
QWidget#contentArea {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #245edc, stop:1 #1a4a8a);
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}

QLabel#titleLabel {
    color: white;
    font-size: 13px;
    font-weight: bold;
    padding-left: 8px;
}

QPushButton#minimizeBtn, QPushButton#maximizeBtn, QPushButton#closeBtn {
    background: transparent;
    border: none;
    color: white;
    font-size: 11px;
    font-weight: bold;
    min-width: 30px;
    max-width: 30px;
    min-height: 22px;
    max-height: 22px;
    border-radius: 0px;
    padding: 0px;
}

QPushButton#minimizeBtn:hover, QPushButton#maximizeBtn:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

QPushButton#closeBtn:hover {
    background-color: #e81123;
}

QPushButton#minimizeBtn:pressed, QPushButton#maximizeBtn:pressed {
    background-color: rgba(255, 255, 255, 0.1);
}

QPushButton#closeBtn:pressed {
    background-color: #bf0f1d;
}
"""
