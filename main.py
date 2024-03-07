import csv
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

    def add_ean_code(self, ean_code, product, brand):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code] = {"ean_code": ean_code, "product": product, "brand": brand,
                                        "image_path": error_picture_path,
                                        "model_path": error_picture_path}
            print(f"EAN code {ean_code} added successfully.")
        else:
            print("Invalid EAN code. It must be 13 digits.")

    # adds an ean code to the store with the path to the ean code and a temp error picture as model
    def add_ean_image(self, ean_code, image_path):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code]["image_path"] = image_path
            print(f"EAN image with code {ean_code} added successfully.")
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

    def get_image_path(self, ean_code):
        return self.ean_codes[ean_code]["image_path"]

    def get_model_path(self, ean_code):
        return self.ean_codes[ean_code]["model_path"]


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Mapper")
        self.setGeometry(100, 100, 800, 400)

        self.layout = QVBoxLayout()
        self.layout_buttons = QHBoxLayout()
        self.layout_lists = QHBoxLayout()

        self.btn_import_csv = QPushButton("Import EAN from CSV")
        self.btn_import_csv.clicked.connect(self.import_csv)
        self.layout_buttons.addWidget(self.btn_import_csv)

        self.btn_browse_main = QPushButton("Browse EAN Folder")
        self.btn_browse_main.clicked.connect(self.browse_main_folder)

        self.btn_browse_modelpicture = QPushButton("Browse Model Picture Folder")
        self.btn_browse_modelpicture.clicked.connect(self.browse_modelpicture_folder)

        self.list_widget_main = QListWidget()

        self.list_widget_model = QListWidget()

        self.layout_buttons.addWidget(self.btn_browse_main)
        self.layout_buttons.addWidget(self.btn_browse_modelpicture)

        self.layout_lists.addWidget(self.list_widget_main)
        self.layout_lists.addWidget(self.list_widget_model)

        self.layout.addLayout(self.layout_buttons)
        self.layout.addLayout(self.layout_lists)

        self.setLayout(self.layout)

        self.ean_manager = EAN()

    def import_csv(self):
        csv_file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", filter="CSV Files (*.csv)")
        if csv_file_path:
            self.import_ean_from_csv(csv_file_path)

    # def import_ean_from_csv(self, csv_file_path):
    #     try:
    #         with open(csv_file_path, newline='') as csvfile:
    #             reader = csv.DictReader(csvfile, delimiter=';')
    #             for row in reader:
    #                 brand = row['brand']
    #                 product = row['product']
    #                 ean_code = row['ean_code']
    #                 self.ean_manager.add_ean_code(ean_code, product, brand)
    #     except FileNotFoundError:
    #         print(f"CSV file '{csv_file_path}' not found.")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

    def import_ean_from_csv(self, csv_file_path):
        try:
            with open(csv_file_path, newline='') as csvfile:
                # Use csv.Sniffer to determine the format of the CSV file
                sample = csvfile.read(1024)
                dialect = csv.Sniffer().sniff(sample)
                csvfile.seek(0)

                # Use DictReader with the detected dialect to read the CSV file
                reader = csv.DictReader(csvfile, delimiter=';', dialect=dialect)

                # Extract the column names from the first row of the CSV file
                column_names = reader.fieldnames

                # Ensure column_names is not empty
                if column_names:
                    # Iterate through the rows and access the data using column names
                    for row in reader:
                        # Assuming the column names are dynamic and can vary
                        # You can access each column dynamically
                        brand = row[column_names[0]]
                        product = row[column_names[1]]
                        ean_code = row[column_names[2]]
                        self.ean_manager.add_ean_code(ean_code, product, brand)
                else:
                    print("CSV file does not contain any headers.")
        except FileNotFoundError:
            print(f"CSV file '{csv_file_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def browse_main_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select EAN Picture Folder")
        if folder_path:
            self.list_widget_main.clear()
            ean_files = [file for file in os.listdir(folder_path) if
                         file.endswith(('jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'))]
            for ean_code, rest in self.ean_manager.get_ean_codes().items():
                for file in ean_files:
                    if ean_code in file:
                        image_path = os.path.join(folder_path, file)
                        if os.path.exists(image_path):
                            self.ean_manager.add_ean_image(ean_code, image_path)
            for ean_code, rest in self.ean_manager.get_ean_codes().items():
                pixmap = QPixmap(self.ean_manager.get_image_path(ean_code)).scaled(QSize(350, 150))
                item = QListWidgetItem()
                item.setIcon(QIcon(pixmap))
                item.setText(ean_code)
                self.list_widget_main.addItem(item)
            self.list_widget_main.setIconSize(QSize(350, 150))

    def browse_modelpicture_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Model Picture Folder")
        if folder_path:
            self.list_widget_model.clear()
            model_picture_files = [file for file in os.listdir(folder_path) if
                                   file.endswith(('jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff'))]
            for ean_code, rest in self.ean_manager.get_ean_codes().items():
                for file in model_picture_files:
                    if ean_code in file:
                        model_picture_path = os.path.join(folder_path, file)
                        if os.path.exists(model_picture_path):
                            self.ean_manager.add_ean_model(ean_code, model_picture_path)
            for ean_code, rest in self.ean_manager.get_ean_codes().items():
                pixmap = QPixmap(self.ean_manager.get_model_path(ean_code)).scaled(QSize(150, 150))
                item = QListWidgetItem()
                item.setIcon(QIcon(pixmap))
                item.setText(ean_code)
                self.list_widget_model.addItem(item)
            self.list_widget_model.setIconSize(QSize(150, 150))

    def clear_layout(self):
        self.list_widget_main.clear()
        self.list_widget_model.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
