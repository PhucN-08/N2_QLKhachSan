import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "rooms.db"
TYPES = ("Standard", "Deluxe", "Suite")
STATUSES = ("Empty", "Booked", "Occupied", "Deactivated")


# ================= DATABASE =================

def connect():
    return sqlite3.connect(DB)


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_number VARCHAR(10) NOT NULL UNIQUE,
                room_type TEXT NOT NULL CHECK(room_type IN ('Standard','Deluxe','Suite')),
                status TEXT NOT NULL DEFAULT 'Empty'
                    CHECK(status IN ('Empty','Booked','Occupied','Deactivated')),
                price DECIMAL(10,2) NOT NULL,
                image_url VARCHAR(255)
            )
        """)


def get_rooms():
    with connect() as db:
        return db.execute(
            "SELECT id, room_number, room_type, status, price, image_url "
            "FROM rooms ORDER BY id"
        ).fetchall()


def add_room(room_number, room_type, price, image_url=""):
    try:
        with connect() as db:
            db.execute("""
                INSERT INTO rooms
                (room_number, room_type, status, price, image_url)
                VALUES (?, ?, 'Empty', ?, ?)
            """, (room_number, room_type, price, image_url))
        return True
    except sqlite3.IntegrityError:
        return False


def update_room(room_id, room_number, room_type, status, price, image_url=""):
    try:
        with connect() as db:
            cur = db.execute("""
                UPDATE rooms
                SET room_number=?, room_type=?, status=?, price=?, image_url=?
                WHERE id=?
            """, (room_number, room_type, status, price, image_url, room_id))
            return cur.rowcount > 0
    except sqlite3.IntegrityError:
        return False


def delete_room(room_id):
    with connect() as db:
        cur = db.execute("DELETE FROM rooms WHERE id=?", (room_id,))
        return cur.rowcount > 0


def deactivate_room(room_id):
    with connect() as db:
        cur = db.execute("""
            UPDATE rooms
            SET status='Deactivated'
            WHERE id=?
        """, (room_id,))
        return cur.rowcount > 0


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
        messagebox.showwarning("Thông báo", "Vui lòng nhập số phòng và giá.")
        return

    try:
        price = float(price)
        if price < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Thông báo", "Giá phòng không hợp lệ.")
        return

    if add_room(number, room_type, price, image):
        messagebox.showinfo("Thành công", "Đã thêm phòng.")
        clear_form()
        refresh()
    else:
        messagebox.showerror("Lỗi", "Số phòng đã tồn tại.")


def update():
    room_id = id_var.get()

    if not room_id:
        messagebox.showwarning("Thông báo", "Hãy chọn phòng cần cập nhật.")
        return

    number = number_var.get().strip()
    room_type = type_var.get()
    status = status_var.get()
    price = price_var.get().strip()
    image = image_var.get().strip()

    if not number or not price:
        messagebox.showwarning("Thông báo", "Vui lòng nhập đầy đủ thông tin.")
        return

    try:
        price = float(price)
        if price < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Thông báo", "Giá phòng không hợp lệ.")
        return

    if update_room(room_id, number, room_type, status, price, image):
        messagebox.showinfo("Thành công", "Đã cập nhật phòng.")
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
        messagebox.showwarning("Thông báo", "Hãy chọn phòng cần xóa.")
        return

    if not messagebox.askyesno(
        "Xác nhận",
        "Bạn có chắc muốn xóa phòng này?"
    ):
        return

    if delete_room(room_id):
        messagebox.showinfo("Thành công", "Đã xóa phòng.")
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

    values = table.item(selected[0], "values")

    id_var.set(values[0])
    number_var.set(values[1])
    type_var.set(values[2])
    status_var.set(values[3])
    price_var.set(values[4])
    image_var.set(values[5])


# ================= WINDOW =================

init_db()

root = tk.Tk()
root.title("Quản lý phòng khách sạn")
root.geometry("1000x600")
root.minsize(900, 550)

# ================= COLORS =================

NAVY = "#1F3F64"
NAVY_DARK = "#173451"
BACKGROUND = "#F3F5F7"
WHITE = "#FFFFFF"
LIGHT_BLUE = "#E8EEF5"
BORDER = "#D6DDE5"
TEXT = "#243447"
GRAY = "#7F8C8D"
GREEN = "#20B26B"
GREEN_DARK = "#17965A"
BLUE = "#2684C2"
BLUE_DARK = "#1C6C9F"
RED = "#D63C32"
RED_DARK = "#B52F27"
ORANGE = "#E67E22"
ORANGE_DARK = "#C96316"


root.configure(bg=BACKGROUND)

# ---------- ttk Style ----------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    fieldbackground=WHITE,
    foreground=TEXT,
    rowheight=32,
    borderwidth=0,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background=LIGHT_BLUE,
    foreground=TEXT,
    font=("Arial", 10, "bold"),
    padding=8,
    relief="flat"
)

style.map(
    "Treeview",
    background=[("selected", "#DCEAF7")],
    foreground=[("selected", TEXT)]
)

style.configure(
    "TCombobox",
    fieldbackground=WHITE,
    background=WHITE,
    foreground=TEXT,
    bordercolor=BORDER,
    lightcolor=BORDER,
    darkcolor=BORDER
)


# ---------- Title ----------

header = tk.Frame(
    root,
    bg=NAVY,
    height=70
)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="QUẢN LÝ PHÒNG KHÁCH SẠN",
    bg=NAVY,
    fg=WHITE,
    font=("Arial", 20, "bold")
).pack(side="left", padx=25)


# ---------- Form ----------

form_container = tk.Frame(
    root,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1
)
form_container.pack(
    padx=15,
    pady=(15, 10),
    fill="x"
)

tk.Label(
    form_container,
    text="Thông tin phòng",
    bg=WHITE,
    fg=TEXT,
    font=("Arial", 12, "bold")
).grid(
    row=0,
    column=0,
    columnspan=4,
    sticky="w",
    padx=25,
    pady=(18, 10)
)

form = tk.Frame(
    form_container,
    bg=WHITE
)
form.grid(
    row=1,
    column=0,
    columnspan=4,
    sticky="ew",
    padx=25
)

id_var = tk.StringVar()
number_var = tk.StringVar()
type_var = tk.StringVar(value="Standard")
status_var = tk.StringVar(value="Empty")
price_var = tk.StringVar()
image_var = tk.StringVar()

tk.Label(
    form,
    text="ID",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=0, column=0, padx=(0, 8), pady=6, sticky="w")

tk.Entry(
    form,
    textvariable=id_var,
    state="readonly",
    width=15,
    bg="#F5F6F7",
    readonlybackground="#F5F6F7",
    fg=TEXT,
    relief="solid",
    bd=1
).grid(row=0, column=1, padx=(0, 25), pady=6)

tk.Label(
    form,
    text="Số phòng",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=0, column=2, padx=(0, 8), pady=6, sticky="w")

tk.Entry(
    form,
    textvariable=number_var,
    width=20,
    bg=WHITE,
    fg=TEXT,
    relief="solid",
    bd=1
).grid(row=0, column=3, padx=(0, 25), pady=6)

tk.Label(
    form,
    text="Loại phòng",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=1, column=0, padx=(0, 8), pady=6, sticky="w")

ttk.Combobox(
    form,
    textvariable=type_var,
    values=TYPES,
    state="readonly",
    width=18
).grid(row=1, column=1, padx=(0, 25), pady=6)

tk.Label(
    form,
    text="Trạng thái",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=1, column=2, padx=(0, 8), pady=6, sticky="w")

ttk.Combobox(
    form,
    textvariable=status_var,
    values=STATUSES,
    state="readonly",
    width=18
).grid(row=1, column=3, padx=(0, 25), pady=6)

tk.Label(
    form,
    text="Giá/ngày",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=2, column=0, padx=(0, 8), pady=6, sticky="w")

tk.Entry(
    form,
    textvariable=price_var,
    width=20,
    bg=WHITE,
    fg=TEXT,
    relief="solid",
    bd=1
).grid(row=2, column=1, padx=(0, 25), pady=6)

tk.Label(
    form,
    text="Image URL",
    bg=WHITE,
    fg=GRAY,
    font=("Arial", 10)
).grid(row=2, column=2, padx=(0, 8), pady=6, sticky="w")

tk.Entry(
    form,
    textvariable=image_var,
    width=40,
    bg=WHITE,
    fg=TEXT,
    relief="solid",
    bd=1
).grid(row=2, column=3, padx=(0, 25), pady=6)


# ---------- Buttons ----------

buttons = tk.Frame(
    form_container,
    bg=WHITE
)
buttons.grid(
    row=2,
    column=0,
    columnspan=4,
    sticky="w",
    padx=25,
    pady=(10, 20)
)

tk.Button(
    buttons,
    text="Thêm phòng",
    width=15,
    command=add,
    bg=GREEN,
    fg=WHITE,
    activebackground=GREEN_DARK,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    font=("Arial", 10, "bold"),
    padx=5,
    pady=8,
    cursor="hand2"
).pack(side="left", padx=(0, 10))

tk.Button(
    buttons,
    text="Cập nhật",
    width=15,
    command=update,
    bg=BLUE,
    fg=WHITE,
    activebackground=BLUE_DARK,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    font=("Arial", 10, "bold"),
    padx=5,
    pady=8,
    cursor="hand2"
).pack(side="left", padx=10)

tk.Button(
    buttons,
    text="Xóa phòng",
    width=15,
    command=delete,
    bg=RED,
    fg=WHITE,
    activebackground=RED_DARK,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    font=("Arial", 10, "bold"),
    padx=5,
    pady=8,
    cursor="hand2"
).pack(side="left", padx=10)

tk.Button(
    buttons,
    text="Vô hiệu hóa",
    width=15,
    command=deactivate,
    bg=ORANGE,
    fg=WHITE,
    activebackground=ORANGE_DARK,
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    font=("Arial", 10, "bold"),
    padx=5,
    pady=8,
    cursor="hand2"
).pack(side="left", padx=10)

tk.Button(
    buttons,
    text="Làm mới",
    width=15,
    command=lambda: [clear_form(), refresh()],
    bg=GRAY,
    fg=WHITE,
    activebackground="#687778",
    activeforeground=WHITE,
    relief="flat",
    bd=0,
    font=("Arial", 10, "bold"),
    padx=5,
    pady=8,
    cursor="hand2"
).pack(side="left", padx=10)


# ---------- Table ----------

table_container = tk.Frame(
    root,
    bg=WHITE,
    highlightbackground=BORDER,
    highlightthickness=1
)
table_container.pack(
    padx=15,
    pady=(0, 15),
    fill="both",
    expand=True
)

table_frame = tk.Frame(
    table_container,
    bg=WHITE
)
table_frame.pack(
    padx=15,
    pady=15,
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