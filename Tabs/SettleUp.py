from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt

class SettlUpTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        # --- Search Section ---
        layout.addWidget(QLabel("Search Employee by ID or Name:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type employee ID or name...")
        layout.addWidget(self.search_input)

        self.suggestions_list = QListWidget()
        layout.addWidget(self.suggestions_list)

        # --- Amount Due Display ---
        amt_layout = QHBoxLayout()
        amt_layout.addWidget(QLabel("Amount Due:"))
        self.amount_label = QLabel("0")
        amt_layout.addWidget(self.amount_label)
        layout.addLayout(amt_layout)

        # --- Settle Up Section ---
        settle_layout = QHBoxLayout()
        self.settle_input = QLineEdit()
        self.settle_input.setPlaceholderText("Amount to settle")
        self.settle_btn = QPushButton("Settle Up")
        settle_layout.addWidget(self.settle_input)
        settle_layout.addWidget(self.settle_btn)
        layout.addLayout(settle_layout)

        self.setLayout(layout)

        # --- Events ---
        self.search_input.textChanged.connect(self.update_suggestions)
        self.suggestions_list.itemClicked.connect(self.select_employee)
        self.settle_btn.clicked.connect(self.settle_up)

        self.selected_employee = None  # store selected employee

    def update_suggestions(self, text):
        self.suggestions_list.clear()
        if not text:
            return
        text = text.lower()
        employees = self.db.get_employees()
        for id, emp_id, name, due in employees:
            if text in emp_id.lower() or text in name.lower():
                item = QListWidgetItem(f"{emp_id} - {name}")
                item.setData(Qt.UserRole, (id, emp_id, name, due))
                self.suggestions_list.addItem(item)

    def select_employee(self, item):
        self.selected_employee = item.data(Qt.UserRole)
        _, emp_id, name, due = self.selected_employee
        self.amount_label.setText(str(due))

    def settle_up(self):
        if not self.selected_employee:
            QMessageBox.warning(self, "Error", "Select an employee first.")
            return

        settle_text = self.settle_input.text().strip()
        if not settle_text.replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Error", "Enter a valid number to settle.")
            return

        settle_amount = float(settle_text)
        internal_id, emp_id, name, due = self.selected_employee

        # Update amount due
        new_due = due - settle_amount
        self.db.update_employee(internal_id, emp_id, name, new_due)

        QMessageBox.information(
            self, "Success",
            f"{settle_amount} settled for {name}.\nNew amount due: {new_due}"
        )
        self.amount_label.setText(str(new_due))
        self.settle_input.clear()

        # Refresh selection
        self.selected_employee = (internal_id, emp_id, name, new_due)
        self.update_suggestions(self.search_input.text())

    def refresh(self):
        """Refresh the tab content when switching."""
        self.search_input.clear()
        self.suggestions_list.clear()
        self.amount_label.setText("0")
        self.settle_input.clear()
        self.selected_employee = None
