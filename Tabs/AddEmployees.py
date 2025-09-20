from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt

class AddEmployeesTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        # Add Employee Section
        add_label = QLabel("➕ Add New Employee")
        add_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(add_label)

        form_layout = QHBoxLayout()
        self.emp_id_input = QLineEdit()
        self.emp_id_input.setPlaceholderText("Employee ID (can have leading zeros)")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Employee Name")
        self.add_btn = QPushButton("Add Employee")
        form_layout.addWidget(self.emp_id_input)
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.add_btn)
        layout.addLayout(form_layout)

        # Employees Table
        emp_label = QLabel("👨‍💼 Employees List")
        emp_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(emp_label)

        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(4)
        self.emp_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Amount Due", "Delete"])
        self.emp_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.emp_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.emp_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.emp_table.setAlternatingRowColors(True)
        self.emp_table.verticalHeader().setVisible(False)

        self.emp_table.itemChanged.connect(self.handle_item_changed)
        layout.addWidget(self.emp_table, stretch=1)

        self.setLayout(layout)

        # Events
        self.add_btn.clicked.connect(self.add_employee)
        self.refresh()  # Initial load

    def refresh_employees(self):
        self.emp_table.blockSignals(True)
        self.emp_table.setRowCount(0)
        employees = self.db.get_employees()
        for row, (id, emp_id, name, due) in enumerate(employees):
            self.emp_table.insertRow(row)

            # Employee ID (editable)
            id_item = QTableWidgetItem(emp_id)
            id_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            id_item.setData(Qt.UserRole, id)  # internal table id
            self.emp_table.setItem(row, 0, id_item)

            # Name (editable)
            name_item = QTableWidgetItem(name)
            name_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            name_item.setData(Qt.UserRole, id)
            self.emp_table.setItem(row, 1, name_item)

            # Amount Due (editable)
            due_item = QTableWidgetItem(str(due))
            due_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            due_item.setData(Qt.UserRole, id)
            self.emp_table.setItem(row, 2, due_item)

            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setFixedWidth(40)
            del_btn.clicked.connect(lambda _, eid=id: self.delete_employee(eid))
            self.emp_table.setCellWidget(row, 3, del_btn)

        self.emp_table.blockSignals(False)
        self.emp_table.resizeRowsToContents()

    def handle_item_changed(self, item):
        row = item.row()
        col = item.column()
        if col not in (0, 1, 2):
            return

        internal_id = item.data(Qt.UserRole)
        emp_id_text = self.emp_table.item(row, 0).text()
        name = self.emp_table.item(row, 1).text()
        due_text = self.emp_table.item(row, 2).text()

        if not emp_id_text or not name or not due_text.replace(".", "", 1).isdigit():
            QMessageBox.warning(self, "Error", "Invalid values entered.")
            self.refresh_employees()
            return

        self.db.update_employee(internal_id, emp_id_text, name, float(due_text))

    def add_employee(self):
        emp_id_text = self.emp_id_input.text().strip()
        name = self.name_input.text().strip()

        if not emp_id_text or not name:
            QMessageBox.warning(self, "Error", "Enter valid Employee ID and Name.")
            return

        success = self.db.add_employee(emp_id_text, name)
        if not success:
            QMessageBox.warning(self, "Error", f"Employee ID {emp_id_text} already exists.")
        else:
            QMessageBox.information(self, "Success", f"Employee {name} added.")

        self.emp_id_input.clear()
        self.name_input.clear()
        self.refresh()

    def delete_employee(self, internal_id):
        self.db.delete_employee(internal_id)
        self.refresh()

    def refresh(self):
        """General refresh method for tab switching"""
        self.refresh_employees()
