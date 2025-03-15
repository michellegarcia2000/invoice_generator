import sys
import json
import os 
import re 

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, 
    QTableWidget, QTableWidgetItem, QDateEdit, QTextEdit, QHBoxLayout
)
from PyQt6.QtCore import QDate



class InvoiceApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # outdir 
        # Define directory dynamically
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
        json_directory = os.path.join(script_dir,"invoices/")
        self.outdir_path = json_directory

        # Window settings
        self.setWindowTitle("Invoice Form")
        self.setGeometry(200, 200, 700, 600)

        # Layout
        self.layout = QVBoxLayout()

        # Invoice Number
        # self.label_number = QLabel("Enter Invoice Number:")
        # self.layout.addWidget(self.label_number)

        # Invoice Number (Pre-filled)
        self.entry_number = self.get_next_invoice_number()
        self.entry_number_label = QLabel("Invoice Number:")
        self.entry_number = QLineEdit(self.entry_number)  # Pre-fill with next number
        self.entry_number.setReadOnly(False)  # Prevent user from editing
        self.layout.addWidget(self.entry_number_label)
        self.layout.addWidget(self.entry_number)

        # Invoice Date
        self.label_date = QLabel("Select Invoice Date:")
        self.layout.addWidget(self.label_date)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)  # Enable calendar pop-up
        self.date_edit.setDate(QDate.currentDate())  # Default to today
        self.layout.addWidget(self.date_edit)

        # Billing Address
        self.label_billing = QLabel("Billing Address:")
        self.layout.addWidget(self.label_billing)

        self.entry_billing = QTextEdit(self)
        self.layout.addWidget(self.entry_billing)

        # Shipping Address
        self.label_shipping = QLabel("Shipping Address:")
        self.layout.addWidget(self.label_shipping)

        self.entry_shipping = QTextEdit(self)
        self.layout.addWidget(self.entry_shipping)

        # Instructions
        self.label_instructions = QLabel("Instructions:")
        self.layout.addWidget(self.label_instructions)

        self.entry_instructions = QTextEdit(self)
        self.layout.addWidget(self.entry_instructions)

        # Invoice Table
        self.label_table = QLabel("Invoice Items (Fill in the table below):")
        self.layout.addWidget(self.label_table)

        self.table = QTableWidget(5, 4)  # Default 5 rows, 4 columns
        self.table.setHorizontalHeaderLabels(["Quantity", "Description", "Unit Price", "Total"])
        self.layout.addWidget(self.table)

        # Connect changes to the calculation function
        self.table.cellChanged.connect(lambda row, col: self.calculate_total(row, col))

        # Buttons Layout
        button_layout = QHBoxLayout()

        # Add Row Button
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_row_button)

        # Total Label
        self.total_label = QLabel("Total Amount: $0.00")
        button_layout.addWidget(self.total_label)

        self.layout.addLayout(button_layout)

        # Submit Button
        self.submit_button = QPushButton("Submit Invoice")
        self.submit_button.clicked.connect(self.submit_invoice)
        self.layout.addWidget(self.submit_button)

        # Set layout
        self.setLayout(self.layout)

    def get_next_invoice_number(self):
        """Finds the highest existing invoice number and returns the next available one."""
        if not os.path.exists(self.outdir_path):
            os.makedirs(self.outdir_path)

        existing_files = [f for f in os.listdir(self.outdir_path) if f.endswith(".json")]
        invoice_numbers = []

        # Extract numbers from filenames (e.g., "invoice_001.json" → 1)
        for filename in existing_files:
            match = re.search(r'invoice_(\d+)\.json', filename)
            if match:
                invoice_numbers.append(int(match.group(1)))

        next_invoice = max(invoice_numbers, default=0) + 1
        return f"{next_invoice:03d}"

    def add_row(self):
        """Dynamically adds a new row to the invoice table."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)  # Insert a new row at the bottom

    def calculate_total(self, row=None, column=None):
        """Calculates the total based on quantity and unit price."""
        total_amount = 0.0

        for row in range(self.table.rowCount()):
            quantity_item = self.table.item(row, 0)
            unit_price_item = self.table.item(row, 2)

            if quantity_item and unit_price_item:
                try:
                    quantity = float(quantity_item.text()) if quantity_item.text() else 0
                    unit_price = float(unit_price_item.text()) if unit_price_item.text() else 0
                    total = quantity * unit_price

                    # Update the "Total" column
                    self.table.blockSignals(True)  # Prevent infinite recursion
                    self.table.setItem(row, 3, QTableWidgetItem(f"{total:.2f}"))
                    self.table.blockSignals(False)

                    total_amount += total
                except ValueError:
                    pass  # Ignore if the value is not a number

        # Update total label
        self.total_label.setText(f"Total Amount: ${total_amount:.2f}")


    def submit_invoice(self):
        """Collects form data and saves it to a JSON file."""
        invoice_number = self.entry_number.text().strip()
        invoice_date = self.date_edit.date().toString("yyyy-MM-dd")
        billing_address = self.entry_billing.toPlainText().strip()
        shipping_address = self.entry_shipping.toPlainText().strip()
        instructions = self.entry_instructions.toPlainText().strip()

        # Collect table data
        invoice_items = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text().strip() if item else "")

            if any(row_data):  # Ensure non-empty rows are saved
                invoice_items.append({
                    "Quantity": row_data[0],
                    "Description": row_data[1],
                    "Unit Price": row_data[2],
                    "Total": row_data[3]
                })

        # Ensure Invoice Number is entered
        if not invoice_number:
            QMessageBox.warning(self, "Error", "Invoice number cannot be empty!")
            return

        # Create a dictionary to store invoice data
        invoice_data = {
            "Invoice Number": invoice_number,
            "Invoice Date": invoice_date,
            "Billing Address": billing_address,
            "Shipping Address": shipping_address,
            "Instructions": instructions,
            "Items": invoice_items,
            "Total Amount": self.total_label.text()
        }

        # Save to JSON
        json_filename = self.outdir_path + f"invoice_{invoice_number}.json"
        with open(json_filename, "w") as json_file:
            json.dump(invoice_data, json_file, indent=4)

        QMessageBox.information(
            self, "Invoice Submitted",
            f"Invoice {invoice_number} has been successfully saved as {json_filename}!\nTotal Amount: {self.total_label.text()}"
        )

def run_survey(): 
    """Runs the PyQt survey application."""
    app = QApplication.instance()  # Check if an instance of QApplication already exists
    if app is None:
        app = QApplication(sys.argv)  # Create a new instance only if needed

    window = InvoiceApp()
    window.show()
    
    # Instead of sys.exit(app.exec()), use app.exec() directly
    app.exec()

# Run the app
if __name__ == "__main__":
    run_survey()
