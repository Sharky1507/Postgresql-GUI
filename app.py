import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2

class PostgreSQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PostgreSQL Database GUI App")
        # add Database credentials
        self.db_params = {
            'host': 'localhost',
            'database': 'mydatabase',
            'user': 'postgres',
            'password': 'root@123',
            'port': '5432'
        }
        
        self.conn = psycopg2.connect(**self.db_params)
        self.create_table()
        
        self.create_widgets()
        
        self.selected_id = None
    # can change according to your tables
    def create_table(self):
        try:
            cur = self.conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    age INT NOT NULL
                )
            ''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating table: {e}")

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Student Details")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Age:").grid(row=1, column=0, padx=5, pady=5)
        self.age_entry = ttk.Entry(input_frame)
        self.age_entry.grid(row=1, column=1, padx=5, pady=5)

        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        ttk.Button(button_frame, text="Add", command=self.add_student).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Update", command=self.update_student).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Delete", command=self.delete_student).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_entries).grid(row=0, column=3, padx=5)

        self.tree = ttk.Treeview(self.root, columns=('ID', 'Name', 'Age'), show='headings')
        self.tree.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Age', text='Age')
        self.tree.column('ID', width=50)
        self.tree.column('Name', width=150)
        self.tree.column('Age', width=50)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.display_students()

    def run_query(self, query, parameters=()):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, parameters)
                self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            return False

    def add_student(self):
        name = self.name_entry.get()
        age = self.age_entry.get()
        
        if name and age:
            if self.run_query("INSERT INTO students (name, age) VALUES (%s, %s)", (name, age)):
                self.clear_entries()
                self.display_students()
        else:
            messagebox.showwarning("Input Error", "Please fill both name and age fields")

    def update_student(self):
        if self.selected_id:
            name = self.name_entry.get()
            age = self.age_entry.get()
            
            if name and age:
                if self.run_query("UPDATE students SET name = %s, age = %s WHERE id = %s", 
                                (name, age, self.selected_id)):
                    self.clear_entries()
                    self.display_students()
            else:
                messagebox.showwarning("Input Error", "Please fill both name and age fields")
        else:
            messagebox.showwarning("Selection Error", "Please select a record to update")

    def delete_student(self):
        if self.selected_id:
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
                if self.run_query("DELETE FROM students WHERE id = %s", (self.selected_id,)):
                    self.clear_entries()
                    self.display_students()
        else:
            messagebox.showwarning("Selection Error", "Please select a record to delete")

    def display_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT * FROM students ORDER BY id")
                rows = cur.fetchall()
                
                for row in rows:
                    self.tree.insert('', 'end', values=row)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item[0])
            self.selected_id = item['values'][0]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, item['values'][1])
            self.age_entry.delete(0, tk.END)
            self.age_entry.insert(0, item['values'][2])

    def clear_entries(self):
        self.selected_id = None
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PostgreSQLApp(root)
    root.mainloop()