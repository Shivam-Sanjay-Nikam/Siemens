from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QMessageBox, QListWidget, QListWidgetItem, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

class SettleUpTab(QWidget):
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

        # --- Setup Shortcuts ---
        self.setup_shortcuts()
        
        # --- Apply Styling ---
        self.apply_styling()

        self.selected_employee = None  # store selected employee

    def update_suggestions(self, text):
        self.suggestions_list.clear()
        if not text:
            return
        text = text.lower()
        employees = self.db.get_employees()
        
        # Filter and sort employees by decreasing due amounts
        filtered_employees = []
        for id, emp_id, name, due in employees:
            if text in emp_id.lower() or text in name.lower():
                filtered_employees.append((id, emp_id, name, due))
        
        # Sort by due amount in decreasing order
        filtered_employees.sort(key=lambda x: x[3], reverse=True)
        
        for id, emp_id, name, due in filtered_employees:
            if due < 0:
                item = QListWidgetItem(f"{emp_id} - {name} (Credit: ₹{abs(due):.2f})")
            else:
                item = QListWidgetItem(f"{emp_id} - {name} (Due: ₹{due:.2f})")
            item.setData(Qt.UserRole, (id, emp_id, name, due))
            self.suggestions_list.addItem(item)

    def select_employee(self, item):
        self.selected_employee = item.data(Qt.UserRole)
        _, emp_id, name, due = self.selected_employee
        if due < 0:
            self.amount_label.setText(f"Credit: ₹{abs(due):.2f}")
        else:
            self.amount_label.setText(f"₹{due:.2f}")

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

        if settle_amount <= 0:
            QMessageBox.warning(self, "Error", "Amount must be positive.")
            return

        # Allow settling more than due amount (overpayment)
        if settle_amount > due:
            reply = QMessageBox.question(
                self, "Overpayment Confirmation",
                f"Amount (₹{settle_amount:.2f}) exceeds current due (₹{due:.2f}).\n"
                f"This will create a credit balance of ₹{settle_amount - due:.2f}.\n\n"
                f"Continue with overpayment?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Update amount due using adjust_employee_due (subtract the amount)
        self.db.adjust_employee_due(internal_id, -settle_amount)

        new_due = due - settle_amount
        if new_due < 0:
            # Overpayment case
            QMessageBox.information(
                self, "Success",
                f"Settlement successful!\n\n"
                f"Employee: {name} ({emp_id})\n"
                f"Amount settled: ₹{settle_amount:.2f}\n"
                f"Credit balance: ₹{abs(new_due):.2f}"
            )
        else:
            # Normal payment case
            QMessageBox.information(
                self, "Success",
                f"Settlement successful!\n\n"
                f"Employee: {name} ({emp_id})\n"
                f"Amount settled: ₹{settle_amount:.2f}\n"
                f"Remaining due: ₹{new_due:.2f}"
            )
        
        # Update the display
        if new_due < 0:
            self.amount_label.setText(f"Credit: ₹{abs(new_due):.2f}")
        else:
            self.amount_label.setText(f"₹{new_due:.2f}")
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

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for Settle Up tab."""
        # Settle up shortcut
        QShortcut(QKeySequence("Ctrl+Return"), self, self.settle_up)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self.settle_up)
        
        # Focus shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.search_input.setFocus())
        QShortcut(QKeySequence("Ctrl+A"), self, lambda: self.settle_input.setFocus())

    def apply_styling(self):
        """Apply modern styling to Settle Up tab."""
        self.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #333;
                margin: 5px 0px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                color: #333;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #000;
            }
            QListWidget::item:selected:hover {
                background-color: #bbdefb;
                color: #000;
            }
        """)
