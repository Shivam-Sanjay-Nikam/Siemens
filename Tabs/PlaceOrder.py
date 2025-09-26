from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QListWidget, QListWidgetItem,
    QCheckBox, QTextEdit, QDialog, QDialogButtonBox, QShortcut, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QKeySequence
import os
from datetime import datetime

class PlaceOrderTab(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db

        main_layout = QVBoxLayout()

        # --- Employee Search Section with autocomplete ---
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLabel("Employee ID or Name:"))
        self.emp_search = QLineEdit()
        self.emp_search.setPlaceholderText("Type employee ID or name...")
        search_layout.addWidget(self.emp_search)

        self.suggestions_list = QListWidget()
        search_layout.addWidget(self.suggestions_list)

        # Employee Name input (if new)
        self.emp_name_input = QLineEdit()
        self.emp_name_input.setPlaceholderText("Employee Name (if new)")
        search_layout.addWidget(self.emp_name_input)

        main_layout.addLayout(search_layout)

        # --- Left (Menu) and Right (Cart) Layout ---
        lr_layout = QHBoxLayout()

        # --- Left: Today's Menu ---
        menu_layout = QVBoxLayout()
        
        # Menu header
        menu_header_layout = QHBoxLayout()
        menu_header_layout.addWidget(QLabel("📋 Today's Menu"))
        menu_header_layout.addStretch()
        
        menu_layout.addLayout(menu_header_layout)
        
        self.menu_list = QTableWidget()
        self.menu_list.setColumnCount(3)
        self.menu_list.setHorizontalHeaderLabels(["Item", "Price (₹)", "Qty"])
        self.menu_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.menu_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.menu_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.menu_list.verticalHeader().setVisible(False)
        self.menu_list.setFocusPolicy(Qt.NoFocus)  # Remove focus rectangle
        self.menu_list.setSelectionMode(QTableWidget.SingleSelection)  # Single selection only
        self.menu_list.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire row
        menu_layout.addWidget(self.menu_list)

        self.add_btn = QPushButton("Add to Cart")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        menu_layout.addWidget(self.add_btn)
        lr_layout.addLayout(menu_layout)

        # --- Right: Cart ---
        cart_layout = QVBoxLayout()
        
        # Cart header with clear button
        cart_header_layout = QHBoxLayout()
        cart_header_layout.addWidget(QLabel("🛒 Current Cart"))
        cart_header_layout.addStretch()
        
        clear_cart_btn = QPushButton("Clear Cart")
        clear_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        clear_cart_btn.clicked.connect(self.refresh)
        cart_header_layout.addWidget(clear_cart_btn)
        
        cart_layout.addLayout(cart_header_layout)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(3)
        self.cart_table.setHorizontalHeaderLabels(["Item", "Qty", "Remove"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.cart_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setFocusPolicy(Qt.NoFocus)  # Remove focus rectangle
        self.cart_table.setSelectionMode(QTableWidget.SingleSelection)  # Single selection only
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire row
        self.cart_table.cellChanged.connect(self.on_cart_cell_changed)  # Connect quantity editing
        cart_layout.addWidget(self.cart_table)

        # Print receipt toggle
        self.print_receipt_checkbox = QCheckBox("Print Receipt")
        self.print_receipt_checkbox.setChecked(True)  # Default to enabled
        self.print_receipt_checkbox.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #333;
                font-size: 14px;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #0078d4;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border: 2px solid #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #ccc;
            }
        """)
        cart_layout.addWidget(self.print_receipt_checkbox)

        # Cart action buttons
        cart_buttons_layout = QHBoxLayout()
        self.place_btn = QPushButton("Place Order")
        self.place_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        cart_buttons_layout.addWidget(self.place_btn)
        cart_layout.addLayout(cart_buttons_layout)
        
        lr_layout.addLayout(cart_layout)

        main_layout.addLayout(lr_layout)
        self.setLayout(main_layout)

        self.cart_items = {}  # item_id: qty
        self.selected_employee = None

        # --- Events ---
        self.add_btn.clicked.connect(self.add_to_cart)
        self.place_btn.clicked.connect(self.place_order)
        self.emp_search.textChanged.connect(self.update_suggestions)
        self.suggestions_list.itemClicked.connect(self.select_employee)

        # --- Setup Shortcuts ---
        self.setup_shortcuts()
        
        # --- Apply Styling ---
        self.apply_styling()

        self.refresh()

    # --- Employee Autocomplete ---
    def update_suggestions(self, text):
        self.suggestions_list.clear()
        if not text:
            return
        text = text.lower()
        for id, emp_id, name, _ in self.db.get_employees():
            if text in emp_id.lower() or text in name.lower():
                item = QListWidgetItem(f"{emp_id} - {name}")
                item.setData(Qt.UserRole, (id, emp_id, name))
                self.suggestions_list.addItem(item)

    def select_employee(self, item):
        self.selected_employee = item.data(Qt.UserRole)
        _, emp_id, name = self.selected_employee
        self.emp_search.setText(emp_id)
        self.emp_name_input.setText(name)

    # --- Refresh Menu ---
    def refresh(self):
        self.cart_items = {}
        self.cart_table.setRowCount(0)

        self.menu_list.blockSignals(True)
        self.menu_list.setRowCount(0)
        for row, (item_id, name, cost) in enumerate(self.db.get_today_menu()):
            self.menu_list.insertRow(row)
            self.menu_list.setItem(row, 0, QTableWidgetItem(name))
            self.menu_list.setItem(row, 1, QTableWidgetItem(str(cost)))

            # Simple quantity input with better editing
            qty_item = QTableWidgetItem("1")
            qty_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            qty_item.setData(Qt.UserRole, item_id)
            qty_item.setBackground(Qt.white)
            qty_item.setForeground(Qt.black)
            qty_item.setTextAlignment(Qt.AlignCenter)  # Center align text
            self.menu_list.setItem(row, 2, qty_item)
        self.menu_list.blockSignals(False)


    # --- Add to Cart ---
    def add_to_cart(self):
        selected_items = self.menu_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Select Item", "Select a menu item first.")
            return
        row = selected_items[0].row()
        
        # Get quantity from table item
        qty_item = self.menu_list.item(row, 2)
        if not qty_item:
            QMessageBox.warning(self, "Error", "Unable to get quantity.")
            return
            
        item_id = qty_item.data(Qt.UserRole)
        name = self.menu_list.item(row, 0).text()
        qty = int(qty_item.text())

        # Add to existing quantity if item already in cart
        if item_id in self.cart_items:
            self.cart_items[item_id] += qty
        else:
            self.cart_items[item_id] = qty
        
        self.refresh_cart()

    # --- Refresh Cart Table ---
    def refresh_cart(self):
        self.cart_table.blockSignals(True)
        self.cart_table.setRowCount(0)
        for row, (item_id, qty) in enumerate(self.cart_items.items()):
            item_name = next(name for iid, name, _ in self.db.get_today_menu() if iid == item_id)
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item_name))

            # Simple quantity display
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable)
            qty_item.setData(Qt.UserRole, item_id)
            qty_item.setBackground(Qt.white)
            qty_item.setForeground(Qt.black)
            self.cart_table.setItem(row, 1, qty_item)

            remove_checkbox = QCheckBox()
            remove_checkbox.setStyleSheet("""
                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 2px solid #dc3545;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #dc3545;
                    border: 2px solid #dc3545;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEzLjMzMzMgNEw2IDExLjMzMzNMMi42NjY2NyA4IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
                }
                QCheckBox::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #dc3545;
                }
                QCheckBox::indicator:hover {
                    border: 2px solid #c82333;
                }
            """)
            remove_checkbox.stateChanged.connect(lambda state, iid=item_id: self.on_remove_checkbox_changed(state, iid))
            self.cart_table.setCellWidget(row, 2, remove_checkbox)
        self.cart_table.blockSignals(False)

    # --- Update Cart Quantity ---
    def update_cart_quantity(self, item_id, new_qty):
        """Update quantity for an item in the cart."""
        if item_id in self.cart_items:
            self.cart_items[item_id] = new_qty

    def on_cart_cell_changed(self, row, column):
        """Handle cart quantity changes."""
        if column == 1:  # Quantity column
            try:
                qty_item = self.cart_table.item(row, column)
                if qty_item:
                    item_id = qty_item.data(Qt.UserRole)
                    new_qty = int(qty_item.text())
                    if new_qty <= 0:
                        # Remove item if quantity is 0 or negative
                        self.remove_from_cart(item_id)
                    else:
                        self.update_cart_quantity(item_id, new_qty)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for quantity.")
                # Reset to previous value
                if item_id in self.cart_items:
                    qty_item.setText(str(self.cart_items[item_id]))

    def on_remove_checkbox_changed(self, state, item_id):
        """Handle remove checkbox changes."""
        if state == Qt.Checked:
            self.remove_from_cart(item_id)



    # --- Remove From Cart ---
    def remove_from_cart(self, item_id):
        if item_id in self.cart_items:
            del self.cart_items[item_id]
            self.refresh_cart()

    # --- Clear Cart ---
    def clear_cart(self):
        if not self.cart_items:
            QMessageBox.information(self, "Cart Empty", "The cart is already empty.")
            return
            
        # Create custom dialog for better UX
        dialog = QDialog(self)
        dialog.setWindowTitle("🗑️ Clear Cart")
        dialog.setModal(True)
        dialog.resize(400, 200)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 10px;
            }
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton#cancelBtn {
                background-color: #6c757d;
            }
            QPushButton#cancelBtn:hover {
                background-color: #5a6268;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Warning icon and message
        warning_frame = QFrame()
        warning_layout = QHBoxLayout()
        warning_label = QLabel("⚠️")
        warning_label.setStyleSheet("font-size: 24px; color: #dc3545;")
        warning_layout.addWidget(warning_label)
        
        message_label = QLabel("Are you sure you want to clear all items from the cart?\n\nThis action cannot be undone.")
        message_label.setWordWrap(True)
        warning_layout.addWidget(message_label)
        warning_frame.setLayout(warning_layout)
        layout.addWidget(warning_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(dialog.reject)
        
        clear_btn = QPushButton("Clear Cart")
        clear_btn.clicked.connect(dialog.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(clear_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
    # --- Place Order ---
    def place_order(self):
        emp_text = self.emp_search.text().strip()
        emp_name = self.emp_name_input.text().strip()
        if not emp_text:
            QMessageBox.warning(self, "Error", "Employee ID cannot be empty.")
            return

        try:
            if emp_name:
                self.db.add_employee(emp_text, emp_name)

            if not self.cart_items:
                QMessageBox.warning(self, "Error", "Cart is empty.")
                return

            items_with_qty = list(self.cart_items.items())
            order_id = self.db.place_order(emp_text, items_with_qty)
            
            if not order_id:
                QMessageBox.critical(self, "Error", "Failed to place order. Please try again.")
                return
            
            # Print receipt if enabled
            if self.print_receipt_checkbox.isChecked():
                self.print_receipt(order_id, emp_text, emp_name, items_with_qty)
            
            QMessageBox.information(self, "Success", f"Order #{order_id} placed successfully!")

            # Reset
            self.emp_search.clear()
            self.emp_name_input.clear()
            self.cart_items = {}
            self.selected_employee = None
            self.refresh()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to place order: {str(e)}")
            import logging
            logging.error(f"Order placement failed: {str(e)}")

    # --- Print Receipt ---
    def print_receipt(self, order_id, emp_id, emp_name, items_with_qty):
        """Generate and print a receipt for the order with comprehensive error handling."""
        try:
            # Calculate total
            total = 0
            item_details = []
            for item_id, qty in items_with_qty:
                # Get item details from database
                items = self.db.get_items()
                for iid, name, cost in items:
                    if iid == item_id:
                        item_total = cost * qty
                        total += item_total
                        item_details.append((name, qty, cost, item_total))
                        break

            # Create receipt content
            receipt_html = self.generate_receipt_html(order_id, emp_id, emp_name, item_details, total)
            
            # Show preview dialog with better error handling
            self.show_receipt_preview(receipt_html, order_id)
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logging.error(f"Receipt generation failed: {str(e)}")
            
            # Show user-friendly error message
            QMessageBox.critical(
                self, 
                "Receipt Generation Failed", 
                f"Unable to generate receipt for Order #{order_id}.\n\n"
                f"Error: {str(e)}\n\n"
                f"The order has been placed successfully, but receipt printing failed.\n"
                f"You can view the order details in the Orders tab."
            )

    def generate_receipt_html(self, order_id, emp_id, emp_name, item_details, total):
        """Generate HTML content for the receipt."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Courier New', monospace; margin: 20px; }}
                .header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
                .title {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
                .subtitle {{ font-size: 14px; color: #666; }}
                .order-info {{ margin-bottom: 20px; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                .items-table th, .items-table td {{ border: 1px solid #000; padding: 8px; text-align: left; }}
                .items-table th {{ background-color: #f0f0f0; font-weight: bold; }}
                .total {{ font-size: 18px; font-weight: bold; text-align: right; border-top: 2px solid #000; padding-top: 10px; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">CAFETERIA RECEIPT</div>
                <div class="subtitle">Order Management System</div>
            </div>
            
            <div class="order-info">
                <p><strong>Order ID:</strong> #{order_id}</p>
                <p><strong>Employee ID:</strong> {emp_id}</p>
                <p><strong>Employee Name:</strong> {emp_name}</p>
                <p><strong>Date & Time:</strong> {current_time}</p>
            </div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for name, qty, price, item_total in item_details:
            html += f"""
                    <tr>
                        <td>{name}</td>
                        <td>{qty}</td>
                        <td>₹{price:.2f}</td>
                        <td>₹{item_total:.2f}</td>
                    </tr>
            """
        
        html += f"""
                </tbody>
            </table>
            
            <div class="total">
                <p>Total Amount: ₹{total:.2f}</p>
            </div>
            
            <div class="footer">
                <p>Thank you for your order!</p>
                <p>Generated by Order Management System</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def show_receipt_preview(self, receipt_html, order_id):
        """Show receipt preview dialog with print option and better error handling."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Receipt Preview - Order #{order_id}")
            dialog.setModal(True)
            dialog.resize(600, 700)
            
            layout = QVBoxLayout()
            
            # Receipt preview
            preview = QTextEdit()
            preview.setHtml(receipt_html)
            preview.setReadOnly(True)
            layout.addWidget(preview)
            
            # Buttons
            button_box = QDialogButtonBox()
            print_btn = button_box.addButton("🖨️ Print", QDialogButtonBox.ActionRole)
            save_btn = button_box.addButton("💾 Save as PDF", QDialogButtonBox.ActionRole)
            copy_btn = button_box.addButton("📋 Copy Text", QDialogButtonBox.ActionRole)
            close_btn = button_box.addButton("Close", QDialogButtonBox.RejectRole)
            
            print_btn.clicked.connect(lambda: self.print_html(receipt_html, order_id))
            save_btn.clicked.connect(lambda: self.save_receipt_pdf(receipt_html, order_id))
            copy_btn.clicked.connect(lambda: self.copy_receipt_text(receipt_html, order_id))
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(button_box)
            dialog.setLayout(layout)
            dialog.exec_()
            
        except Exception as e:
            import logging
            logging.error(f"Receipt preview failed: {str(e)}")
            QMessageBox.critical(
                self, 
                "Receipt Preview Error", 
                f"Unable to show receipt preview.\n\nError: {str(e)}"
            )

    def print_html(self, html_content, order_id):
        """Print the HTML content with comprehensive error handling."""
        try:
            # Check if printing is available
            if not QPrinter.availablePrinters():
                QMessageBox.warning(
                    self, 
                    "No Printer Available", 
                    "No printers are available on this system.\n\n"
                    "Please connect a printer or use 'Save as PDF' option instead."
                )
                return

            printer = QPrinter()
            printer.setPageSize(QPrinter.A4)
            printer.setOrientation(QPrinter.Portrait)
            
            print_dialog = QPrintDialog(printer, self)
            print_dialog.setWindowTitle(f"Print Receipt - Order #{order_id}")
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                doc = QTextDocument()
                doc.setHtml(html_content)
                doc.print_(printer)
                
                QMessageBox.information(
                    self, 
                    "Print Successful", 
                    f"Receipt for Order #{order_id} has been sent to printer successfully!"
                )
            else:
                # User cancelled printing
                pass
                
        except Exception as e:
            import logging
            logging.error(f"Print failed for order {order_id}: {str(e)}")
            
            QMessageBox.critical(
                self, 
                "Print Failed", 
                f"Failed to print receipt for Order #{order_id}.\n\n"
                f"Error: {str(e)}\n\n"
                f"Possible solutions:\n"
                f"• Check if printer is connected and turned on\n"
                f"• Try using 'Save as PDF' option instead\n"
                f"• Restart the application and try again"
            )

    def save_receipt_pdf(self, html_content, order_id):
        """Save receipt as PDF file with error handling."""
        try:
            from PyQt5.QtWidgets import QFileDialog
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtCore import QFileInfo
            
            # Get save location
            filename = f"Receipt_Order_{order_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Receipt as PDF",
                filename,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_path:
                # Create PDF printer
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                printer.setPageSize(QPrinter.A4)
                printer.setOrientation(QPrinter.Portrait)
                
                # Generate PDF
                doc = QTextDocument()
                doc.setHtml(html_content)
                doc.print_(printer)
                
                QMessageBox.information(
                    self, 
                    "PDF Saved Successfully", 
                    f"Receipt for Order #{order_id} has been saved as PDF:\n\n{file_path}"
                )
            else:
                # User cancelled save
                pass
                
        except Exception as e:
            import logging
            logging.error(f"PDF save failed for order {order_id}: {str(e)}")
            
            QMessageBox.critical(
                self, 
                "PDF Save Failed", 
                f"Failed to save receipt as PDF for Order #{order_id}.\n\n"
                f"Error: {str(e)}\n\n"
                f"Please check if you have write permissions to the selected location."
            )

    def copy_receipt_text(self, html_content, order_id):
        """Copy receipt as plain text to clipboard as fallback option."""
        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QMimeData
            
            # Convert HTML to plain text
            doc = QTextDocument()
            doc.setHtml(html_content)
            plain_text = doc.toPlainText()
            
            # Copy to clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(plain_text)
            
            QMessageBox.information(
                self, 
                "Text Copied", 
                f"Receipt text for Order #{order_id} has been copied to clipboard.\n\n"
                f"You can now paste it into any text editor or document."
            )
            
        except Exception as e:
            import logging
            logging.error(f"Copy to clipboard failed for order {order_id}: {str(e)}")
            
            QMessageBox.warning(
                self, 
                "Copy Failed", 
                f"Failed to copy receipt text to clipboard.\n\nError: {str(e)}"
            )

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for Place Order tab."""
        # Place order shortcut
        QShortcut(QKeySequence("Ctrl+Return"), self, self.place_order)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self.place_order)
        
        # Add to cart shortcut
        QShortcut(QKeySequence("Ctrl+A"), self, self.add_to_cart)
        
        # Clear cart shortcut
        QShortcut(QKeySequence("Ctrl+Delete"), self, self.clear_cart)
        
        # Focus shortcuts
        QShortcut(QKeySequence("Ctrl+E"), self, lambda: self.emp_search.setFocus())
        QShortcut(QKeySequence("Ctrl+M"), self, lambda: self.menu_list.setFocus())
        QShortcut(QKeySequence("Ctrl+C"), self, lambda: self.cart_table.setFocus())

    def apply_styling(self):
        """Apply modern styling to Place Order tab."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
            QLabel {
                font-weight: bold;
                color: #333;
                margin: 5px 0px;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                box-shadow: 0 0 0 3px rgba(0, 120, 212, 0.1);
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #005a9e;
                transform: translateY(0px);
            }
            QTableWidget {
                border: 2px solid #dee2e6;
                border-radius: 10px;
                background-color: white;
                gridline-color: #e9ecef;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #e9ecef;
                font-size: 14px;
            }
            QTableWidget::item:selected {
                background-color: #28a745;
                color: white;
                border: none;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
                color: #333;
            }
            QTableWidget::item:selected:hover {
                background-color: #218838;
                color: white;
            }
            QHeaderView::section {
                background-color: #0078d4;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QListWidget {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
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
            /* Special styling for quantity columns */
            QTableWidget::item[column="2"] {
                background-color: #fff3cd;
                color: #000;
                font-weight: bold;
                text-align: center;
            }
            QTableWidget::item[column="2"]:selected {
                background-color: #28a745;
                color: white;
            }
            QCheckBox {
                font-weight: bold;
                color: #333;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #dee2e6;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border-color: #0078d4;
            }
            /* Enhanced quantity column styling */
            QTableWidget QTableWidgetItem[column="2"] {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
            QTableWidget QTableWidgetItem[column="1"] {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                font-weight: bold;
            }
            /* Add subtle shadows and modern look */
            QTableWidget, QListWidget, QLineEdit {
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
        """)
