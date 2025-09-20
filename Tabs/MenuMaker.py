from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget


class MenuMakerTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Add Menu Item:"))
        self.menu_input = QLineEdit()
        layout.addWidget(self.menu_input)

        self.add_button = QPushButton("Add Item")
        layout.addWidget(self.add_button)

        layout.addWidget(QLabel("Current Menu:"))
        self.menu_list = QListWidget()
        self.menu_list.addItems(["Pizza", "Burger", "Pasta"])
        layout.addWidget(self.menu_list)

        self.setLayout(layout)
