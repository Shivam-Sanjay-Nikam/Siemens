import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from db import Database

from Tabs.PlaceOrder import PlaceOrderTab
from Tabs.Orders import OrderedTab
from Tabs.MenuMaker import MenuMakerTab
from Tabs.SettleUp import SettlUpTab
from Tabs.AddEmployees import AddEmployeesTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Management System")
        self.setGeometry(200, 200, 900, 600)

        self.db = Database()  # Shared DB instance

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Initialize Tabs ---
        self.place_order_tab = PlaceOrderTab(self.db)
        self.ordered_tab = OrderedTab(self.db)
        self.menu_tab = MenuMakerTab(self.db)
        self.settle_tab = SettlUpTab(self.db)
        self.employee_tab = AddEmployeesTab(self.db)

        self.tabs.addTab(self.place_order_tab, "Place Order")
        self.tabs.addTab(self.ordered_tab, "Ordered")
        self.tabs.addTab(self.menu_tab, "Menu Maker")
        self.tabs.addTab(self.settle_tab, "Settle Up")
        self.tabs.addTab(self.employee_tab, "Employees")

        # --- Connect tab change signal ---
        self.tabs.currentChanged.connect(self.on_tab_changed)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
