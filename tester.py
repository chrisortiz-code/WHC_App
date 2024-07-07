import customtkinter as ctk
from tkinter import messagebox

class CheckboxMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Checkbox Menu")
        self.geometry("400x300")

        self.tabButtons = [[]]

        self.checkbox_vars = {}

        self.create_checkbox_menu()
        self.create_save_button()

    def create_checkbox_menu(self):
        frame = ctk.CTkToplevel(self.window)
        frame.pack(pady=20, padx=20, fill='both', expand=True)

        for i in self.Databases:
            label = ctk.CTkLabel(frame, text=i.name)
            label.pack(anchor='w')

            self.checkbox_vars[i] = {}
            for table in i.tables:
                var = ctk.IntVar()
                checkbox = ctk.CTkCheckBox(frame, text=table, variable=var)
                checkbox.pack(anchor='w', padx=20)
                self.checkbox_vars[i][table] = var

    def create_save_button(self):
        save_button = ctk.CTkButton(self, text="Save", command=self.save)
        save_button.pack(pady=10)

    def save(self):
        results = {}
        for db, tables in self.checkbox_vars.items():
            results[db] = {table: var.get() for table, var in tables.items()}

        self.print_results(results)

    def print_results(self, results):
        print("Checkbox Results:")
        for db, tables in results.items():
            print(f"{db}:")
            for table, checked in tables.items():
                print(f"  {table}: {'Checked' if checked else 'Unchecked'}")

        messagebox.showinfo("Results", "Results printed to console")

if __name__ == "__main__":
    app = CheckboxMenu()
    app.mainloop()
