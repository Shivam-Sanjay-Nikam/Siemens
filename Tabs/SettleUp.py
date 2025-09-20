from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class SettlUpTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Settlement / Billing"))
        self.settle_button = QPushButton("Settle Orders")
        layout.addWidget(self.settle_button)

        self.setLayout(layout)
