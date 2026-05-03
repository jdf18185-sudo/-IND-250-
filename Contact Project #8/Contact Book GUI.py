import customtkinter as ctk
from tkinter import filedialog, messagebox
import json
import os
import re
from datetime import datetime

class ContactBookApp:
    """
    Main application class for the Contact Book GUI.
    Provides functionality to manage contacts: add, view, search, update, delete.
    Also allows loading different JSON files for contacts.
    """

    def __init__(self, root):
        """
        Initialize the Contact Book application.
        Sets up the GUI elements and loads initial contacts.
        """
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.contacts = []  # List to hold contact dictionaries
        self.contacts_file = 'contacts.json'  # Default file path
        self.load_contacts()  # Load contacts on startup

        # Main frame for layout
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons for main actions
        self.load_button = ctk.CTkButton(self.frame, text="Load JSON File", command=self.load_json_file)
        self.load_button.pack(pady=5)

        self.add_button = ctk.CTkButton(self.frame, text="Add Contact", command=self.add_contact)
        self.add_button.pack(pady=5)

        self.view_button = ctk.CTkButton(self.frame, text="View All Contacts", command=self.view_contacts)
        self.view_button.pack(pady=5)

        self.search_button = ctk.CTkButton(self.frame, text="Search Contact", command=self.search_contact)
        self.search_button.pack(pady=5)

        self.update_button = ctk.CTkButton(self.frame, text="Update Contact", command=self.update_contact)
        self.update_button.pack(pady=5)

        self.delete_button = ctk.CTkButton(self.frame, text="Delete Contact", command=self.delete_contact)
        self.delete_button.pack(pady=5)

        # Text area for displaying contacts or messages
        self.text_area = ctk.CTkTextbox(self.frame, wrap="word")
        self.text_area.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_area.configure(state="disabled")  # Read-only

    def load_contacts(self):
        """
        Load contacts from the current JSON file.
        If the file doesn't exist or is invalid, start with an empty list.
        """
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, 'r') as file:
                    self.contacts = json.load(file)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Error reading contacts file. Starting with empty list.")
                self.contacts = []
        else:
            self.contacts = []

    def save_contacts(self):
        """
        Save the current contacts list to the JSON file.
        Ensures data persistence.
        """
        try:
            with open(self.contacts_file, 'w') as file:
                json.dump(self.contacts, file, indent=4)
            messagebox.showinfo("Success", "Contacts saved successfully!")
        except IOError as e:
            messagebox.showerror("Error", f"Error saving contacts: {e}")

    def load_json_file(self):
        """
        Open a file dialog to select and load a different JSON file for contacts.
        Updates the contacts_file path and reloads contacts.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.contacts_file = file_path
            self.load_contacts()
            self.display_message(f"Loaded contacts from {file_path}")

    def validate_name(self, name):
        """
        Validate the contact name.
        Ensures it contains only letters and spaces, and is not empty.
        Returns True if valid, False otherwise.
        """
        if any(char.isdigit() for char in name) or not name.strip():
            return False
        return True

    def validate_phone(self, phone):
        """
        Validate the phone number.
        Ensures it contains 7-15 digits after removing spaces and dashes.
        Returns True if valid, False otherwise.
        """
        cleaned = phone.replace(' ', '').replace('-', '')
        return cleaned.isdigit() and 7 <= len(cleaned) <= 15

    def validate_email(self, email):
        """
        Validate the email address using a regular expression.
        Returns True if valid, False otherwise.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def add_contact(self):
        """
        Open a dialog to add a new contact.
        Prompts for name, phone, address, and email with validation.
        Adds the contact if valid and saves.
        """
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add Contact")
        dialog.geometry("400x400")

        # Input fields
        ctk.CTkLabel(dialog, text="Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Phone:").pack(pady=5)
        phone_entry = ctk.CTkEntry(dialog)
        phone_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Address:").pack(pady=5)
        address_entry = ctk.CTkEntry(dialog)
        address_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="Email:").pack(pady=5)
        email_entry = ctk.CTkEntry(dialog)
        email_entry.pack(pady=5)

        def save():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_entry.get().strip()
            email = email_entry.get().strip()

            if not self.validate_name(name):
                messagebox.showerror("Error", "Invalid name. Use letters and spaces only.")
                return
            if any(c['name'].lower() == name.lower() for c in self.contacts):
                messagebox.showerror("Error", "Contact with this name already exists.")
                return
            if not self.validate_phone(phone):
                messagebox.showerror("Error", "Invalid phone. Enter 7-15 digits.")
                return
            if email and not self.validate_email(email):
                messagebox.showerror("Error", "Invalid email format.")
                return

            contact = {
                'name': name,
                'phone': phone,
                'address': address,
                'email': email,
                'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.contacts.append(contact)
            self.save_contacts()
            dialog.destroy()
            self.display_message(f"Contact '{name}' added successfully!")

        ctk.CTkButton(dialog, text="Add", command=save).pack(pady=10)

    def view_contacts(self):
        """
        Display all contacts in the text area.
        Shows a formatted list or a message if no contacts exist.
        """
        self.text_area.configure(state="normal")
        self.text_area.delete("0.0", "end")
        if not self.contacts:
            self.text_area.insert("0.0", "No contacts saved yet.")
        else:
            for i, contact in enumerate(self.contacts, 1):
                self.text_area.insert("end", f"{i}. Name: {contact['name']}\n")
                self.text_area.insert("end", f"   Phone: {contact['phone']}\n")
                self.text_area.insert("end", f"   Address: {contact['address']}\n")
                self.text_area.insert("end", f"   Email: {contact['email']}\n\n")
        self.text_area.configure(state="disabled")

    def search_contact(self):
        """
        Open a dialog to search for contacts by name.
        Displays matching contacts in the text area.
        """
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Search Contact")
        dialog.geometry("400x200")

        ctk.CTkLabel(dialog, text="Enter name to search:").pack(pady=5)
        search_entry = ctk.CTkEntry(dialog)
        search_entry.pack(pady=5)

        def search():
            query = search_entry.get().strip().lower()
            found = [c for c in self.contacts if query in c['name'].lower()]
            self.text_area.configure(state="normal")
            self.text_area.delete("0.0", "end")
            if not found:
                self.text_area.insert("0.0", f"No contacts found matching '{query}'.")
            else:
                self.text_area.insert("end", f"Found {len(found)} contact(s):\n\n")
                for c in found:
                    self.text_area.insert("end", f"Name: {c['name']}\n")
                    self.text_area.insert("end", f"Phone: {c['phone']}\n")
                    self.text_area.insert("end", f"Address: {c['address']}\n")
                    self.text_area.insert("end", f"Email: {c['email']}\n\n")
            self.text_area.configure(state="disabled")
            dialog.destroy()

        ctk.CTkButton(dialog, text="Search", command=search).pack(pady=10)

    def update_contact(self):
        """
        Open a dialog to update an existing contact.
        Allows selecting a contact and editing their details with validation.
        """
        if not self.contacts:
            messagebox.showerror("Error", "No contacts to update.")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Update Contact")
        dialog.geometry("400x500")

        # Contact selection
        ctk.CTkLabel(dialog, text="Select contact:").pack(pady=5)
        names = [c['name'] for c in self.contacts]
        combo = ctk.CTkComboBox(dialog, values=names)
        combo.pack(pady=5)

        # Input fields
        ctk.CTkLabel(dialog, text="New Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="New Phone:").pack(pady=5)
        phone_entry = ctk.CTkEntry(dialog)
        phone_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="New Address:").pack(pady=5)
        address_entry = ctk.CTkEntry(dialog)
        address_entry.pack(pady=5)

        ctk.CTkLabel(dialog, text="New Email:").pack(pady=5)
        email_entry = ctk.CTkEntry(dialog)
        email_entry.pack(pady=5)

        def load_selected():
            selected = combo.get()
            for c in self.contacts:
                if c['name'] == selected:
                    name_entry.delete(0, "end")
                    name_entry.insert(0, c['name'])
                    phone_entry.delete(0, "end")
                    phone_entry.insert(0, c['phone'])
                    address_entry.delete(0, "end")
                    address_entry.insert(0, c['address'])
                    email_entry.delete(0, "end")
                    email_entry.insert(0, c['email'])
                    break

        combo.bind("<<ComboboxSelected>>", lambda e: load_selected())

        def update():
            selected = combo.get()
            if not selected:
                messagebox.showerror("Error", "Please select a contact.")
                return

            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            address = address_entry.get().strip()
            email = email_entry.get().strip()

            if not self.validate_name(name):
                messagebox.showerror("Error", "Invalid name.")
                return
            if not self.validate_phone(phone):
                messagebox.showerror("Error", "Invalid phone.")
                return
            if email and not self.validate_email(email):
                messagebox.showerror("Error", "Invalid email.")
                return

            for c in self.contacts:
                if c['name'] == selected:
                    c['name'] = name
                    c['phone'] = phone
                    c['address'] = address
                    c['email'] = email
                    break

            self.save_contacts()
            dialog.destroy()
            self.display_message(f"Contact updated to '{name}'.")

        ctk.CTkButton(dialog, text="Update", command=update).pack(pady=10)

    def delete_contact(self):
        """
        Open a dialog to delete an existing contact.
        Prompts for confirmation before deleting.
        """
        if not self.contacts:
            messagebox.showerror("Error", "No contacts to delete.")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Delete Contact")
        dialog.geometry("400x200")

        ctk.CTkLabel(dialog, text="Select contact to delete:").pack(pady=5)
        names = [c['name'] for c in self.contacts]
        combo = ctk.CTkComboBox(dialog, values=names)
        combo.pack(pady=5)

        def delete():
            selected = combo.get()
            if not selected:
                messagebox.showerror("Error", "Please select a contact.")
                return

            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{selected}'?")
            if confirm:
                self.contacts = [c for c in self.contacts if c['name'] != selected]
                self.save_contacts()
                dialog.destroy()
                self.display_message(f"Contact '{selected}' deleted successfully!")

        ctk.CTkButton(dialog, text="Delete", command=delete).pack(pady=10)

    def display_message(self, msg):
        """
        Display a temporary message in the text area.
        Used for feedback after operations.
        """
        self.text_area.configure(state="normal")
        self.text_area.delete("0.0", "end")
        self.text_area.insert("0.0", msg)
        self.text_area.configure(state="disabled")

def main():
    """
    Main entry point for the application.
    Creates the root window and starts the GUI event loop.
    """
    root = ctk.CTk()
    app = ContactBookApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
