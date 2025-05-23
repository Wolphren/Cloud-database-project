import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import time
from datetime import datetime
from prettytable import PrettyTable

class InventoryManagementSystem:
    def __init__(self, credentials_path):
        """Initialize connection to Firebase and Firestore client"""
        try:
            # Initializes Firebase with credentials
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            
            # Gets the Firestore client
            self.db = firestore.client()
            self.inventory_collection = self.db.collection('inventory')
            print("Successfully connected to Firestore")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            exit(1)
    
    def add_item(self, item_data):
        """Add a new item to the inventory
        
        Args:
            item_data (dict): Dictionary containing item details
        
        Returns:
            str: ID of the added document
        """
        try:
            # Add timestamp
            item_data['created_at'] = firestore.SERVER_TIMESTAMP
            item_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Add the document to the inventory
            doc_ref = self.inventory_collection.add(item_data)[1]
            print(f"Item added successfully with ID: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            print(f"Error adding item: {e}")
            return None
    
    def get_all_items(self):
        """Retrieves all items from the inventory
        
        Returns:
            list: List of dictionaries containing item data
        """
        try:
            items = []
            docs = self.inventory_collection.stream()
            
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                items.append(item_data)
            
            return items
        except Exception as e:
            print(f"Error retrieving items: {e}")
            return []
    
    def get_item_by_id(self, item_id):
        """Retrieves an item by its ID
        
        Args:
            item_id (str): Document ID of the item
        
        Returns:
            dict: Item data or None if not found
        """
        try:
            doc_ref = self.inventory_collection.document(item_id)
            doc = doc_ref.get()
            
            if doc.exists:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                return item_data
            else:
                print(f"No item found with ID: {item_id}")
                return None
        except Exception as e:
            print(f"Error retrieving item: {e}")
            return None
    
    def update_item(self, item_id, update_data):
        """Update an existing item in the inventory
        
        Args:
            item_id (str): Document ID of the item to update
            update_data (dict): Dictionary containing updated fields
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add updated timestamp
            update_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref = self.inventory_collection.document(item_id)
            doc_ref.update(update_data)
            print(f"Item with ID {item_id} updated successfully")
            return True
        except Exception as e:
            print(f"Error updating item: {e}")
            return False
    
    def delete_item(self, item_id):
        """Delete an item from the inventory
        
        Args:
            item_id (str): Document ID of the item to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.inventory_collection.document(item_id).delete()
            print(f"Item with ID {item_id} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False
    
    def search_items(self, field, value):
        """Searches for items based on field and value
        
        Args:
            field (str): The field to search
            value: The value to compare against
        
        Returns:
            list: List of matching items
        """
        try:
            items = []
            query = self.inventory_collection.where(field, '==', value)
            
            docs = query.stream()
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                items.append(item_data)
            
            return items
        except Exception as e:
            print(f"Error searching items: {e}")
            return []


def display_items(items):
    """Display items in a formatted table"""
    if not items:
        print("No items found.")
        return
    
    table = PrettyTable()
    # Determine columns from the first item
    if items:
        columns = ['id'] + [key for key in items[0].keys() if key != 'id' and key not in ['created_at', 'updated_at']]
        table.field_names = columns
        
        for item in items:
            row = [item.get(col, '') for col in columns]
            table.add_row(row)
    
    print(table)


def main():
    """Main function to run the inventory management system"""
    # Path to your Firebase credentials file
    creds_path = "inventory-management-sys-ea98a-firebase-adminsdk-fbsvc-b1132ffa2d.json"
    
    # Check if credentials file exists
    if not os.path.exists(creds_path):
        print(f"Error: Firebase credentials file not found at {creds_path}")
        creds_path = input("Enter the path to your Firebase credentials JSON file: ")
        if not os.path.exists(creds_path):
            print("Invalid path. Exiting.")
            return
    
    # Initialize inventory system
    inventory_system = InventoryManagementSystem(creds_path)
    
    while True:
        print("\n===== Inventory Management System =====")
        print("1. Add New Item")
        print("2. View All Items")
        print("3. Search for Item")
        print("4. Update Item")
        print("5. Delete Item")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == '1':
            # Add new item
            print("\n----- Add New Item -----")
            name = input("Enter item name: ")
            category = input("Enter item category: ")
            quantity = int(input("Enter quantity: "))
            price = float(input("Enter price: "))
            
            item_data = {
                'name': name,
                'category': category,
                'quantity': quantity,
                'price': price
            }
            
            inventory_system.add_item(item_data)
        
        elif choice == '2':
            # View all items
            print("\n----- All Items -----")
            items = inventory_system.get_all_items()
            display_items(items)
        
        elif choice == '3':
            # Search for items
            print("\n----- Search Items -----")
            print("Search by: 1. ID  2. Name  3. Category  4. Price  5. Quantity")
            search_choice = input("Enter your choice (1-5): ")
            
            if search_choice == '1':
                item_id = input("Enter item ID: ")
                item = inventory_system.get_item_by_id(item_id)
                if item:
                    display_items([item])
            else:
                field_map = {
                    '2': 'name',
                    '3': 'category',
                    '4': 'price',
                    '5': 'quantity'
                }
                
                if search_choice in field_map:
                    field = field_map[search_choice]
                    
                    if field in ['price', 'quantity']:
                        try:
                            value = float(input(f"Enter {field}: "))
                        except ValueError:
                            print("Invalid value. Must be a number.")
                            continue
                    else:
                        value = input(f"Enter {field}: ")
                    
                    items = inventory_system.search_items(field, value)
                    display_items(items)
                else:
                    print("Invalid choice.")
        
        elif choice == '4':
            # Update item
            print("\n----- Update Item -----")
            item_id = input("Enter item ID to update: ")
            
            item = inventory_system.get_item_by_id(item_id)
            if not item:
                continue
            
            print("Current item details:")
            display_items([item])
            
            print("\nEnter new details (leave blank to keep current value):")
            name = input(f"Name [{item.get('name', '')}]: ")
            category = input(f"Category [{item.get('category', '')}]: ")
            quantity_str = input(f"Quantity [{item.get('quantity', '')}]: ")
            price_str = input(f"Price [{item.get('price', '')}]: ")
            
            update_data = {}
            if name:
                update_data['name'] = name
            if category:
                update_data['category'] = category
            if quantity_str:
                try:
                    update_data['quantity'] = int(quantity_str)
                except ValueError:
                    print("Invalid quantity. Must be a number.")
            if price_str:
                try:
                    update_data['price'] = float(price_str)
                except ValueError:
                    print("Invalid price. Must be a number.")
            
            if update_data:
                inventory_system.update_item(item_id, update_data)
            else:
                print("No changes made.")
        
        elif choice == '5':
            # Delete item
            print("\n----- Delete Item -----")
            item_id = input("Enter item ID to delete: ")
            
            item = inventory_system.get_item_by_id(item_id)
            if item:
                print("Item to delete:")
                display_items([item])
                confirm = input("Are you sure you want to delete this item? (y/n): ")
                if confirm.lower() == 'y':
                    inventory_system.delete_item(item_id)
        
        elif choice == '6':
            # Exit
            print("Exiting Inventory Management System. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()