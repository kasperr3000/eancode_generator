import csv
import os
import subprocess
import sys

# Install if not installed
try:
    import PyQt5
    import reportlab
    import barcode
    import tempfile
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5", "reportlab", "python-barcode", "tempfile"])

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QListWidgetItem, QListWidget, QHBoxLayout, QProgressBar
from PyQt5.QtGui import QPixmap, QIcon
from math import ceil

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph

from barcode import EAN13
from barcode.writer import ImageWriter


class EAN:
    def __init__(self):
        self.ean_codes = {}

        # Get the directory of the Python program
        self.program_directory = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the "error.jpg" picture
        self.error_picture_path = os.path.join(self.program_directory, "error.jpg")

    def add_ean_code(self, ean_code, product, brand):
        if len(ean_code) == 13 and ean_code.isdigit():
            self.ean_codes[ean_code] = {"ean_code": ean_code, "product": product, "brand": brand,
                                        "image_path": self.error_picture_path,
                                        "model_path": self.error_picture_path}
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


def generate_tickets_pdf(ean_instance, output_filename, duplicates=33):
    c = canvas.Canvas(output_filename, pagesize=A4)

    # Define label dimensions
    label_width = 168  # in mm
    label_height = 80  # in mm

    # Define margins and spacing
    left_margin = 5 * mm
    bottom_margin = -1 * mm
    horizontal_spacing = 5 * mm
    vertical_spacing = 0 * mm

    # Define border style
    c.setDash(1, 2)

    # Define styles
    styles = getSampleStyleSheet()
    style_center = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER, fontSize=7)

    # Calculate the width and height available for tickets
    available_width = A4[0] - 2 * left_margin
    available_height = A4[1] - bottom_margin

    # Calculate the number of rows and columns to fit all tickets
    cols = 3
    rows = min(ceil(duplicates / cols), int(available_height / (label_height + vertical_spacing)))

    # Calculate the actual horizontal and vertical spacing between tickets
    horizontal_spacing = (available_width - cols * label_width) / (cols - 1) if cols > 1 else 0
    vertical_spacing = (available_height - rows * label_height) / (rows - 1) if rows > 1 else 0

    # Generate the specified number of duplicates
    for i in range(duplicates):
        # Calculate label positions based on row and column indexes
        col = i % cols
        row = i // cols

        x = left_margin + col * (label_width + horizontal_spacing)
        y = A4[1] - (bottom_margin + row * (label_height + vertical_spacing))

        # Draw dashed border for the label
        c.rect(x, y, label_width, label_height)

        # Calculate the position for the ticket within the label
        ticket_width = label_width - 1 * mm
        ticket_height = label_height - 1 * mm
        ticket_x = x + 1 * mm
        ticket_y = y + 1 * mm

        # Calculate the position for the product picture
        product_img_path = ean_instance['model_path']
        product_img_width = ticket_height
        product_img_height = ticket_height
        product_img_x = ticket_x
        product_img_y = ticket_y

        # Draw product picture
        c.drawImage(product_img_path, product_img_x, product_img_y, width=product_img_width, height=product_img_height)

        # Calculate the position for the barcode
        barcode_width = ticket_width - product_img_width
        barcode_height = ticket_height / 1.75
        barcode_x = product_img_x + product_img_width
        barcode_y = ticket_y

        # Generate barcode image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_barcode_file:
            ean = EAN13(ean_instance["ean_code"], writer=ImageWriter())
            ean.write(temp_barcode_file.name)

            # Draw barcode image
            c.drawImage(temp_barcode_file.name, barcode_x, barcode_y, width=barcode_width, height=barcode_height)

        # Calculate the position for the text elements (product name and brand name)
        text_width = barcode_width
        text_height = ticket_height / 4
        text_x = barcode_x
        text_y = product_img_y + ticket_height / 2

        # Add brand name and product name
        product_name = Paragraph(f"Product: {ean_instance['product']}", style_center)
        brand_name = Paragraph(f"Brand: {ean_instance['brand']}", style_center)
        product_name.wrapOn(c, text_width, text_height)
        brand_name.wrapOn(c, text_width, text_height)
        product_name.drawOn(c, text_x, text_y + 10)  # Adjusted position for product name
        brand_name.drawOn(c, text_x, text_y)  # Adjusted position for brand name

    c.save()
    print(f"PDF generated successfully: {output_filename}")


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

        self.btn_browse_modelpicture = QPushButton("Browse Model Picture Folder")
        self.btn_browse_modelpicture.clicked.connect(self.browse_modelpicture_folder)

        self.btn_generate_pdf = QPushButton("Generate PDF")
        self.btn_generate_pdf.clicked.connect(self.generate_pdf)

        self.list_widget_main = QListWidget()
        self.list_widget_main.setIconSize(QSize(150, 150))

        self.list_widget_model = QListWidget()

        self.layout_buttons.addWidget(self.btn_browse_modelpicture)
        self.layout_buttons.addWidget(self.btn_generate_pdf)

        self.layout_lists.addWidget(self.list_widget_main)
        self.layout_lists.addWidget(self.list_widget_model)

        self.layout.addLayout(self.layout_buttons)
        self.layout.addLayout(self.layout_lists)

        self.setLayout(self.layout)

        self.ean_manager = EAN()
        self.ean_info = []  # To store information about each EAN code
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(False)
        self.layout.addWidget(self.progress_bar)

        item_height = self.list_widget_main.iconSize().height()
        self.list_widget_main.setStyleSheet(f"QListWidget::item {{ height: {item_height}px; }}")

    def generate_pdf(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if output_folder:
            total_ean_codes = len(self.ean_manager.get_ean_codes())
            current_progress = 0
            for index, (ean_code, _) in enumerate(self.ean_manager.get_ean_codes().items(), 1):
                self.generate_pdf_for_ean(ean_code, output_folder)
                current_progress = int((index / total_ean_codes) * 100)
                self.progress_bar.setValue(current_progress)
                QApplication.processEvents()
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Done!")

    def generate_pdf_for_ean(self, ean_code, output_folder):
        ean_data = self.ean_manager.get_ean_codes().get(ean_code)
        if ean_data:
            pdf_filename = os.path.join(output_folder, f"{ean_code}_EAN_labels.pdf")
            generate_tickets_pdf(ean_data, output_filename=pdf_filename)
            print(f"PDF generated for EAN code '{ean_code}': {pdf_filename}")

    def import_csv(self):
        csv_file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", filter="CSV Files (*.csv)")
        if csv_file_path:
            self.import_ean_from_csv(csv_file_path)

    def import_ean_from_csv(self, csv_file_path):
        try:
            with open(csv_file_path, newline='') as csvfile:
                sample = csvfile.read(1024)
                dialect = csv.Sniffer().sniff(sample)
                csvfile.seek(0)

                reader = csv.DictReader(csvfile, delimiter=';', dialect=dialect)

                if reader.fieldnames:
                    for row in reader:
                        brand = row[reader.fieldnames[0]]
                        product = row[reader.fieldnames[1]]
                        ean_code = row[reader.fieldnames[2]]
                        self.ean_manager.add_ean_code(ean_code, product, brand)
                        self.ean_info.append(f"EAN: {ean_code}, Product: {product}, Brand: {brand}")

                    self.list_widget_main.clear()
                    self.list_widget_main.addItems(self.ean_info)
                else:
                    print("CSV file does not contain any headers.")
        except FileNotFoundError:
            print(f"CSV file '{csv_file_path}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

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
