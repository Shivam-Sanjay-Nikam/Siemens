from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

class OrdersTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        header = QLabel("📦 Placed Orders")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Employee", "Total (₹)", "Items Ordered", "Delete"])
        self.order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.order_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.order_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setAlternatingRowColors(True)
        layout.addWidget(self.order_table)

        self.setLayout(layout)
        
        # --- Setup Shortcuts ---
        self.setup_shortcuts()
        
        # --- Apply Styling ---
        self.apply_styling()
        
        self.refresh()

    def refresh_orders(self):
        """Refresh orders and show items ordered for each order."""
        self.order_table.setRowCount(0)
        orders = self.db.get_orders()
        for row, (order_id, emp_name, total) in enumerate(orders):
            self.order_table.insertRow(row)
            
            # Order ID
            self.order_table.setItem(row, 0, QTableWidgetItem(str(order_id)))

            # Employee
            self.order_table.setItem(row, 1, QTableWidgetItem(emp_name))

            # Total Cost
            self.order_table.setItem(row, 2, QTableWidgetItem(str(total)))

            # Items Ordered
            items = self.db.get_order_items(order_id)
            items_str = "\n".join([f"{name} x{qty}" for name, qty in items])
            item_cell = QTableWidgetItem(items_str)
            item_cell.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.order_table.setItem(row, 3, item_cell)

            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedWidth(40)
            delete_btn.clicked.connect(lambda _, oid=order_id: self.delete_order(oid))
            self.order_table.setCellWidget(row, 4, delete_btn)

        self.order_table.resizeRowsToContents()

    def delete_order(self, order_id):
        """Delete an order with confirmation."""
        # Get order details for confirmation
        orders = self.db.get_orders()
        order_details = None
        for oid, emp_name, total in orders:
            if oid == order_id:
                order_details = (oid, emp_name, total)
                break
        
        if not order_details:
            QMessageBox.warning(self, "Error", "Order not found.")
            return
        
        oid, emp_name, total = order_details
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Delete Order", 
            f"Are you sure you want to delete Order #{oid}?\n\n"
            f"Employee: {emp_name}\n"
            f"Total: ₹{total}\n\n"
            f"This will also adjust the employee's due amount.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_order(order_id)
            if success:
                QMessageBox.information(self, "Success", f"Order #{order_id} deleted successfully.")
                self.refresh_orders()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete order.")

    def refresh(self):
        """General refresh for tab switching."""
        self.refresh_orders()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for Orders tab."""
        # Refresh shortcut
        QShortcut(QKeySequence("F5"), self, self.refresh_orders)
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh_orders)

    def apply_styling(self):
        """Apply modern styling to Orders tab."""
        self.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                margin: 5px 0px;
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
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
