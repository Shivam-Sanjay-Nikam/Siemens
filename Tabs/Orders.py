from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget

class OrderedTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Placed Orders:"))
        self.order_list = QListWidget()
        layout.addWidget(self.order_list)
        self.setLayout(layout)

        self.refresh()  # Initial load

    def refresh_orders(self):
        """Refresh the list of orders."""
        self.order_list.clear()
        for oid, name, total in self.db.get_orders():
            self.order_list.addItem(f"Order {oid} | {name} | Total ₹{total}")

    def refresh(self):
        """General refresh method for tab switching."""
        self.refresh_orders()
