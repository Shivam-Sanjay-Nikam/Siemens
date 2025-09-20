from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget


class OrderedTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Placed Orders:"))
        self.order_list = QListWidget()
        self.order_list.addItem("EmpID: 101 | Pizza")
        layout.addWidget(self.order_list)

        self.setLayout(layout)
