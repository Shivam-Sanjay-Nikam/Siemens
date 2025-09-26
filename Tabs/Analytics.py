from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QDateEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate


class AnalyticsTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        layout = QVBoxLayout()

        # --- Date Range Filter ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        filter_layout.addWidget(self.to_date)

        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.apply_filter_btn)

        self.clear_filter_btn = QPushButton("All Time")
        self.clear_filter_btn.clicked.connect(self.clear_filter)
        filter_layout.addWidget(self.clear_filter_btn)

        layout.addLayout(filter_layout)
        
        # Initialize filter state
        self.filter_applied = False

        # --- KPI Section ---
        self.kpi_grid = QGridLayout()
        self.kpi_labels = {
            "total_orders": QLabel("0"),
            "total_revenue": QLabel("0"),
            "total_employees": QLabel("0"),
            "total_due": QLabel("0"),
        }

        def make_card(title, key, row, col):
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; color: #555;")
            value_label = self.kpi_labels[key]
            value_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 6px 0;")
            card = QVBoxLayout()
            card.addWidget(title_label)
            card.addWidget(value_label)
            wrapper = QVBoxLayout()
            container = QWidget()
            container.setLayout(card)
            container.setStyleSheet("""
                QWidget {
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 10px 14px;
                }
            """)
            self.kpi_grid.addWidget(container, row, col)

        make_card("Total Orders", "total_orders", 0, 0)
        make_card("Total Revenue (₹)", "total_revenue", 0, 1)
        make_card("Total Employees", "total_employees", 0, 2)
        make_card("Total Due (₹)", "total_due", 0, 3)

        layout.addLayout(self.kpi_grid)

        # --- Tables Section ---
        tables_layout = QHBoxLayout()

        # Top Items Table
        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(2)
        self.top_items_table.setHorizontalHeaderLabels(["Item", "Qty Sold"])
        self.top_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.top_items_table.verticalHeader().setVisible(False)
        self.top_items_table.setAlternatingRowColors(True)

        # Top Debtors Table
        self.top_debtors_table = QTableWidget()
        self.top_debtors_table.setColumnCount(3)
        self.top_debtors_table.setHorizontalHeaderLabels(["Employee", "Emp ID", "Amount Due (₹)"])
        self.top_debtors_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_debtors_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.top_debtors_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.top_debtors_table.verticalHeader().setVisible(False)
        self.top_debtors_table.setAlternatingRowColors(True)

        tables_layout.addWidget(self.top_items_table)
        tables_layout.addWidget(self.top_debtors_table)

        layout.addLayout(tables_layout)

        # Recent Orders Table
        recent_label = QLabel("Recent Orders")
        recent_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(recent_label)

        self.recent_orders_table = QTableWidget()
        self.recent_orders_table.setColumnCount(3)
        self.recent_orders_table.setHorizontalHeaderLabels(["Order ID", "Employee", "Total (₹)"])
        self.recent_orders_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.recent_orders_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.recent_orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.recent_orders_table.verticalHeader().setVisible(False)
        self.recent_orders_table.setAlternatingRowColors(True)
        layout.addWidget(self.recent_orders_table)

        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)
        self.apply_styling()
        self.refresh()

    def refresh(self):
        # Compose date range strings - only if filter is applied
        date_from = None
        date_to = None
        if hasattr(self, 'filter_applied') and self.filter_applied:
            date_from = self.from_date.date().toString('yyyy-MM-dd') + ' 00:00:00'
            date_to = self.to_date.date().toString('yyyy-MM-dd') + ' 23:59:59'

        # KPIs
        kpis = self.db.get_kpis(date_from, date_to)
        self.kpi_labels["total_orders"].setText(str(kpis["total_orders"]))
        self.kpi_labels["total_revenue"].setText(f"{kpis['total_revenue']:.2f}")
        self.kpi_labels["total_employees"].setText(str(kpis["total_employees"]))
        self.kpi_labels["total_due"].setText(f"{kpis['total_due']:.2f}")

        # Top items
        top_items = self.db.get_top_items(date_from=date_from, date_to=date_to)
        self.top_items_table.setRowCount(0)
        for row, (name, qty) in enumerate(top_items):
            self.top_items_table.insertRow(row)
            self.top_items_table.setItem(row, 0, QTableWidgetItem(name))
            self.top_items_table.setItem(row, 1, QTableWidgetItem(str(qty)))

        # Top debtors
        debtors = self.db.get_top_debtors()
        self.top_debtors_table.setRowCount(0)
        for row, (emp_name, emp_id, due) in enumerate(debtors):
            self.top_debtors_table.insertRow(row)
            self.top_debtors_table.setItem(row, 0, QTableWidgetItem(emp_name))
            self.top_debtors_table.setItem(row, 1, QTableWidgetItem(emp_id))
            self.top_debtors_table.setItem(row, 2, QTableWidgetItem(f"{due:.2f}"))

        # Recent orders
        recent = self.db.get_recent_orders(date_from=date_from, date_to=date_to)
        self.recent_orders_table.setRowCount(0)
        for row, (order_id, emp_name, total) in enumerate(recent):
            self.recent_orders_table.insertRow(row)
            self.recent_orders_table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.recent_orders_table.setItem(row, 1, QTableWidgetItem(emp_name))
            self.recent_orders_table.setItem(row, 2, QTableWidgetItem(f"{total:.2f}"))

    def apply_filter(self):
        """Apply date filter and refresh data."""
        self.filter_applied = True
        self.refresh()

    def clear_filter(self):
        """Clear date filter and show all-time data."""
        self.filter_applied = False
        self.refresh()

    def apply_styling(self):
        self.setStyleSheet("""
            QLabel { color: #333; }
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
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #106ebe; }
            QPushButton:pressed { background-color: #005a9e; }
        """)


