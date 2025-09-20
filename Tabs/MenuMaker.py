from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt

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
        form_layout.addWidget(self.item_input)
        form_layout.addWidget(self.cost_input)
        form_layout.addWidget(self.add_btn)
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
        self.save_today_btn.clicked.connect(self.save_today_menu)

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
