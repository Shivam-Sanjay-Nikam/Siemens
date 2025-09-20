import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

# Import your tab classes
from Tabs.PlaceOrder import PlaceOrderTab
from Tabs.Orders import OrderedTab
from Tabs.MenuMaker import MenuMakerTab
from Tabs.SettleUp import SettlUpTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Order Management System")
        self.setGeometry(200, 200, 800, 600)

        # Create Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add Tabs
        self.tabs.addTab(PlaceOrderTab(), "Place Order")
        self.tabs.addTab(OrderedTab(), "Ordered")
        self.tabs.addTab(MenuMakerTab(), "Menu Maker")
        self.tabs.addTab(SettlUpTab(), "Settle Up")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
