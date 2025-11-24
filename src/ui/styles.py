DARK_THEME = """
QWidget {
    background-color: #2e2e2e;
    color: #ffffff;
    font-family: Arial;
    font-size: 10pt;
}
QPushButton {
    background-color: #555555;
    border: 1px solid #777777;
    padding: 8px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #6a6a6a;
}
QPushButton:disabled {
    background-color: #333333;
    color: #777777;
}
QListWidget, QTextEdit {
    background-color: #3e3e3e;
    border: 1px solid #555555;
    padding: 5px;
    border-radius: 5px;
}
QProgressBar {
    text-align: center;
    background-color: #555555;
    border: 1px solid #777777;
    border-radius: 5px;
}
QProgressBar::chunk {
    background-color: #3b82f6;
    border-radius: 5px;
}
QLabel {
    font-weight: bold;
    padding-top: 5px;
}
/* --- Radio Button Styling --- */
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #777777;
    background-color: #444444;
}
QRadioButton::indicator:hover {
    border: 2px solid #999999;
}
QRadioButton::indicator:checked {
    background-color: #3b82f6;
    border: 2px solid #3b82f6;
}
QRadioButton::indicator:checked:hover {
    background-color: #5a9bff;
    border: 2px solid #5a9bff;
}
"""