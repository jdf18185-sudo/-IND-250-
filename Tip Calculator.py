# Import the Tkinter library for creating graphical user interfaces
import tkinter as tk
from tkinter import ttk, messagebox

# Create the main application class
class TipCalculatorApp:
    """A GUI application to calculate tip amounts and split bills among diners."""
    
    def __init__(self, root):
        """Initialize the Tip Calculator GUI application."""
        self.root = root
        # Set the title of the window
        self.root.title("Tip Calculator")
        # Set the size of the window (width x height)
        self.root.geometry("500x600")
        # Make the window resizable
        self.root.resizable(False, False)
        
        # Create variables to store user input values
        # These variables automatically trigger callbacks when changed
        self.bill_amount = tk.StringVar()  # Store the bill amount as text
        self.tip_percentage = tk.DoubleVar(value=15.0)  # Store tip percentage (default 15%)
        self.num_diners = tk.IntVar(value=1)  # Store number of diners (default 1)
        
        # Trace the variables so calculations update automatically when they change
        self.bill_amount.trace("w", self.calculate)  # "w" means write/change
        self.tip_percentage.trace("w", self.calculate)
        self.num_diners.trace("w", self.calculate)
        
        # Create all the GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create and arrange all the GUI elements."""
        
        # ===== TITLE SECTION =====
        title_label = tk.Label(
            self.root,
            text="💰 Tip Calculator",
            font=("Arial", 24, "bold"),
            fg="#2E7D32"
        )
        title_label.pack(pady=20)
        
        # ===== BILL AMOUNT SECTION =====
        # Create a frame (container) for the bill amount section
        bill_frame = tk.Frame(self.root, bg="#F5F5F5", relief=tk.RIDGE, bd=2)
        bill_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Label for bill amount
        bill_label = tk.Label(bill_frame, text="Bill Amount ($):", font=("Arial", 12), bg="#F5F5F5")
        bill_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        # Entry field for user to type the bill amount
        bill_entry = tk.Entry(
            bill_frame,
            textvariable=self.bill_amount,
            font=("Arial", 14),
            width=20,
            justify=tk.RIGHT
        )
        bill_entry.pack(padx=10, pady=(0, 10))
        
        # ===== TIP PERCENTAGE SECTION =====
        # Create a frame for the tip percentage options
        tip_frame = tk.Frame(self.root, bg="#F5F5F5", relief=tk.RIDGE, bd=2)
        tip_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Label for tip percentage
        tip_label = tk.Label(tip_frame, text="Tip Percentage (%):", font=("Arial", 12, "bold"), bg="#F5F5F5")
        tip_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Create a sub-frame for the radio buttons to organize them nicely
        radio_frame = tk.Frame(tip_frame, bg="#F5F5F5")
        radio_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create radio button for 10% tip
        radio_10 = tk.Radiobutton(
            radio_frame,
            text="10%",
            variable=self.tip_percentage,
            value=10.0,
            font=("Arial", 11),
            bg="#F5F5F5"
        )
        radio_10.pack(side=tk.LEFT, padx=5)
        
        # Create radio button for 15% tip
        radio_15 = tk.Radiobutton(
            radio_frame,
            text="15%",
            variable=self.tip_percentage,
            value=15.0,
            font=("Arial", 11),
            bg="#F5F5F5"
        )
        radio_15.pack(side=tk.LEFT, padx=5)
        
        # Create radio button for 20% tip
        radio_20 = tk.Radiobutton(
            radio_frame,
            text="20%",
            variable=self.tip_percentage,
            value=20.0,
            font=("Arial", 11),
            bg="#F5F5F5"
        )
        radio_20.pack(side=tk.LEFT, padx=5)
        
        # ===== NUMBER OF DINERS SECTION =====
        # Create a frame for the number of diners section
        diners_frame = tk.Frame(self.root, bg="#F5F5F5", relief=tk.RIDGE, bd=2)
        diners_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Label for number of diners
        diners_label = tk.Label(diners_frame, text="Number of Diners:", font=("Arial", 12, "bold"), bg="#F5F5F5")
        diners_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Create a sub-frame for the spinbox and label
        spinbox_frame = tk.Frame(diners_frame, bg="#F5F5F5")
        spinbox_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Label showing current number of diners
        diners_value_label = tk.Label(spinbox_frame, text="1", font=("Arial", 14, "bold"), bg="#F5F5F5", width=3)
        diners_value_label.pack(side=tk.LEFT, padx=10)
        
        # Spinbox widget to select number of diners (1 to 6)
        # A spinbox is like a mini up/down counter
        diners_spinbox = tk.Spinbox(
            spinbox_frame,
            from_=1,  # Minimum value
            to=6,  # Maximum value
            textvariable=self.num_diners,
            width=5,
            font=("Arial", 12),
            justify=tk.CENTER
        )
        diners_spinbox.pack(side=tk.LEFT)
        
        # Update the label whenever the spinbox changes
        # This shows the current value selected
        def update_diners_label(*args):
            diners_value_label.config(text=str(self.num_diners.get()))
        self.num_diners.trace("w", update_diners_label)
        
        # ===== RESULTS SECTION =====
        # Create a frame for displaying the calculation results
        results_frame = tk.Frame(self.root, bg="#E8F5E9", relief=tk.RIDGE, bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Label for results section
        results_label = tk.Label(results_frame, text="Calculation Results", font=("Arial", 12, "bold"), bg="#E8F5E9")
        results_label.pack(pady=(10, 5))
        
        # ===== TIP AMOUNT DISPLAY =====
        tip_result_frame = tk.Frame(results_frame, bg="#E8F5E9")
        tip_result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(tip_result_frame, text="Tip Amount:", font=("Arial", 11), bg="#E8F5E9").pack(side=tk.LEFT)
        self.tip_amount_label = tk.Label(tip_result_frame, text="$0.00", font=("Arial", 11, "bold"), bg="#E8F5E9", fg="#1B5E20")
        self.tip_amount_label.pack(side=tk.RIGHT)
        
        # ===== TOTAL BILL DISPLAY =====
        total_result_frame = tk.Frame(results_frame, bg="#E8F5E9")
        total_result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(total_result_frame, text="Total (Bill + Tip):", font=("Arial", 11), bg="#E8F5E9").pack(side=tk.LEFT)
        self.total_label = tk.Label(total_result_frame, text="$0.00", font=("Arial", 11, "bold"), bg="#E8F5E9", fg="#1B5E20")
        self.total_label.pack(side=tk.RIGHT)
        
        # Add a separator line for visual organization
        tk.Frame(results_frame, height=2, bg="#4CAF50").pack(fill=tk.X, padx=10, pady=10)
        
        # ===== PER PERSON DISPLAY =====
        per_person_result_frame = tk.Frame(results_frame, bg="#E8F5E9")
        per_person_result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(per_person_result_frame, text="Per Person (including tip):", font=("Arial", 11, "bold"), bg="#E8F5E9").pack(side=tk.LEFT)
        self.per_person_label = tk.Label(per_person_result_frame, text="$0.00", font=("Arial", 14, "bold"), bg="#E8F5E9", fg="#D32F2F")
        self.per_person_label.pack(side=tk.RIGHT)
        
        # ===== BUTTON SECTION =====
        # Create a frame for the buttons at the bottom
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Reset button to clear all fields
        reset_button = tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_calculator,
            font=("Arial", 11),
            bg="#FFC107",
            width=10
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Quit/Exit button to close the application
        quit_button = tk.Button(
            button_frame,
            text="Quit",
            command=self.root.quit,
            font=("Arial", 11),
            bg="#F44336",
            fg="white",
            width=10
        )
        quit_button.pack(side=tk.RIGHT, padx=5)
        
    def calculate(self, *args):
        """Calculate and update all the tip and split calculations."""
        try:
            # Get the bill amount from the entry field
            # If the field is empty or has invalid input, set it to 0
            bill = float(self.bill_amount.get()) if self.bill_amount.get() else 0.0
            
            # Get the tip percentage selected by the user
            tip_percent = self.tip_percentage.get()
            
            # Get the number of diners
            num_diners = self.num_diners.get()
            
            # Calculate the tip amount (bill × tip percentage / 100)
            tip_amount = bill * (tip_percent / 100)
            
            # Calculate the total bill (original bill + tip)
            total_bill = bill + tip_amount
            
            # Calculate how much each person should pay
            per_person = total_bill / num_diners if num_diners > 0 else 0
            
            # Update the display labels with the calculated values
            # Format the numbers as currency with 2 decimal places
            self.tip_amount_label.config(text=f"${tip_amount:.2f}")
            self.total_label.config(text=f"${total_bill:.2f}")
            self.per_person_label.config(text=f"${per_person:.2f}")
            
        except ValueError:
            # If the user enters non-numeric data, show an error
            # Set all displays to $0.00
            self.tip_amount_label.config(text="$0.00")
            self.total_label.config(text="$0.00")
            self.per_person_label.config(text="$0.00")
    
    def reset_calculator(self):
        """Clear all fields and reset to default values."""
        # Clear the bill amount field
        self.bill_amount.set("")
        # Reset tip percentage to 15%
        self.tip_percentage.set(15.0)
        # Reset number of diners to 1
        self.num_diners.set(1)
        # This will trigger the calculate function automatically
        # and update all displays to $0.00


# Main program - create the window and run the application
if __name__ == "__main__":
    # Create the main window using Tkinter
    root = tk.Tk()
    
    # Create an instance of our TipCalculatorApp class
    app = TipCalculatorApp(root)
    
    # Start the application and display the window
    # This keeps the window open and responsive
    root.mainloop()
