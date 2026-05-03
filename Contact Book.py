import json
import os
import re
from datetime import datetime

# File path for storing contacts
CONTACTS_FILE = 'contacts.json'

def load_contacts():
    """
    Load contacts from the JSON file.
    If the file doesn't exist, return an empty list.
    """
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, 'r') as file:
                contacts = json.load(file)
                return contacts
        except json.JSONDecodeError:
            print("Error reading contacts file. Starting with empty contact list.")
            return []
    return []

def save_contacts(contacts):
    """
    Save the contacts list to the JSON file.
    This ensures data persists after the program closes.
    """
    try:
        with open(CONTACTS_FILE, 'w') as file:
            json.dump(contacts, file, indent=4)
        print("Contacts saved successfully!")
    except IOError as e:
        print(f"Error saving contacts: {e}")

def validate_name(name):
    """
    Validate that the name contains only letters and spaces.
    Returns True if valid, False otherwise.
    """
    # Check if name contains any digits
    if any(char.isdigit() for char in name):
        return False
    # Check if name is empty or only spaces
    if not name.strip():
        return False
    return True

def validate_phone(phone):
    """
    Validate that the phone number contains only digits and is reasonable length (7-15 digits).
    Returns True if valid, False otherwise.
    """
    # Remove any spaces or dashes for validation
    cleaned_phone = phone.replace(' ', '').replace('-', '')
    # Check if it contains only digits and is within reasonable length
    if cleaned_phone.isdigit() and 7 <= len(cleaned_phone) <= 15:
        return True
    return False

def validate_email(email):
    """
    Validate email format using a regular expression.
    Returns True if valid, False otherwise.
    """
    # Simple email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None

def add_contact(contacts):
    """
    Add a new contact to the contact list.
    Prompts user for name, phone, address, and email with validation.
    """
    print("\n--- Add New Contact ---")
    
    # Get and validate name
    while True:
        name = input("Enter contact name: ").strip()
        if validate_name(name):
            break
        else:
            print("Invalid name. Please enter a name with letters and spaces only (no numbers).")
    
    # Check if contact already exists
    if any(contact['name'].lower() == name.lower() for contact in contacts):
        print(f"A contact with the name '{name}' already exists!")
        return
    
    # Get and validate phone number
    while True:
        phone = input("Enter phone number: ").strip()
        if validate_phone(phone):
            break
        else:
            print("Invalid phone number. Please enter 7-15 digits (spaces and dashes allowed).")
    
    # Get address (no specific validation needed)
    address = input("Enter address: ").strip()
    
    # Get and validate email
    while True:
        email = input("Enter email address: ").strip()
        if email == "":  # Email is optional
            break
        if validate_email(email):
            break
        else:
            print("Invalid email format. Please enter a valid email (e.g., user@example.com).")
    
    # Create the contact dictionary
    contact = {
        'name': name,
        'phone': phone,
        'address': address,
        'email': email,
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Add to contacts list and save
    contacts.append(contact)
    save_contacts(contacts)
    print(f"Contact '{name}' added successfully!")

def view_contacts(contacts):
    """
    Display all contacts in a formatted list.
    Shows empty message if no contacts exist.
    """
    print("\n--- Contact List ---")
    
    if not contacts:
        print("No contacts saved yet.")
        return
    
    for index, contact in enumerate(contacts, 1):
        print(f"\n{index}. Name: {contact['name']}")
        print(f"   Phone: {contact['phone']}")
        print(f"   Address: {contact['address']}")
        print(f"   Email: {contact['email']}")

def search_contact(contacts):
    """
    Search for a contact by name and display their information.
    Uses case-insensitive search.
    """
    print("\n--- Search Contact ---")
    
    if not contacts:
        print("No contacts saved yet.")
        return
    
    search_name = input("Enter the name to search for: ").strip().lower()
    
    found_contacts = [contact for contact in contacts if search_name in contact['name'].lower()]
    
    if not found_contacts:
        print(f"No contacts found matching '{search_name}'.")
        return
    
    print(f"\nFound {len(found_contacts)} contact(s):")
    for contact in found_contacts:
        print(f"\nName: {contact['name']}")
        print(f"Phone: {contact['phone']}")
        print(f"Address: {contact['address']}")
        print(f"Email: {contact['email']}")

def delete_contact(contacts):
    """
    Delete a contact by name.
    Asks for confirmation before deleting.
    """
    print("\n--- Delete Contact ---")
    
    if not contacts:
        print("No contacts saved yet.")
        return
    
    delete_name = input("Enter the name of the contact to delete: ").strip()
    
    # Find the contact
    contact_found = None
    for contact in contacts:
        if contact['name'].lower() == delete_name.lower():
            contact_found = contact
            break
    
    if contact_found is None:
        print(f"Contact '{delete_name}' not found.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete '{contact_found['name']}'? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        contacts.remove(contact_found)
        save_contacts(contacts)
        print(f"Contact '{contact_found['name']}' deleted successfully!")
    else:
        print("Deletion cancelled.")

def display_menu():
    """
    Display the main menu options to the user.
    """
    print("\n========== CONTACT BOOK ==========")
    print("1. Add Contact")
    print("2. View All Contacts")
    print("3. Search Contact")
    print("4. Delete Contact")
    print("5. Exit")
    print("==================================")

def main():
    """
    Main function that runs the contact book application.
    Loads contacts, displays menu, and processes user choices in a loop.
    """
    print("Welcome to Contact Book!")
    contacts = load_contacts()
    
    while True:
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == '1':
            add_contact(contacts)
        elif choice == '2':
            view_contacts(contacts)
        elif choice == '3':
            search_contact(contacts)
        elif choice == '4':
            delete_contact(contacts)
        elif choice == '5':
            print("Thank you for using Contact Book. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

# Entry point of the program
if __name__ == '__main__':
    main()
