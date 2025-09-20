from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QSpinBox, QHBoxLayout, QMessageBox
)

class PlaceOrderTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Employee ID:"))
        self.emp_input = QLineEdit()
        layout.addWidget(self.emp_input)

        layout.addWidget(QLabel("Employee Name (if new):"))
        self.emp_name_input = QLineEdit()
        layout.addWidget(self.emp_name_input)

        layout.addWidget(QLabel("Menu Items:"))
        self.menu_list = QListWidget()
        layout.addWidget(self.menu_list)

        layout.addWidget(QLabel("Quantity:"))
        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(1)
        self.qty_input.setValue(1)
        layout.addWidget(self.qty_input)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add to Order")
        self.place_btn = QPushButton("Place Order")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.place_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.current_order = []

        # --- Events ---
        self.add_btn.clicked.connect(self.add_to_order)
        self.place_btn.clicked.connect(self.place_order)

        self.refresh()  # Load menu initially

    def refresh(self):
        """Refresh today’s menu from DB."""
        self.menu_list.clear()
        for item_id, name, cost in self.db.get_today_menu():
            self.menu_list.addItem(f"{item_id}: {name} - ₹{cost}")
        self.current_order = []

    def add_to_order(self):
        selected = self.menu_list.currentItem()
        if not selected:
            return
        item_id = int(selected.text().split(":")[0])
        qty = self.qty_input.value()
        self.current_order.append((item_id, qty))
        QMessageBox.information(self, "Added", f"Item {item_id} x{qty} added to order.")

    def place_order(self):
        emp_id = self.emp_input.text().strip()
        emp_name = self.emp_name_input.text().strip()

        if not emp_id:
            QMessageBox.warning(self, "Error", "Employee ID cannot be empty.")
            return

        # Employee ID is stored as TEXT to allow leading zeros
        if emp_name:
            self.db.add_employee(emp_id, emp_name)

        if not self.current_order:
            QMessageBox.warning(self, "Error", "No items in order.")
            return

        order_id = self.db.place_order(emp_id, self.current_order)
        QMessageBox.information(self, "Success", f"Order {order_id} placed successfully.")
        self.current_order = []
        self.refresh()  # Refresh menu/order list after placing order
