import sqlite3
import logging
import os
import sys
from datetime import datetime

class Database:
    def __init__(self, db_name="orders.db"):
        # --- Determine database path ---
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Create data directory next to executable/script
        data_dir = os.path.join(base_path, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Database file path
        db_path = os.path.join(data_dir, db_name)
        
        # --- Setup logs directory and file ---
        log_dir = os.path.join(base_path, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"db_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_path = os.path.join(log_dir, log_filename)

        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        logging.info(f"Database initialized at: {db_path}")

        # --- Setup DB ---
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT UNIQUE NOT NULL,
            emp_name TEXT NOT NULL,
            amount_due REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            cost REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT,
            total_order_cost REAL,
            FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        );

        CREATE TABLE IF NOT EXISTS today_menu (
            item_id INTEGER UNIQUE,
            FOREIGN KEY(item_id) REFERENCES items(item_id)
        );
        """)
        self.conn.commit()
        logging.info("Tables created/verified")

    # ---------------- MENU METHODS ----------------
    def add_item(self, name, cost):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO items(item_name, cost) VALUES(?, ?)", (name, cost))
        self.conn.commit()
        logging.info(f"Item added: {name}, cost={cost}")

    def get_items(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_id, item_name, cost FROM items")
        items = cursor.fetchall()
        logging.info("Fetched all items")
        return items

    def update_item(self, item_id, new_name, new_cost):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE items SET item_name=?, cost=? WHERE item_id=?", (new_name, new_cost, item_id))
        self.conn.commit()
        logging.info(f"Item updated: id={item_id}, new_name={new_name}, new_cost={new_cost}")

    def delete_item(self, item_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM items WHERE item_id=?", (item_id,))
        cursor.execute("DELETE FROM today_menu WHERE item_id=?", (item_id,))
        self.conn.commit()
        logging.info(f"Item deleted: id={item_id}")

    def set_today_menu(self, item_ids):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM today_menu")  # Reset
        for iid in item_ids:
            cursor.execute("INSERT INTO today_menu(item_id) VALUES(?)", (iid,))
        self.conn.commit()
        logging.info(f"Today menu set: {item_ids}")

    def get_today_menu(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT i.item_id, i.item_name, i.cost 
            FROM items i
            JOIN today_menu t ON i.item_id = t.item_id
        """)
        menu = cursor.fetchall()
        logging.info("Fetched today's menu")
        return menu

    # ---------------- EMPLOYEE METHODS ----------------
    def add_employee(self, emp_id, emp_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO employees(emp_id, emp_name) VALUES(?, ?)", (emp_id, emp_name))
            self.conn.commit()
            logging.info(f"Employee added: emp_id={emp_id}, name={emp_name}")
            return True
        except sqlite3.IntegrityError:
            logging.warning(f"Duplicate employee ID attempted: {emp_id}")
            return False  # Duplicate emp_id

    def get_employees(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, emp_id, emp_name, amount_due FROM employees")
        employees = cursor.fetchall()
        logging.info("Fetched all employees")
        return employees

    def update_employee(self, id, emp_id, emp_name, amount_due):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE employees SET emp_id=?, emp_name=?, amount_due=? WHERE id=?",
            (emp_id, emp_name, amount_due, id)
        )
        self.conn.commit()
        logging.info(f"Employee updated: id={id}, emp_id={emp_id}, name={emp_name}, amount_due={amount_due}")

    def delete_employee(self, id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=?", (id,))
        self.conn.commit()
        logging.info(f"Employee deleted: id={id}")

    def adjust_employee_due(self, id, amount_change):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE employees SET amount_due = amount_due + ? WHERE id=?", (amount_change, id))
        self.conn.commit()
        logging.info(f"Adjusted employee due: id={id}, change={amount_change}")

    # ---------------- ORDER METHODS ----------------
    def place_order(self, emp_id, items_with_qty):
        cursor = self.conn.cursor()

        total = 0
        for item_id, qty in items_with_qty:
            cursor.execute("SELECT cost FROM items WHERE item_id=?", (item_id,))
            price = cursor.fetchone()[0]
            total += price * qty

        cursor.execute("INSERT INTO orders(emp_id, total_order_cost) VALUES(?, ?)", (emp_id, total))
        order_id = cursor.lastrowid

        for item_id, qty in items_with_qty:
            cursor.execute(
                "INSERT INTO order_items(order_id, item_id, quantity) VALUES(?, ?, ?)",
                (order_id, item_id, qty)
            )

        cursor.execute("UPDATE employees SET amount_due = amount_due + ? WHERE emp_id=?", (total, emp_id))

        self.conn.commit()
        logging.info(f"Order placed: emp_id={emp_id}, order_id={order_id}, total={total}")
        return order_id

    def get_orders(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT o.order_id, e.emp_name, o.total_order_cost
            FROM orders o
            JOIN employees e ON o.emp_id = e.emp_id
        """)
        orders = cursor.fetchall()
        logging.info("Fetched all orders")
        return orders

    def settle_due(self, emp_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE employees SET amount_due = 0 WHERE emp_id=?", (emp_id,))
        self.conn.commit()
        logging.info(f"Settled due for emp_id={emp_id}")

    def get_order_items(self, order_id):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT i.item_name, oi.quantity
            FROM order_items oi
            JOIN items i ON oi.item_id = i.item_id
            WHERE oi.order_id=?
        """, (order_id,))
        items = cursor.fetchall()
        logging.info(f"Fetched items for order_id={order_id}")
        return items
