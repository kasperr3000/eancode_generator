import sys
import os
import subprocess

from PyQt5.QtCore import QSize

# Install PyQt5 if not installed
try:
    import PyQt5
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QLabel, QGridLayout
from PyQt5.QtGui import QPixmap
from math import ceil


class EAN:
    def __init__(self):
        self.ean_codes = {}

    def add_ean_code(self, ean_code, image_path):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code] = image_path
            print(f"EAN code {ean_code} added successfully.")
        else:
            print("Invalid EAN code. It must be 13 digits.")

    def get_ean_codes(self):
        return self.ean_codes


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mapper")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.btn_browse = QPushButton("Browse Folder")
        self.btn_browse.clicked.connect(self.browse_folder)
        self.layout.addWidget(self.btn_browse)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.setLayout(self.layout)

        self.ean_manager = EAN()

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            image_files = [file for file in os.listdir(folder_path) if file.endswith(('jpg', 'jpeg', 'png', 'gif'))]
            self.clear_layout()

            num_columns = 2
            num_rows = ceil(len(image_files) / num_columns)

            for index, image_file in enumerate(image_files):
                ean_code = os.path.splitext(image_file)[0]
                image_path = os.path.join(folder_path, image_file)
                self.ean_manager.add_ean_code(ean_code, image_path)

                row = index // num_columns
                col = index % num_columns

                pixmap = QPixmap(image_path).scaledToWidth(150)
                label = QLabel()
                label.setPixmap(pixmap)
                self.grid_layout.addWidget(label, row, col)

    def clear_layout(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
