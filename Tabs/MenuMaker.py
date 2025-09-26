from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem,
    QHeaderView, QFileDialog, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
import os
import csv

class MenuMakerTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        # --- Add New Item Section ---
        add_label = QLabel("➕ Add New Item")
        add_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(add_label)

        form_layout = QHBoxLayout()
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Item Name")
        self.cost_input = QLineEdit()
        self.cost_input.setPlaceholderText("Price (₹)")
        self.add_btn = QPushButton("Add Item")
        self.import_btn = QPushButton("Import CSV/Excel")
        form_layout.addWidget(self.item_input)
        form_layout.addWidget(self.cost_input)
        form_layout.addWidget(self.add_btn)
        form_layout.addWidget(self.import_btn)
        layout.addLayout(form_layout)

        # --- Menu Table ---
        menu_label = QLabel("📋 All Menu Items")
        menu_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(menu_label)

        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(3)
        self.menu_table.setHorizontalHeaderLabels(["Item Name", "Price (₹)", "Delete"])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.menu_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.menu_table.setAlternatingRowColors(True)
        self.menu_table.setWordWrap(True)
        self.menu_table.verticalHeader().setVisible(False)

        # Allow editing
        self.menu_table.itemChanged.connect(self.handle_item_changed)

        layout.addWidget(self.menu_table, stretch=1)

        # --- Today's Menu ---
        today_label = QLabel("📌 Set Today’s Menu")
        today_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(today_label)

        self.today_list = QListWidget()
        self.today_list.setAlternatingRowColors(True)
        layout.addWidget(self.today_list, stretch=1)

        self.save_today_btn = QPushButton("💾 Save Today’s Menu")
        layout.addWidget(self.save_today_btn)

        self.setLayout(layout)

        # Events
        self.add_btn.clicked.connect(self.add_item)
        self.import_btn.clicked.connect(self.import_items)
        self.save_today_btn.clicked.connect(self.save_today_menu)

        # --- Setup Shortcuts ---
        self.setup_shortcuts()
        
        # --- Apply Styling ---
        self.apply_styling()

        self.refresh()  # initial load

    def refresh_menu(self):
        self.menu_table.blockSignals(True)
        self.menu_table.setRowCount(0)
        items = self.db.get_items()
        for row, (item_id, name, cost) in enumerate(items):
            self.menu_table.insertRow(row)

            # Item Name (editable)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, item_id)
            self.menu_table.setItem(row, 0, name_item)

            # Price (editable)
            cost_item = QTableWidgetItem(str(cost))
            cost_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            cost_item.setData(Qt.UserRole, item_id)
            self.menu_table.setItem(row, 1, cost_item)

            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setFixedWidth(40)
            del_btn.clicked.connect(lambda _, iid=item_id: self.delete_item(iid))
            self.menu_table.setCellWidget(row, 2, del_btn)

        self.menu_table.blockSignals(False)
        self.menu_table.resizeRowsToContents()

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col not in (0, 1):
            return

        item_id = item.data(Qt.UserRole)
        new_name = self.menu_table.item(row, 0).text()
        new_cost_text = self.menu_table.item(row, 1).text()

        if not new_name or not new_cost_text.replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Error", "Invalid edit values.")
            self.refresh_menu()
            return

        self.db.update_item(item_id, new_name, float(new_cost_text))
        self.refresh_today_menu()

    def refresh_today_menu(self):
        self.today_list.clear()
        items = self.db.get_items()
        today_items = {iid for iid, _, _ in self.db.get_today_menu()}

        for item_id, name, cost in items:
            entry = QListWidgetItem(f"{name} - ₹{cost}")
            entry.setFlags(entry.flags() | Qt.ItemIsUserCheckable)
            entry.setCheckState(Qt.Checked if item_id in today_items else Qt.Unchecked)
            entry.setData(Qt.UserRole, item_id)
            self.today_list.addItem(entry)

    def add_item(self):
        name = self.item_input.text().strip()
        cost = self.cost_input.text().strip()
        if not name or not cost.replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Error", "Enter valid name and price.")
            return
        self.db.add_item(name, float(cost))
        self.item_input.clear()
        self.cost_input.clear()
        self.refresh()

    def delete_item(self, item_id):
        self.db.delete_item(item_id)
        self.refresh()

    def save_today_menu(self):
        selected_ids = []
        for i in range(self.today_list.count()):
            item = self.today_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_ids.append(item.data(Qt.UserRole))
        self.db.set_today_menu(selected_ids)
        QMessageBox.information(self, "Saved", "Today’s Menu updated successfully!")

    def refresh(self):
        """General refresh method for tab switching"""
        self.refresh_menu()
        self.refresh_today_menu()

    # ---------------- Import Utilities ----------------
    def import_items(self):
        """Open a file dialog to import items from CSV or Excel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV or Excel file",
            os.path.expanduser("~"),
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if not file_path:
            return

        try:
            imported_count = 0
            if file_path.lower().endswith(".csv"):
                imported_count = self._import_from_csv(file_path)
            elif file_path.lower().endswith((".xlsx", ".xls")):
                imported_count = self._import_from_excel(file_path)
            else:
                QMessageBox.warning(self, "Unsupported", "Please select a .csv, .xlsx, or .xls file.")
                return

            self.refresh()
            QMessageBox.information(self, "Import Complete", f"Imported {imported_count} item(s).")
        except Exception as exc:
            QMessageBox.critical(self, "Import Failed", f"Error importing file:\n{exc}")

    def _import_from_csv(self, file_path):
        """Import items from a CSV file with columns: name, price.
        The file may contain a header row. Extra columns are ignored.
        """
        imported = 0
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row_idx, row in enumerate(reader):
                if not row:
                    continue
                # Normalize and attempt to detect header
                cells = [c.strip() for c in row]
                if row_idx == 0 and len(cells) >= 2:
                    header_join = " ".join(cells[:2]).lower()
                    if "name" in header_join and ("price" in header_join or "cost" in header_join):
                        continue  # skip header

                if len(cells) < 2:
                    continue
                name = cells[0]
                price_text = cells[1].replace("₹", "").strip()
                # Validate price
                if not name:
                    continue
                if not price_text.replace(".", "", 1).isdigit():
                    continue
                self.db.add_item(name, float(price_text))
                imported += 1
        return imported

    def _import_from_excel(self, file_path):
        """Import items from an Excel file with first two columns: name, price.
        The sheet may contain a header row. Extra columns are ignored.
        """
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
            name = (row[0] if len(row) > 0 else None)
            price = (row[1] if len(row) > 1 else None)

            # Header detection
            if row_idx == 0 and isinstance(name, str) and isinstance(price, (str, type(None))):
                header_join = f"{str(name).lower()} {str(price).lower() if price is not None else ''}"
                if "name" in header_join and ("price" in header_join or "cost" in header_join):
                    continue

            if isinstance(name, str):
                name = name.strip()
            if not name:
                continue

            # Normalize/validate price
            if isinstance(price, str):
                price_text = price.replace("₹", "").strip()
                if not price_text.replace(".", "", 1).isdigit():
                    continue
                price_val = float(price_text)
            elif isinstance(price, (int, float)):
                price_val = float(price)
            else:
                continue

            self.db.add_item(name, price_val)
            imported += 1

        return imported

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for Menu Maker tab."""
        # Add item shortcut
        QShortcut(QKeySequence("Ctrl+N"), self, self.add_item)
        
        # Import shortcut
        QShortcut(QKeySequence("Ctrl+I"), self, self.import_items)
        
        # Save today's menu shortcut
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_today_menu)
        
        # Focus shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.item_input.setFocus())

    def apply_styling(self):
        """Apply modern styling to Menu Maker tab."""
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
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #000;
            }
            QListWidget::item:selected:hover {
                background-color: #bbdefb;
                color: #000;
            }
        """)
