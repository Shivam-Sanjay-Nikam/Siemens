from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt

class OrderedTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        header = QLabel("📦 Placed Orders")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(header)

        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Order ID", "Employee", "Total (₹)", "Items Ordered"])
        self.order_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.order_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.order_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.order_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.order_table.verticalHeader().setVisible(False)
        self.order_table.setAlternatingRowColors(True)
        layout.addWidget(self.order_table)

        self.setLayout(layout)
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

        self.order_table.resizeRowsToContents()

    def refresh(self):
        """General refresh for tab switching."""
        self.refresh_orders()
