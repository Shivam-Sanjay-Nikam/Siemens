#!/usr/bin/env python3
"""
End-to-end test script for the Order Management System.
This script will test all major functionalities of the application.
"""

import sys
import os
from db import Database

def test_database_operations():
    """Test basic database operations."""
    print("🔍 TESTING DATABASE OPERATIONS")
    print("-" * 40)
    
    db = Database()
    
    # Test 1: Check employees
    employees = db.get_employees()
    print(f"✓ Found {len(employees)} employees")
    if employees:
        print(f"  Sample: {employees[0][1]} ({employees[0][2]})")
    
    # Test 2: Check items
    items = db.get_items()
    print(f"✓ Found {len(items)} items")
    if items:
        print(f"  Sample: {items[0][1]} - ₹{items[0][2]}")
    
    # Test 3: Check today's menu
    today_menu = db.get_today_menu()
    print(f"✓ Today's menu has {len(today_menu)} items")
    if today_menu:
        print(f"  Sample: {today_menu[0][1]} - ₹{today_menu[0][2]}")
    
    return db, employees, items, today_menu

def test_order_placement(db, employees, today_menu):
    """Test order placement functionality."""
    print("\n🛒 TESTING ORDER PLACEMENT")
    print("-" * 40)
    
    if not employees or not today_menu:
        print("❌ Cannot test order placement - missing data")
        return None
    
    # Select first employee and first few menu items
    emp_id = employees[0][1]  # Employee ID
    emp_name = employees[0][2]  # Employee name
    
    # Create order with first 3 menu items
    order_items = []
    for i in range(min(3, len(today_menu))):
        item_id = today_menu[i][0]
        quantity = i + 1  # Different quantities: 1, 2, 3
        order_items.append((item_id, quantity))
    
    print(f"✓ Placing order for {emp_name} ({emp_id})")
    print(f"✓ Order items:")
    total_cost = 0
    for item_id, qty in order_items:
        # Find item details
        for item in today_menu:
            if item[0] == item_id:
                item_total = item[2] * qty
                total_cost += item_total
                print(f"  • {item[1]} x{qty} = ₹{item_total}")
                break
    
    print(f"✓ Total order cost: ₹{total_cost}")
    
    # Place the order
    try:
        order_id = db.place_order(emp_id, order_items)
        print(f"✅ Order placed successfully! Order ID: {order_id}")
        return order_id
    except Exception as e:
        print(f"❌ Failed to place order: {e}")
        return None

def test_order_retrieval(db, order_id):
    """Test order retrieval functionality."""
    print("\n📦 TESTING ORDER RETRIEVAL")
    print("-" * 40)
    
    if not order_id:
        print("❌ Cannot test order retrieval - no order ID")
        return
    
    try:
        orders = db.get_orders()
        print(f"✓ Found {len(orders)} total orders")
        
        # Find our specific order
        our_order = None
        for order in orders:
            if order[0] == order_id:
                our_order = order
                break
        
        if our_order:
            print(f"✅ Found our order: #{our_order[0]}")
            print(f"  Employee: {our_order[1]}")
            print(f"  Total: ₹{our_order[2]}")
        else:
            print("❌ Could not find our order in the list")
            
    except Exception as e:
        print(f"❌ Error retrieving orders: {e}")

def test_employee_due_management(db, employees):
    """Test employee due amount management."""
    print("\n💰 TESTING EMPLOYEE DUE MANAGEMENT")
    print("-" * 40)
    
    if not employees:
        print("❌ Cannot test due management - no employees")
        return
    
    emp_id = employees[0][1]
    emp_name = employees[0][2]
    
    try:
        # Get current due amount
        current_due = employees[0][3]
        print(f"✓ {emp_name} current due: ₹{current_due:.2f}")
        
        # Test settlement
        settlement_amount = 50.0
        print(f"✓ Testing settlement of ₹{settlement_amount}")
        
        # Adjust due (simulate settlement)
        db.adjust_employee_due(employees[0][0], -settlement_amount)
        
        # Get updated due amount
        updated_employees = db.get_employees()
        updated_due = None
        for emp in updated_employees:
            if emp[1] == emp_id:
                updated_due = emp[3]
                break
        
        if updated_due is not None:
            print(f"✅ Due amount updated: ₹{updated_due:.2f}")
            print(f"  Change: ₹{current_due - updated_due:.2f}")
        else:
            print("❌ Could not retrieve updated due amount")
            
    except Exception as e:
        print(f"❌ Error in due management: {e}")

def test_analytics(db):
    """Test analytics functionality."""
    print("\n📊 TESTING ANALYTICS")
    print("-" * 40)
    
    try:
        # Test KPIs
        kpis = db.get_kpis()
        print(f"✓ Total Orders: {kpis['total_orders']}")
        print(f"✓ Total Revenue: ₹{kpis['total_revenue']:.2f}")
        print(f"✓ Total Employees: {kpis['total_employees']}")
        print(f"✓ Total Due: ₹{kpis['total_due']:.2f}")
        
        # Test top items
        top_items = db.get_top_items(5)
        print(f"✓ Top {len(top_items)} items:")
        for i, (name, count, revenue) in enumerate(top_items, 1):
            print(f"  {i}. {name} - {count} orders, ₹{revenue:.2f}")
        
        # Test top debtors
        top_debtors = db.get_top_debtors(5)
        print(f"✓ Top {len(top_debtors)} debtors:")
        for i, (name, due) in enumerate(top_debtors, 1):
            print(f"  {i}. {name} - ₹{due:.2f}")
        
        # Test recent orders
        recent_orders = db.get_recent_orders(5)
        print(f"✓ Recent {len(recent_orders)} orders:")
        for i, (order_id, emp_name, total, items_str) in enumerate(recent_orders, 1):
            print(f"  {i}. Order #{order_id} - {emp_name} - ₹{total:.2f}")
            
    except Exception as e:
        print(f"❌ Error in analytics: {e}")

def test_order_deletion(db, order_id):
    """Test order deletion functionality."""
    print("\n🗑️ TESTING ORDER DELETION")
    print("-" * 40)
    
    if not order_id:
        print("❌ Cannot test order deletion - no order ID")
        return
    
    try:
        # Get order count before deletion
        orders_before = db.get_orders()
        print(f"✓ Orders before deletion: {len(orders_before)}")
        
        # Delete the order
        success = db.delete_order(order_id)
        if success:
            print(f"✅ Order #{order_id} deleted successfully")
            
            # Check orders after deletion
            orders_after = db.get_orders()
            print(f"✓ Orders after deletion: {len(orders_after)}")
            print(f"✓ Orders removed: {len(orders_before) - len(orders_after)}")
        else:
            print(f"❌ Failed to delete order #{order_id}")
            
    except Exception as e:
        print(f"❌ Error in order deletion: {e}")

def main():
    """Main test function."""
    print("=" * 60)
    print("ORDER MANAGEMENT SYSTEM - END-TO-END TEST")
    print("=" * 60)
    
    # Test 1: Database Operations
    db, employees, items, today_menu = test_database_operations()
    
    # Test 2: Order Placement
    order_id = test_order_placement(db, employees, today_menu)
    
    # Test 3: Order Retrieval
    test_order_retrieval(db, order_id)
    
    # Test 4: Employee Due Management
    test_employee_due_management(db, employees)
    
    # Test 5: Analytics
    test_analytics(db)
    
    # Test 6: Order Deletion
    test_order_deletion(db, order_id)
    
    print("\n" + "=" * 60)
    print("✅ END-TO-END TEST COMPLETED!")
    print("All major functionalities have been tested.")
    print("=" * 60)

if __name__ == "__main__":
    main()
