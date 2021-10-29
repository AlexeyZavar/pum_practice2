import os.path
import subprocess
import sys

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QProgressBar, QVBoxLayout, QPushButton, QFileDialog, QApplication, QCheckBox, QSpinBox

from src import AzarArchive, CaesarCipher, CaesarDecoder, ARCHIVE_EXTENSION


class ShennonWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ShennonWidget, self).__init__()

        self.setWindowFlag(QtCore.Qt.WindowMinMaxButtonsHint, False)
        self.setWindowTitle('Shennon | by AlexeyZavar')

        self.out_path = ''
        self.progress_callback = self.on_progress

        btn_style = 'font-size: 24px'

        self.encode_btn = QPushButton('Encode')
        self.decode_btn = QPushButton('Decode')

        self.encode_btn.clicked.connect(self.encode)
        self.decode_btn.clicked.connect(self.decode)

        self.draw_progress_bar_checkbox = QCheckBox('Draw progress bar (slower)')
        self.draw_progress_bar_checkbox.setChecked(True)
        self.draw_progress_bar_checkbox.stateChanged.connect(self.draw_progress_bar_checked)

        self.encryption_key = QSpinBox()
        self.encryption_key.setMinimum(0)
        self.encryption_key.setMaximum(13)

        self.encode_btn.setStyleSheet(btn_style)
        self.decode_btn.setStyleSheet(btn_style)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(QtCore.Qt.AlignHCenter)

        self.layout = QVBoxLayout(self)

        self.layout.addStretch()
        self.layout.addWidget(self.encode_btn)
        self.layout.addWidget(self.decode_btn)
        self.layout.addWidget(self.draw_progress_bar_checkbox)
        self.layout.addWidget(self.encryption_key)
        self.layout.addWidget(self.progress_bar)
        self.layout.addStretch()

    def encode(self):
        dialog = QFileDialog(self)
        path = dialog.getOpenFileName(self, 'Select a file to pack', filter='Text files (*.txt)')[0]

        filename = os.path.basename(path) + '.' + ARCHIVE_EXTENSION

        self.out_path = dialog.getSaveFileName(self, 'Select where to save a file', os.path.join('./out', filename))[0]

        with AzarArchive(path, self.out_path, CaesarCipher, self.progress_callback, self.on_finish) as azar:
            azar.encoder.key = self.encryption_key.value()
            azar.write()

    def decode(self):
        dialog = QFileDialog(self)
        path = dialog.getOpenFileName(self, 'Select a file to unpack', './out', filter='AlexeyZavar ARchive (*.azar)')[
            0]

        filename = os.path.basename(path).replace('.' + ARCHIVE_EXTENSION, '')

        self.out_path = dialog.getSaveFileName(self, 'Select where to save a file', os.path.join('./out', filename))[0]

        with AzarArchive(path, self.out_path, CaesarDecoder, self.progress_callback, self.on_finish) as azar:
            azar.decoder.key = self.encryption_key.value()
            azar.read()

    def on_progress(self, total, processed):
        if self.progress_bar.maximum() != total:
            self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(processed)

        if processed % 100:
            QApplication.processEvents()

    def on_finish(self):
        self.out_path = self.out_path.replace('/', '\\')
        subprocess.Popen(f'explorer /select,"{self.out_path}"')

        self.progress_bar.setValue(0)

    def draw_progress_bar_checked(self, event):
        self.progress_callback = self.on_progress if self.draw_progress_bar_checkbox.isChecked() else None


if __name__ == "__main__":
    if not os.path.exists('out'):
        os.makedirs('out')

    app = QtWidgets.QApplication([])

    widget = ShennonWidget()
    widget.resize(200, 200)
    widget.show()

    sys.exit(app.exec())
