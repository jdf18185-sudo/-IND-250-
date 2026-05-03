# Import libraries we need for this program
import pandas as pd  # pandas helps us work with data in a table format
import os  # os lets us check if files exist
from datetime import datetime  # datetime helps us get the current date and time
import matplotlib.pyplot as plt  # matplotlib helps us create charts and graphs

# Configuration - set the file name where we store expenses
FILE_NAME = "expenses.csv"

def initialize_df():
    """Ensures a CSV exists with the correct columns."""
    # Check if the expenses file already exists
    if os.path.exists(FILE_NAME):
        # If it exists, read and return the data from the file
        return pd.read_csv(FILE_NAME)
    else:
        # If the file doesn't exist, create a new empty one with the correct columns
        # Define the column names for our expense tracker
        columns = ["Date", "Category", "Description", "Amount"]
        # Create an empty DataFrame (table) with these columns
        df = pd.DataFrame(columns=columns)
        # Save the empty DataFrame to a CSV file
        df.to_csv(FILE_NAME, index=False)
        # Return the empty DataFrame
        return df

def add_expense(category, description, amount):
    """Appends a new expense to the CSV."""
    # Read the current expenses from the file
    df = pd.read_csv(FILE_NAME)

    # Create a dictionary with the new expense information
    new_entry = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Get current date and time
        "Category": category,  # What type of expense (Food, Rent, etc.)
        "Description": description,  # A note about the expense
        "Amount": float(amount)  # Convert the amount to a number
    }

    # Add the new expense to the existing data
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    
    # Sort expenses from highest amount to lowest amount
    df = df.sort_values("Amount", ascending=False).reset_index(drop=True)
    # Save the updated data back to the file
    df.to_csv(FILE_NAME, index=False)
    print("\n✅ Expense added successfully!")

def view_summary():
    """Displays data and basic stats using Pandas."""
    # Read all the expenses from the file
    df = pd.read_csv(FILE_NAME)

    # Check if there are any expenses recorded
    if df.empty:
        print("\n📭 No expenses recorded yet.")
        return

    # Display all expenses in a table format
    print("\n--- Current Expenses ---")
    print(df)

    # Calculate and display summary information
    total = df["Amount"].sum()  # Add up all the expenses
    average = df["Amount"].mean()  # Calculate the average expense
    print(f"\n💰 Total Spent: ${total:.2f}")
    print(f"📊 Average Expense: ${average:.2f}")

    # Show how much was spent in each category
    print("\n--- Spending by Category ---")
    category_spending = df.groupby("Category")["Amount"].sum()
    # Format it nicely so it doesn't show "Name: Amount, dtype: float64"
    for category, amount in category_spending.items():
        print(f"  {category}: ${amount:.2f}")


def edit_expense():
    """Allows editing an existing expense by index."""
    # Read all expenses from the file
    df = pd.read_csv(FILE_NAME)
    
    # Check if there are any expenses to edit
    if df.empty:
        print("\n📭 No expenses to edit.")
        return
    
    # Show the user all current expenses so they can pick one to edit
    print("\n--- Current Expenses ---")
    print(df)
    
    # Use try/except to catch errors if the user enters bad data
    try:
        # Ask user which expense they want to edit (by row number)
        index = int(input("\nEnter the index of the expense to edit: "))
        # Make sure the index is valid (between 0 and the number of expenses)
        if index < 0 or index >= len(df):
            print("❌ Invalid index.")
            return
        
        # Get the expense at that row
        expense = df.loc[index]
        print(f"\nEditing expense at index {index}:")
        print(f"Current: Date={expense['Date']}, Category={expense['Category']}, Description={expense['Description']}, Amount=${expense['Amount']:.2f}")
        
        # Ask user for new values (or keep old ones if they just press Enter)
        category = input(f"Enter Category [{expense['Category']}]: ") or expense['Category']
        description = input(f"Enter Description [{expense['Description']}]: ") or expense['Description']
        amount = input(f"Enter Amount [${expense['Amount']:.2f}]: ") or str(expense['Amount'])
        
        # Update the expense with new values and current date/time
        df.at[index, 'Date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Update date/time automatically
        df.at[index, 'Category'] = category
        df.at[index, 'Description'] = description
        df.at[index, 'Amount'] = float(amount)
        
        # Sort expenses from highest to lowest amount
        df = df.sort_values("Amount", ascending=False).reset_index(drop=True)
        # Save changes back to the file
        df.to_csv(FILE_NAME, index=False)
        print("\n✅ Expense updated successfully!")
    except ValueError:
        # If something went wrong with the input, show an error message
        print("❌ Invalid input.")


def delete_expense():
    """Deletes an expense by index."""
    # Read all expenses from the file
    df = pd.read_csv(FILE_NAME)
    
    # Check if there are any expenses to delete
    if df.empty:
        print("\n📭 No expenses to delete.")
        return
    
    # Show the user all current expenses so they can pick one to delete
    print("\n--- Current Expenses ---")
    print(df)
    
    # Use try/except to catch errors if the user enters bad data
    try:
        # Ask user which expense they want to delete (by row number)
        index = int(input("\nEnter the index of the expense to delete: "))
        # Make sure the index is valid
        if index < 0 or index >= len(df):
            print("❌ Invalid index.")
            return
        
        # Save the deleted expense info so we can show it to the user
        deleted = df.loc[index]
        # Remove the expense from the data
        df = df.drop(index).reset_index(drop=True)
        
        # Sort expenses from highest to lowest amount
        df = df.sort_values("Amount", ascending=False).reset_index(drop=True)
        # Save the updated data back to the file
        df.to_csv(FILE_NAME, index=False)
        print(f"\n✅ Deleted: {deleted['Description']} (${deleted['Amount']:.2f})")
    except ValueError:
        # If something went wrong with the input, show an error message
        print("❌ Invalid input.")


def plot_expenses():
    """Generates a pie chart of all expenses."""
    # Read all expenses from the file
    df = pd.read_csv(FILE_NAME)
    
    # Check if there are any expenses to show in a chart
    if df.empty:
        print("\n📭 No expenses to plot.")
        return
    
    # Group expenses by category and add up the amounts in each category
    category_totals = df.groupby("Category")["Amount"].sum()
    
    # Create a new chart figure with a specific size (10 inches wide, 8 inches tall)
    plt.figure(figsize=(10, 8))
    # Draw a pie chart showing the total for each category
    plt.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=140)
    # Add a title to the chart
    plt.title("Expense Distribution by Category")
    # Make the pie chart look like a perfect circle
    plt.axis('equal')
    # Adjust the layout so nothing gets cut off
    plt.tight_layout()
    # Display the chart to the user
    plt.show()
    print("\n✅ Pie chart generated!")


def main():
    # Set up the expense file (creates it if it doesn't exist)
    initialize_df()

    # Keep showing the menu until the user chooses to exit
    while True:
        # Show the menu options to the user
        print("\n--- 📈 Expense Tracker CLI ---")
        print("1. Add Expense")
        print("2. View Summary")
        print("3. Delete Expense")
        print("4. Edit Expense")
        print("5. Plot")
        print("6. Exit")

        # Ask user to pick a menu option
        choice = input("Select an option: ")

        # Do different things based on what the user chose
        if choice == "1":
            # Ask user for expense details and add it
            cat = input("Enter Category (e.g., Food, Rent, Fun): ")
            desc = input("Short Description: ")
            amt = input("Amount: ")
            add_expense(cat, desc, amt)
        elif choice == "2":
            # Show a summary of all expenses
            view_summary()
        elif choice == "3":
            # Delete an expense
            delete_expense()
        elif choice == "4":
            # Edit an existing expense
            edit_expense()
        elif choice == "5":
            # Show a pie chart of expenses
            plot_expenses()
        elif choice == "6":
            # Exit the program
            print("Goodbye!")
            break
        else:
            # If user enters an invalid option, tell them to try again
            print("Invalid choice, try again.")


# This checks if the script is being run directly (not imported as a library)
# If so, start the program by calling the main function
if __name__ == "__main__":
    main()