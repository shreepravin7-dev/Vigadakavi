import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
from datetime import datetime
import os

class ExpenseManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Manager")
        self.root.geometry("800x600")
        
        # Data storage
        self.expenses = []
        self.load_expenses()
        
        # Create main frames
        self.create_input_frame()
        self.create_display_frame()
        self.create_stats_frame()
    
    def create_input_frame(self):
        input_frame = ttk.LabelFrame(self.root, text="Add Expense", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Date input
        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = DateEntry(input_frame, width=15, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Category input
        ttk.Label(input_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.categories = ["Food", "Transportation", "Entertainment", "Bills", "Shopping", "Other"]
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, values=self.categories)
        self.category_combo.grid(row=1, column=1, padx=5, pady=5)
        self.category_combo.set("Food")
        
        # Amount input
        ttk.Label(input_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Description input
        ttk.Label(input_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(input_frame, textvariable=self.desc_var)
        self.desc_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Add button
        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_display_frame(self):
        display_frame = ttk.LabelFrame(self.root, text="Expenses", padding="10")
        display_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        # Create Treeview
        columns = ("Date", "Category", "Amount", "Description")
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=0, column=0, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Delete button
        ttk.Button(display_frame, text="Delete Selected", command=self.delete_expense).grid(row=1, column=0, pady=5)
    
    def create_stats_frame(self):
        stats_frame = ttk.LabelFrame(self.root, text="Statistics", padding="10")
        stats_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=5, sticky="nsew")
        
        self.total_var = tk.StringVar()
        self.category_stats_var = tk.StringVar()
        
        ttk.Label(stats_frame, text="Total Expenses:").grid(row=0, column=0, pady=5)
        ttk.Label(stats_frame, textvariable=self.total_var).grid(row=0, column=1, pady=5)
        
        ttk.Label(stats_frame, text="Category-wise:").grid(row=1, column=0, columnspan=2, pady=5)
        self.stats_text = tk.Text(stats_frame, height=10, width=30)
        self.stats_text.grid(row=2, column=0, columnspan=2, pady=5)
    
    def add_expense(self):
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            expense = {
                "date": self.date_entry.get_date().strftime("%Y-%m-%d"),
                "category": self.category_var.get(),
                "amount": amount,
                "description": self.desc_var.get()
            }
            
            self.expenses.append(expense)
            self.update_display()
            self.save_expenses()
            self.clear_inputs()
            messagebox.showinfo("Success", "Expense added successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            index = self.tree.index(selected_item)
            self.expenses.pop(index)
            self.update_display()
            self.save_expenses()
    
    def update_display(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update expenses list
        for expense in self.expenses:
            self.tree.insert("", "end", values=(
                expense["date"],
                expense["category"],
                f"₹{expense['amount']:.2f}",
                expense["description"]
            ))
        
        self.update_statistics()
    
    def update_statistics(self):
        total = sum(expense["amount"] for expense in self.expenses)
        self.total_var.set(f"₹{total:.2f}")
        
        # Category-wise statistics
        category_totals = {}
        for expense in self.expenses:
            cat = expense["category"]
            category_totals[cat] = category_totals.get(cat, 0) + expense["amount"]
        
        # Update statistics text
        self.stats_text.delete(1.0, tk.END)
        for category, amount in category_totals.items():
            self.stats_text.insert(tk.END, f"{category}: ₹{amount:.2f}\n")
    
    def clear_inputs(self):
        self.amount_var.set("")
        self.desc_var.set("")
        self.date_entry.set_date(datetime.now())
    
    def save_expenses(self):
        with open("expenses.json", "w") as f:
            json.dump(self.expenses, f)
    
    def load_expenses(self):
        try:
            with open("expenses.json", "r") as f:
                self.expenses = json.load(f)
        except FileNotFoundError:
            self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseManager(root)
    root.mainloop()
