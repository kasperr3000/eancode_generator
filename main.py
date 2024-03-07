import sys
import os
import subprocess

# Install PyQt5 if not installed
try:
    import PyQt5
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QLineEdit


class EAN:
    def __init__(self):
        self.ean_codes = set()

    def add_ean_code(self, ean_code):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes.add(ean_code)
            print(f"EAN code {ean_code} added successfully.")
        else:
            print("Invalid EAN code. It must be 13 digits.")

    def get_ean_codes(self):
        return list(self.ean_codes)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mapper")
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.btn_browse = QPushButton("Browse Folder")
        self.btn_browse.clicked.connect(self.browse_folder)
        self.layout.addWidget(self.btn_browse)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.setLayout(self.layout)

        self.ean_manager = EAN()

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            image_files = [os.path.splitext(file)[0] for file in os.listdir(folder_path) if
                           file.endswith(('jpg', 'jpeg', 'png', 'gif'))]
            self.list_widget.clear()
            self.list_widget.addItems(image_files)

            for image_file in image_files:
                self.ean_manager.add_ean_code(image_file)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
