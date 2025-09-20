from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget


class PlaceOrderTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Enter Employee ID:"))
        self.emp_input = QLineEdit()
        layout.addWidget(self.emp_input)

        layout.addWidget(QLabel("Select Menu Item:"))
        self.menu_list = QListWidget()
        self.menu_list.addItems(["Pizza", "Burger", "Pasta"])  # Later link to MenuMaker
        layout.addWidget(self.menu_list)

        self.order_button = QPushButton("Place Order")
        layout.addWidget(self.order_button)

        self.setLayout(layout)
