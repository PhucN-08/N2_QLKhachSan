import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection


class CustomerFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.selected_id = None

        self.create_widgets()
        self.load_customers()

    # GIAO DIỆN

    def create_widgets(self):

        title = tk.Label(
            self,
            text="CUSTOMER MANAGEMENT",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=10)


        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=15)

        tk.Label(
            search_frame,
            text="Search:"
        ).pack(side=tk.LEFT)

        self.txt_search = tk.Entry(
            search_frame,
            width=35
        )
        self.txt_search.pack(
            side=tk.LEFT,
            padx=5
        )

        tk.Button(
            search_frame,
            text="Search",
            width=12,
            command=self.search_customer
        ).pack(side=tk.LEFT)

        tk.Button(
            search_frame,
            text="Refresh",
            width=12,
            command=self.clear_form
        ).pack(
            side=tk.LEFT,
            padx=5
        )


        form = tk.LabelFrame(
            self,
            text="Customer Information",
            padx=10,
            pady=10
        )

        form.pack(
            fill="x",
            padx=15,
            pady=10
        )

        tk.Label(
            form,
            text="Name"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=5
        )

        self.txt_name = tk.Entry(
            form,
            width=40
        )

        self.txt_name.grid(
            row=0,
            column=1,
            padx=10,
            pady=5
        )

        tk.Label(
            form,
            text="Email"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        self.txt_email = tk.Entry(
            form,
            width=40
        )

        self.txt_email.grid(
            row=1,
            column=1,
            padx=10,
            pady=5
        )

        tk.Label(
            form,
            text="Phone"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        self.txt_phone = tk.Entry(
            form,
            width=40
        )

        self.txt_phone.grid(
            row=2,
            column=1,
            padx=10,
            pady=5
        )

        tk.Label(
            form,
            text="Address"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=5
        )

        self.txt_address = tk.Entry(
            form,
            width=40
        )

        self.txt_address.grid(
            row=3,
            column=1,
            padx=10,
            pady=5
        )


        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Add",
            width=12,
            command=self.add_customer
        ).grid(
            row=0,
            column=0,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Update",
            width=12,
            command=self.update_customer
        ).grid(
            row=0,
            column=1,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Delete",
            width=12,
            command=self.delete_customer
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        tk.Button(
            button_frame,
            text="Clear",
            width=12,
            command=self.clear_form
        ).grid(
            row=0,
            column=3,
            padx=5
        )

      

        table_frame = tk.Frame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        columns = (
            "id",
            "name",
            "email",
            "phone",
            "address"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("email", text="Email")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("address", text="Address")

        self.tree.column(
            "id",
            width=60,
            anchor="center"
        )

        self.tree.column(
            "name",
            width=180
        )

        self.tree.column(
            "email",
            width=220
        )

        self.tree.column(
            "phone",
            width=120
        )

        self.tree.column(
            "address",
            width=250
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_tree_select
        )
    # HIỂN THỊ DỮ LIỆU

    def load_customers(self):

        self.clear_table()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT id, name, email, phone, address
                FROM customers
                ORDER BY id
            """

            cursor.execute(sql)

            rows = cursor.fetchall()

            for row in rows:
                self.tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:
            cursor.close()
            conn.close()

    # XÓA DỮ LIỆU TRONG TABLE

    def clear_table(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

    # XÓA DỮ LIỆU TRÊN FORM

    def clear_form(self):

        self.selected_id = None

        self.txt_name.delete(0, tk.END)
        self.txt_email.delete(0, tk.END)
        self.txt_phone.delete(0, tk.END)
        self.txt_address.delete(0, tk.END)
        self.txt_search.delete(0, tk.END)

        self.load_customers()

    # CLICK TREEVIEW

    def on_tree_select(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        values = self.tree.item(selected[0], "values")

        self.selected_id = values[0]

        self.txt_name.delete(0, tk.END)
        self.txt_email.delete(0, tk.END)
        self.txt_phone.delete(0, tk.END)
        self.txt_address.delete(0, tk.END)

        self.txt_name.insert(0, values[1])
        self.txt_email.insert(0, values[2])
        self.txt_phone.insert(0, values[3])
        self.txt_address.insert(0, values[4])

    # KIỂM TRA DỮ LIỆU

    def validate_input(self):

        name = self.txt_name.get().strip()
        email = self.txt_email.get().strip()
        phone = self.txt_phone.get().strip()

        if name == "":
            messagebox.showwarning(
                "Warning",
                "Customer name cannot be empty!"
            )
            return False

        if email != "" and "@" not in email:
            messagebox.showwarning(
                "Warning",
                "Invalid email!"
            )
            return False

        if phone != "" and not phone.isdigit():
            messagebox.showwarning(
                "Warning",
                "Phone number must contain only digits!"
            )
            return False

        return True
    # THÊM KHÁCH HÀNG
    

    def add_customer(self):

        if not self.validate_input():
            return

        name = self.txt_name.get().strip()
        email = self.txt_email.get().strip()
        phone = self.txt_phone.get().strip()
        address = self.txt_address.get().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                INSERT INTO customers(name, email, phone, address)
                VALUES(%s, %s, %s, %s)
            """

            cursor.execute(
                sql,
                (name, email, phone, address)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Customer added successfully!"
            )

            self.clear_form()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # CẬP NHẬT KHÁCH HÀNG

    def update_customer(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Warning",
                "Please select a customer!"
            )

            return

        if not self.validate_input():
            return

        name = self.txt_name.get().strip()
        email = self.txt_email.get().strip()
        phone = self.txt_phone.get().strip()
        address = self.txt_address.get().strip()

        try:

            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE customers
                SET
                    name=%s,
                    email=%s,
                    phone=%s,
                    address=%s
                WHERE id=%s
            """

            cursor.execute(
                sql,
                (
                    name,
                    email,
                    phone,
                    address,
                    self.selected_id
                )
            )

            conn.commit()

            if cursor.rowcount > 0:

                messagebox.showinfo(
                    "Success",
                    "Customer updated successfully!"
                )

            else:

                messagebox.showwarning(
                    "Notice",
                    "No data changed."
                )

            self.clear_form()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()

    # XÓA KHÁCH HÀNG

    def delete_customer(self):

        if self.selected_id is None:

            messagebox.showwarning(
                "Warning",
                "Please select a customer!"
            )

            return

        answer = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to delete this customer?"
        )

        if not answer:
            return

        try:

            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                DELETE FROM customers
                WHERE id=%s
            """

            cursor.execute(
                sql,
                (self.selected_id,)
            )

            conn.commit()

            if cursor.rowcount > 0:

                messagebox.showinfo(
                    "Success",
                    "Customer deleted successfully!"
                )

            else:

                messagebox.showwarning(
                    "Notice",
                    "Customer not found."
                )

            self.clear_form()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()
      
    # TÌM KIẾM KHÁCH HÀNG

    def search_customer(self):

        keyword = self.txt_search.get().strip()

        self.clear_table()

        try:

            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT
                    id,
                    name,
                    email,
                    phone,
                    address
                FROM customers
                WHERE
                    name LIKE %s
                    OR email LIKE %s
                    OR phone LIKE %s
                ORDER BY id
            """

            search = "%" + keyword + "%"

            cursor.execute(
                sql,
                (
                    search,
                    search,
                    search
                )
            )

            rows = cursor.fetchall()

            for row in rows:

                self.tree.insert(
                    "",
                    tk.END,
                    values=row
                )

            if len(rows) == 0:

                messagebox.showinfo(
                    "Notice",
                    "No matching customers found."
                )

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                str(e)
            )

        finally:

            cursor.close()
            conn.close()


# TEST


if __name__ == "__main__":

    root = tk.Tk()

    root.title("Customer Management")

    root.geometry("900x650")

    CustomerFrame(root).pack(
        fill="both",
        expand=True
    )

    root.mainloop()