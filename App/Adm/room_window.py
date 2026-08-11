import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error

import os
import sys

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

sys.path.append(ROOT_DIR)

from db import get_connection

TYPES = ("Standard", "Deluxe", "Suite")
STATUSES = ("Empty", "Booked", "Occupied", "Deactivated")


# ================= DATABASE =================

def connect():
    return get_connection()


def get_rooms():
    try:
        with connect() as db:
            cursor = db.cursor()

            cursor.execute(
                "SELECT id, room_number, room_type, status, price, image_url "
                "FROM rooms ORDER BY id"
            )

            rooms = cursor.fetchall()
            cursor.close()

            return rooms

    except Error as e:
        messagebox.showerror(
            "Lỗi",
            f"Không thể lấy danh sách phòng:\n{e}"
        )
        return []


def add_room(room_number, room_type, price, image_url=""):
    try:
        with connect() as db:
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO rooms
                (room_number, room_type, status, price, image_url)
                VALUES (%s, %s, 'Empty', %s, %s)
            """, (room_number, room_type, price, image_url))

            db.commit()
            cursor.close()

        return True

    except Error:
        return False


def update_room(room_id, room_number, room_type, status, price, image_url=""):
    try:
        with connect() as db:
            cursor = db.cursor()

            cursor.execute("""
                UPDATE rooms
                SET room_number=%s,
                    room_type=%s,
                    status=%s,
                    price=%s,
                    image_url=%s
                WHERE id=%s
            """, (
                room_number,
                room_type,
                status,
                price,
                image_url,
                room_id
            ))

            db.commit()

            success = cursor.rowcount > 0
            cursor.close()

            return success

    except Error:
        return False


def delete_room(room_id):
    try:
        with connect() as db:
            cursor = db.cursor()

            cursor.execute(
                "DELETE FROM rooms WHERE id=%s",
                (room_id,)
            )

            db.commit()

            success = cursor.rowcount > 0
            cursor.close()

            return success

    except Error as e:
        messagebox.showerror(
            "Lỗi",
            f"Không thể xóa phòng:\n{e}"
        )
        return False


def deactivate_room(room_id):
    try:
        with connect() as db:
            cursor = db.cursor()

            cursor.execute("""
                UPDATE rooms
                SET status='Deactivated'
                WHERE id=%s
            """, (room_id,))

            db.commit()

            success = cursor.rowcount > 0
            cursor.close()

            return success

    except Error as e:
        messagebox.showerror(
            "Lỗi",
            f"Không thể vô hiệu hóa phòng:\n{e}"
        )
        return False


# ================= GUI =================

def refresh():
    for item in table.get_children():
        table.delete(item)

    for room in get_rooms():
        table.insert("", "end", values=room)


def clear_form():
    id_var.set("")
    number_var.set("")
    type_var.set("Standard")
    status_var.set("Empty")
    price_var.set("")
    image_var.set("")


def add():
    number = number_var.get().strip()
    room_type = type_var.get()
    price = price_var.get().strip()
    image = image_var.get().strip()

    if not number or not price:
        messagebox.showwarning(
            "Thông báo",
            "Vui lòng nhập số phòng và giá."
        )
        return

    try:
        price = float(price)

        if price < 0:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Thông báo",
            "Giá phòng không hợp lệ."
        )
        return

    if add_room(number, room_type, price, image):
        messagebox.showinfo(
            "Thành công",
            "Đã thêm phòng."
        )

        clear_form()
        refresh()

    else:
        messagebox.showerror(
            "Lỗi",
            "Số phòng đã tồn tại."
        )


def update():
    room_id = id_var.get()

    if not room_id:
        messagebox.showwarning(
            "Thông báo",
            "Hãy chọn phòng cần cập nhật."
        )
        return

    number = number_var.get().strip()
    room_type = type_var.get()
    status = status_var.get()
    price = price_var.get().strip()
    image = image_var.get().strip()

    if not number or not price:
        messagebox.showwarning(
            "Thông báo",
            "Vui lòng nhập đầy đủ thông tin."
        )
        return

    try:
        price = float(price)

        if price < 0:
            raise ValueError

    except ValueError:
        messagebox.showwarning(
            "Thông báo",
            "Giá phòng không hợp lệ."
        )
        return

    if update_room(
        room_id,
        number,
        room_type,
        status,
        price,
        image
    ):
        messagebox.showinfo(
            "Thành công",
            "Đã cập nhật phòng."
        )

        clear_form()
        refresh()

    else:
        messagebox.showerror(
            "Lỗi",
            "Không thể cập nhật. Có thể số phòng đã tồn tại."
        )


def delete():
    room_id = id_var.get()

    if not room_id:
        messagebox.showwarning(
            "Thông báo",
            "Hãy chọn phòng cần xóa."
        )
        return

    if not messagebox.askyesno(
        "Xác nhận",
        "Bạn có chắc muốn xóa phòng này?"
    ):
        return

    if delete_room(room_id):
        messagebox.showinfo(
            "Thành công",
            "Đã xóa phòng."
        )

        clear_form()
        refresh()


def deactivate():
    room_id = id_var.get()

    if not room_id:
        messagebox.showwarning(
            "Thông báo",
            "Hãy chọn phòng cần vô hiệu hóa."
        )
        return

    if not messagebox.askyesno(
        "Xác nhận",
        "Bạn có chắc muốn vô hiệu hóa phòng này?"
    ):
        return

    if deactivate_room(room_id):
        messagebox.showinfo(
            "Thành công",
            "Phòng đã được chuyển sang trạng thái Deactivated."
        )

        clear_form()
        refresh()


def select_room(event):
    selected = table.selection()

    if not selected:
        return

    values = table.item(
        selected[0],
        "values"
    )

    id_var.set(values[0])
    number_var.set(values[1])
    type_var.set(values[2])
    status_var.set(values[3])
    price_var.set(values[4])
    image_var.set(values[5])


# ================= WINDOW =================

root = tk.Tk()

root.title("Quản lý phòng khách sạn")
root.geometry("1000x600")
root.minsize(900, 550)


# ---------- Title ----------

tk.Label(
    root,
    text="QUẢN LÝ PHÒNG KHÁCH SẠN",
    font=("Arial", 20, "bold")
).pack(pady=15)


# ---------- Form ----------

form = tk.Frame(root)
form.pack(padx=20, fill="x")


id_var = tk.StringVar()
number_var = tk.StringVar()
type_var = tk.StringVar(value="Standard")
status_var = tk.StringVar(value="Empty")
price_var = tk.StringVar()
image_var = tk.StringVar()


tk.Label(
    form,
    text="ID"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

tk.Entry(
    form,
    textvariable=id_var,
    state="readonly",
    width=15
).grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    form,
    text="Số phòng"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)

tk.Entry(
    form,
    textvariable=number_var,
    width=20
).grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)


tk.Label(
    form,
    text="Loại phòng"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=5
)

ttk.Combobox(
    form,
    textvariable=type_var,
    values=TYPES,
    state="readonly",
    width=18
).grid(
    row=1,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    form,
    text="Trạng thái"
).grid(
    row=1,
    column=2,
    padx=5,
    pady=5
)

ttk.Combobox(
    form,
    textvariable=status_var,
    values=STATUSES,
    state="readonly",
    width=18
).grid(
    row=1,
    column=3,
    padx=5,
    pady=5
)


tk.Label(
    form,
    text="Giá/ngày"
).grid(
    row=2,
    column=0,
    padx=5,
    pady=5
)

tk.Entry(
    form,
    textvariable=price_var,
    width=20
).grid(
    row=2,
    column=1,
    padx=5,
    pady=5
)


tk.Label(
    form,
    text="Image URL"
).grid(
    row=2,
    column=2,
    padx=5,
    pady=5
)

tk.Entry(
    form,
    textvariable=image_var,
    width=40
).grid(
    row=2,
    column=3,
    padx=5,
    pady=5
)


# ---------- Buttons ----------

buttons = tk.Frame(root)
buttons.pack(pady=15)


tk.Button(
    buttons,
    text="Thêm phòng",
    width=15,
    command=add
).pack(side="left", padx=5)


tk.Button(
    buttons,
    text="Cập nhật",
    width=15,
    command=update
).pack(side="left", padx=5)


tk.Button(
    buttons,
    text="Xóa phòng",
    width=15,
    command=delete
).pack(side="left", padx=5)


tk.Button(
    buttons,
    text="Vô hiệu hóa",
    width=15,
    command=deactivate
).pack(side="left", padx=5)


tk.Button(
    buttons,
    text="Làm mới",
    width=15,
    command=lambda: [clear_form(), refresh()]
).pack(side="left", padx=5)


# ---------- Table ----------

table_frame = tk.Frame(root)

table_frame.pack(
    padx=20,
    pady=5,
    fill="both",
    expand=True
)


columns = (
    "id",
    "room_number",
    "room_type",
    "status",
    "price",
    "image_url"
)


table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


headers = {
    "id": "ID",
    "room_number": "Số phòng",
    "room_type": "Loại phòng",
    "status": "Trạng thái",
    "price": "Giá/ngày",
    "image_url": "Image URL"
}


widths = {
    "id": 50,
    "room_number": 100,
    "room_type": 120,
    "status": 130,
    "price": 120,
    "image_url": 300
}


for column in columns:
    table.heading(
        column,
        text=headers[column]
    )

    table.column(
        column,
        width=widths[column],
        anchor="center"
    )


scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

table.configure(
    yscrollcommand=scrollbar.set
)

table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)

table.bind(
    "<<TreeviewSelect>>",
    select_room
)


refresh()

root.mainloop()