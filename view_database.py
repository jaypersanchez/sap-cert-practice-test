import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class ViewDatabaseApp:
    def __init__(self, master, db_name):
        self.master = master
        self.master.title("View Database")
        self.db_name = db_name
        
        self.label = tk.Label(master, text="Select a table to view:")
        self.label.pack(pady=10)

        self.table_listbox = tk.Listbox(master)
        self.table_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        self.table_listbox.bind('<<ListboxSelect>>', self.on_table_select)

        # Create a Treeview for displaying data
        self.tree = ttk.Treeview(master)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.show_data_button = tk.Button(master, text="Show Data", command=self.show_data)
        self.show_data_button.pack(pady=10)

        self.load_tables()

    def load_tables(self):
        """Load table names from the database and display them in the listbox."""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        conn.close()
        
        for table in tables:
            self.table_listbox.insert(tk.END, table[0])  # Insert table names into the listbox

    def on_table_select(self, event):
        """Handle table selection from the listbox."""
        selected_index = self.table_listbox.curselection()
        if selected_index:
            self.selected_table = self.table_listbox.get(selected_index)
            self.tree.delete(*self.tree.get_children())  # Clear previous data

    def show_data(self):
        """Show data from the selected table."""
        selected_index = self.table_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("No Selection", "Please select a table to view.")
            return
        
        table_name = self.table_listbox.get(selected_index)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {table_name};")  # Retrieve all data from the selected table
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]  # Get column names
        
        conn.close()
        
        # Clear the Treeview
        self.tree.delete(*self.tree.get_children())
        
        # Define the columns
        self.tree["columns"] = column_names
        self.tree["show"] = "headings"  # Hide the first empty column

        # Create column headings
        for col in column_names:
            self.tree.heading(col, text=col)  # Set the column heading
            self.tree.column(col, anchor="center")  # Center align the column

        # Insert rows into the Treeview
        for row in rows:
            self.tree.insert("", "end", values=row)

# Main function to run the application
def main():
    db_name = 'questions.db'  # Your database name
    root = tk.Tk()
    app = ViewDatabaseApp(root, db_name)
    root.mainloop()

if __name__ == "__main__":
    main()
