import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QShortcut, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from db import Database

from Tabs.PlaceOrder import PlaceOrderTab
from Tabs.Orders import OrdersTab
from Tabs.MenuMaker import MenuMakerTab
from Tabs.SettleUp import SettleUpTab
from Tabs.AddEmployees import AddEmployeesTab
from Tabs.Analytics import AnalyticsTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Management System")
        self.setGeometry(200, 200, 1200, 800)
        
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #d0d0d0;
            }
            
            /* Global text visibility fixes */
            QListWidget::item {
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
            
            QTableWidget::item {
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
        """)

        self.db = Database()  # Shared DB instance

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Initialize Tabs ---
        self.place_order_tab = PlaceOrderTab(self.db)
        self.orders_tab = OrdersTab(self.db)
        self.menu_tab = MenuMakerTab(self.db)
        self.settle_tab = SettleUpTab(self.db)
        self.employee_tab = AddEmployeesTab(self.db)
        self.analytics_tab = AnalyticsTab(self.db)

        self.tabs.addTab(self.place_order_tab, "🛒 Place Order")
        self.tabs.addTab(self.orders_tab, "📦 Orders")
        self.tabs.addTab(self.menu_tab, "🍽️ Menu Maker")
        self.tabs.addTab(self.settle_tab, "💰 Settle Up")
        self.tabs.addTab(self.employee_tab, "👥 Employees")
        self.tabs.addTab(self.analytics_tab, "📈 Analytics")

        # --- Connect tab change signal ---
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # --- Setup Shortcuts ---
        self.setup_shortcuts()

    def on_tab_changed(self, index):
        current_widget = self.tabs.widget(index)
        # Call refresh if the tab has a refresh method
        if hasattr(current_widget, "refresh"):
            current_widget.refresh()
        else:
            # fallback checks for older tabs
            if hasattr(current_widget, "refresh_employees"):
                current_widget.refresh_employees()
            if hasattr(current_widget, "refresh_menu"):
                current_widget.refresh_menu()
                current_widget.refresh_today_menu()
            if hasattr(current_widget, "update_suggestions"):
                current_widget.update_suggestions(current_widget.search_input.text())
            if hasattr(current_widget, "refresh_orders"):
                current_widget.refresh_orders()

    def setup_shortcuts(self):
        """Setup global keyboard shortcuts for the application."""
        # Tab navigation shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.tabs.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.tabs.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.tabs.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self, lambda: self.tabs.setCurrentIndex(3))
        QShortcut(QKeySequence("Ctrl+5"), self, lambda: self.tabs.setCurrentIndex(4))
        QShortcut(QKeySequence("Ctrl+6"), self, lambda: self.tabs.setCurrentIndex(5))
        
        # General shortcuts
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("F5"), self, self.refresh_current_tab)
        QShortcut(QKeySequence("Ctrl+R"), self, self.refresh_current_tab)
        
        # Help shortcut
        QShortcut(QKeySequence("F1"), self, self.show_help)

    def refresh_current_tab(self):
        """Refresh the currently active tab."""
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "refresh"):
            current_widget.refresh()

    def show_help(self):
        """Show keyboard shortcuts help dialog."""
        help_text = """
        <h3>Keyboard Shortcuts</h3>
        <p><b>Tab Navigation:</b></p>
        <ul>
            <li>Ctrl+1 - Place Order</li>
            <li>Ctrl+2 - Orders</li>
            <li>Ctrl+3 - Menu Maker</li>
            <li>Ctrl+4 - Settle Up</li>
            <li>Ctrl+5 - Employees</li>
        </ul>
        <p><b>General:</b></p>
        <ul>
            <li>F5 or Ctrl+R - Refresh current tab</li>
            <li>Ctrl+Q - Quit application</li>
            <li>F1 - Show this help</li>
        </ul>
        <p><b>Tab-specific shortcuts:</b></p>
        <ul>
            <li>Place Order: Ctrl+Enter (Place Order)</li>
            <li>Menu Maker: Ctrl+N (Add Item)</li>
            <li>Employees: Ctrl+N (Add Employee)</li>
        </ul>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
