from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QHeaderView, QFileDialog, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import os
import csv

class AddEmployeesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        # Add Employee Section
        add_label = QLabel("➕ Add New Employee")
        add_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(add_label)

        form_layout = QHBoxLayout()
        self.emp_id_input = QLineEdit()
        self.emp_id_input.setPlaceholderText("Employee ID (can have leading zeros)")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Employee Name")
        self.add_btn = QPushButton("Add Employee")
        self.import_btn = QPushButton("Import CSV/Excel")
        form_layout.addWidget(self.emp_id_input)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.import_btn)
        layout.addLayout(form_layout)

        # Employees Table
        emp_label = QLabel("👨‍💼 Employees List")
        emp_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(emp_label)

        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(4)
        self.emp_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Amount Due", "Delete"])
        self.emp_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.emp_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.emp_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.emp_table.setAlternatingRowColors(True)
        self.emp_table.verticalHeader().setVisible(False)

        self.emp_table.itemChanged.connect(self.handle_item_changed)
        layout.addWidget(self.emp_table, stretch=1)

        self.setLayout(layout)

        # Events
        self.add_btn.clicked.connect(self.add_employee)
        self.import_btn.clicked.connect(self.import_employees)
        
        # --- Setup Shortcuts ---
        self.setup_shortcuts()
        
        # --- Apply Styling ---
        self.apply_styling()
        
        self.refresh()  # Initial load

    def refresh_employees(self):
        self.emp_table.blockSignals(True)
        self.emp_table.setRowCount(0)
        employees = self.db.get_employees()
        for row, (id, emp_id, name, due) in enumerate(employees):
            self.emp_table.insertRow(row)

            # Employee ID (editable)
            id_item = QTableWidgetItem(emp_id)
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            id_item.setData(Qt.UserRole, id)  # internal table id
            self.emp_table.setItem(row, 0, id_item)

            # Name (editable)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, id)
            self.emp_table.setItem(row, 1, name_item)

            # Amount Due (editable)
            due_item = QTableWidgetItem(str(due))
            due_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            due_item.setData(Qt.UserRole, id)
            self.emp_table.setItem(row, 2, due_item)

            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setFixedWidth(40)
            del_btn.clicked.connect(lambda _, eid=id: self.delete_employee(eid))
            self.emp_table.setCellWidget(row, 3, del_btn)

        self.emp_table.blockSignals(False)
        self.emp_table.resizeRowsToContents()

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col not in (0, 1, 2):
            return

        internal_id = item.data(Qt.UserRole)
        emp_id_text = self.emp_table.item(row, 0).text()
        name = self.emp_table.item(row, 1).text()
        due_text = self.emp_table.item(row, 2).text()

        if not emp_id_text or not name or not due_text.replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Error", "Invalid values entered.")
            self.refresh_employees()
            return

        self.db.update_employee(internal_id, emp_id_text, name, float(due_text))

    def add_employee(self):
        emp_id_text = self.emp_id_input.text().strip()
        name = self.name_input.text().strip()

        if not emp_id_text or not name:
            QMessageBox.warning(self, "Error", "Enter valid Employee ID and Name.")
            return

        success = self.db.add_employee(emp_id_text, name)
        if not success:
            QMessageBox.warning(self, "Error", f"Employee ID {emp_id_text} already exists.")
        else:
            QMessageBox.information(self, "Success", f"Employee {name} added.")

        self.emp_id_input.clear()
        self.name_input.clear()
        self.refresh()

    def delete_employee(self, internal_id):
        self.db.delete_employee(internal_id)
        self.refresh()

    def refresh(self):
        """General refresh method for tab switching"""
        self.refresh_employees()

    # ---------------- Import Utilities ----------------
    def import_employees(self):
        """Open file dialog and import employees from CSV or Excel.
        Expected columns: Employee ID, Name (header optional). Extra columns ignored.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV or Excel file",
            os.path.expanduser("~"),
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".csv"):
                count = self._import_from_csv(file_path)
            elif file_path.lower().endswith((".xlsx", ".xls")):
                count = self._import_from_excel(file_path)
            else:
                QMessageBox.warning(self, "Unsupported", "Please select a .csv, .xlsx, or .xls file.")
                return

            self.refresh()
            QMessageBox.information(self, "Import Complete", f"Imported {count} employee(s).")
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", f"Error importing file:\n{exc}")

    def _import_from_csv(self, file_path):
        imported = 0
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row_idx, row in enumerate(reader):
                if not row:
                    continue
                cells = [c.strip() for c in row]
                # header detection
                if row_idx == 0 and len(cells) >= 2:
                    header_join = " ".join(cells[:2]).lower()
                    if ("employee" in header_join or "emp" in header_join) and ("name" in header_join or "id" in header_join):
                        # If header looks like [emp_id, name] or similar, skip
                        continue

                if len(cells) < 2:
                    continue
                emp_id_text = cells[0]
                name = cells[1]
                if not emp_id_text or not name:
                    continue
                # Try to add; skip duplicates
                if self.db.add_employee(emp_id_text, name):
                    imported += 1
        return imported

    def _import_from_excel(self, file_path):
        try:
            import openpyxl  # type: ignore
        except Exception:
            raise RuntimeError("openpyxl is required for Excel import. Please install it.")

        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        imported = 0

        for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
            if not row:
                continue
            emp_id_val = row[0] if len(row) > 0 else None
            name_val = row[1] if len(row) > 1 else None

            # Header detection
            if row_idx == 0 and isinstance(emp_id_val, str) and isinstance(name_val, (str, type(None))):
                header = f"{emp_id_val.lower()} {str(name_val).lower() if name_val is not None else ''}"
                if ("employee" in header or "emp" in header) and ("name" in header or "id" in header):
                    continue

            emp_id_text = str(emp_id_val).strip() if emp_id_val is not None else ""
            name = str(name_val).strip() if name_val is not None else ""
            if not emp_id_text or not name:
                continue
            if self.db.add_employee(emp_id_text, name):
                imported += 1

        return imported

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for Add Employees tab."""
        # Add employee shortcut
        QShortcut(QKeySequence("Ctrl+N"), self, self.add_employee)
        
        # Import shortcut
        QShortcut(QKeySequence("Ctrl+I"), self, self.import_employees)
        
        # Focus shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.emp_id_input.setFocus())

    def apply_styling(self):
        """Apply modern styling to Add Employees tab."""
        self.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                margin: 5px 0px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
                color: #333;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
                color: #333;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #000;
            }
            QTableWidget::item:selected:hover {
                background-color: #bbdefb;
                color: #000;
            }
        """)
