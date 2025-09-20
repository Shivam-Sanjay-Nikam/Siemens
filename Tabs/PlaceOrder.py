from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt

class PlaceOrderTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        main_layout = QVBoxLayout()

        # --- Employee Search Section with autocomplete ---
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLabel("Employee ID or Name:"))
        self.emp_search = QLineEdit()
        self.emp_search.setPlaceholderText("Type employee ID or name...")
        search_layout.addWidget(self.emp_search)

        self.suggestions_list = QListWidget()
        search_layout.addWidget(self.suggestions_list)

        # Employee Name input (if new)
        self.emp_name_input = QLineEdit()
        self.emp_name_input.setPlaceholderText("Employee Name (if new)")
        search_layout.addWidget(self.emp_name_input)

        main_layout.addLayout(search_layout)

        # --- Left (Menu) and Right (Cart) Layout ---
        lr_layout = QHBoxLayout()

        # --- Left: Today's Menu ---
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(QLabel("📋 Today’s Menu"))
        self.menu_list = QTableWidget()
        self.menu_list.setColumnCount(3)
        self.menu_list.setHorizontalHeaderLabels(["Item", "Price (₹)", "Qty"])
        self.menu_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.menu_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.menu_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.menu_list.verticalHeader().setVisible(False)
        menu_layout.addWidget(self.menu_list)

        self.add_btn = QPushButton("➕ Add to Cart")
        menu_layout.addWidget(self.add_btn)
        lr_layout.addLayout(menu_layout)

        # --- Right: Cart ---
        cart_layout = QVBoxLayout()
        cart_layout.addWidget(QLabel("🛒 Current Cart"))
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Delete"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.cart_table.verticalHeader().setVisible(False)
        cart_layout.addWidget(self.cart_table)

        self.place_btn = QPushButton("✅ Place Order")
        cart_layout.addWidget(self.place_btn)
        lr_layout.addLayout(cart_layout)

        main_layout.addLayout(lr_layout)
        self.setLayout(main_layout)

        self.cart_items = {}  # item_id: qty
        self.selected_employee = None

        # --- Events ---
        self.add_btn.clicked.connect(self.add_to_cart)
        self.place_btn.clicked.connect(self.place_order)
        self.menu_list.itemChanged.connect(self.menu_qty_changed)
        self.cart_table.itemChanged.connect(self.cart_qty_changed)
        self.emp_search.textChanged.connect(self.update_suggestions)
        self.suggestions_list.itemClicked.connect(self.select_employee)

        self.refresh()

    # --- Employee Autocomplete ---
    def update_suggestions(self, text):
        self.suggestions_list.clear()
        if not text:
            return
        text = text.lower()
        for id, emp_id, name, _ in self.db.get_employees():
            if text in emp_id.lower() or text in name.lower():
                item = QListWidgetItem(f"{emp_id} - {name}")
                item.setData(Qt.UserRole, (id, emp_id, name))
                self.suggestions_list.addItem(item)

    def select_employee(self, item):
        self.selected_employee = item.data(Qt.UserRole)
        _, emp_id, name = self.selected_employee
        self.emp_search.setText(emp_id)
        self.emp_name_input.setText(name)

    # --- Refresh Menu ---
    def refresh(self):
        self.cart_items = {}
        self.cart_table.setRowCount(0)

        self.menu_list.blockSignals(True)
        self.menu_list.setRowCount(0)
        for row, (item_id, name, cost) in enumerate(self.db.get_today_menu()):
            self.menu_list.insertRow(row)
            self.menu_list.setItem(row, 0, QTableWidgetItem(name))
            self.menu_list.setItem(row, 1, QTableWidgetItem(str(cost)))

            qty_item = QTableWidgetItem("1")
            qty_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            qty_item.setData(Qt.UserRole, item_id)
            self.menu_list.setItem(row, 2, qty_item)
        self.menu_list.blockSignals(False)

    # --- Menu Qty Changed ---
    def menu_qty_changed(self, item):
        if item.column() == 2:
            text = item.text()
            if not text.isdigit() or int(text) <= 0:
                QMessageBox.warning(self, "Invalid", "Quantity must be positive.")
                item.setText("1")

    # --- Add to Cart ---
    def add_to_cart(self):
        selected_items = self.menu_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Select Item", "Select a menu item first.")
            return
        row = selected_items[0].row()
        item_id = self.menu_list.item(row, 2).data(Qt.UserRole)
        name = self.menu_list.item(row, 0).text()
        qty = int(self.menu_list.item(row, 2).text())

        self.cart_items[item_id] = qty
        self.refresh_cart()

    # --- Refresh Cart Table ---
    def refresh_cart(self):
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(0)
        for row, (item_id, qty) in enumerate(self.cart_items.items()):
            item_name = next(name for iid, name, _ in self.db.get_today_menu() if iid == item_id)
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item_name))

            qty_item = QTableWidgetItem(str(qty))
            qty_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            qty_item.setData(Qt.UserRole, item_id)
            self.cart_table.setItem(row, 1, qty_item)

            del_btn = QPushButton("🗑️")
            del_btn.clicked.connect(lambda _, iid=item_id: self.remove_from_cart(iid))
            self.cart_table.setCellWidget(row, 2, del_btn)
        self.cart_table.blockSignals(False)

    # --- Cart Qty Changed ---
    def cart_qty_changed(self, item):
        if item.column() == 1:
            text = item.text()
            item_id = item.data(Qt.UserRole)
            if not text.isdigit() or int(text) <= 0:
                QMessageBox.warning(self, "Invalid", "Quantity must be positive.")
                item.setText(str(self.cart_items[item_id]))
            else:
                self.cart_items[item_id] = int(text)

    # --- Remove From Cart ---
    def remove_from_cart(self, item_id):
        if item_id in self.cart_items:
            del self.cart_items[item_id]
            self.refresh_cart()

    # --- Place Order ---
    def place_order(self):
        emp_text = self.emp_search.text().strip()
        emp_name = self.emp_name_input.text().strip()
        if not emp_text:
            QMessageBox.warning(self, "Error", "Employee ID cannot be empty.")
            return

        if emp_name:
            self.db.add_employee(emp_text, emp_name)

        if not self.cart_items:
            QMessageBox.warning(self, "Error", "Cart is empty.")
            return

        items_with_qty = list(self.cart_items.items())
        order_id = self.db.place_order(emp_text, items_with_qty)
        QMessageBox.information(self, "Success", f"Order {order_id} placed successfully!")

        # Reset
        self.emp_search.clear()
        self.emp_name_input.clear()
        self.cart_items = {}
        self.selected_employee = None
        self.refresh()
