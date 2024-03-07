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
    QLabel, QGridLayout, QListWidgetItem, QListWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from math import ceil

# Get the directory of the Python program
program_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the "error.jpg" picture
error_picture_path = os.path.join(program_directory, "error.jpg")


class EAN:
    def __init__(self):
        self.ean_codes = {}

    # adds an ean code to the store with the path to the ean code and a temp error picture as model
    def add_ean_code(self, ean_code, image_path):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code] = {"ean_code": ean_code, "image_path": image_path,
                                        "model_path": error_picture_path}
            print(f"EAN code {ean_code} added successfully.")
        else:
            print("Invalid EAN code. It must be 13 digits.")

    # add the model to an ean code in the store
    def add_ean_model(self, ean_code, model_path):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code]["model_path"] = model_path
            print(f"Model {model_path} link to EAN code {ean_code} successful.")
        else:
            print(f"error: when trying to add model {model_path} to EAN. \nEAN{ean_code} must be 13 digits.")

    def get_ean_codes(self):
        return self.ean_codes

    def get_model_path(self, ean_code):
        return self.ean_codes[ean_code]["model_path"]



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mapper")
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()

        self.btn_browse_main = QPushButton("Browse Main Folder")
        self.btn_browse_main.clicked.connect(self.browse_main_folder)

        self.btn_browse_modelpicture = QPushButton("Browse Model Picture Folder")
        self.btn_browse_modelpicture.clicked.connect(self.browse_modelpicture_folder)

        self.list_widget_main = QListWidget()

        self.list_widget_model = QListWidget()

        self.layout_buttons = QHBoxLayout()
        self.layout_buttons.addWidget(self.btn_browse_main)
        self.layout_buttons.addWidget(self.btn_browse_modelpicture)

        self.layout_lists = QHBoxLayout()
        self.layout_lists.addWidget(self.list_widget_main)
        self.layout_lists.addWidget(self.list_widget_model)

        self.layout.addLayout(self.layout_buttons)
        self.layout.addLayout(self.layout_lists)

        self.setLayout(self.layout)

        self.ean_manager = EAN()

    def browse_main_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Main Folder")
        if folder_path:
            image_files = [file for file in os.listdir(folder_path) if file.endswith(('jpg', 'jpeg', 'png', 'gif'))]
            self.list_widget_main.clear()
            for image_file in image_files:
                ean_code = os.path.splitext(image_file)[0]
                image_path = os.path.join(folder_path, image_file)
                self.ean_manager.add_ean_code(ean_code, image_path)
                pixmap = QPixmap(image_path).scaledToWidth(150)
                item = QListWidgetItem()
                item.setIcon(QIcon(pixmap))
                item.setText(ean_code)
                self.list_widget_main.addItem(item)

    def browse_modelpicture_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Model Picture Folder")
        if folder_path:
            self.list_widget_model.clear()
            model_picture_files = [file for file in os.listdir(folder_path) if
                                   file.endswith(('jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'))]
            for ean_code, main_image_path in self.ean_manager.get_ean_codes().items():
                for file in model_picture_files:
                    if file.startswith(ean_code):
                        model_picture_path = os.path.join(folder_path, file)
                        if os.path.exists(model_picture_path):
                            self.ean_manager.add_ean_model(ean_code,model_picture_path)
            for ean_code, main_image_path in self.ean_manager.get_ean_codes().items():
                    pixmap = QPixmap(self.ean_manager.get_model_path(ean_code)).scaledToWidth(150)
                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(ean_code)
                    self.list_widget_model.addItem(item)


    def clear_layout(self):
        self.list_widget_main.clear()
        self.list_widget_model.clear()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
