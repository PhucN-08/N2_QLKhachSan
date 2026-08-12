"""
gui_invoice.py
Frame Tkinter cho tab "Invoices" - bố cục đúng theo bản vẽ tay:
Booking / Customer / Room / Check in / Check out / Room price / Extra fee /
Total / Status / Payment  +  nút Create / Update / Export / Clear
+ bảng danh sách hóa đơn phía dưới
"""
import tkinter as tk
from tkinter import ttk, messagebox

import App.Adm.invoice_service as inv_srv


class InvoiceFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.bookings_cache = {}     # map "001 - A - Room 001" -> booking dict
        self.current_invoice_id = None
        self._build_form()
        self._build_table()
        self.refresh_bookings()
        self.refresh_table()

    # -------------------------------------------------------------
    # FORM (phần trên)
    # -------------------------------------------------------------
    def _build_form(self):
        frm = tk.LabelFrame(self, text="Invoice information", padx=10, pady=10)
        frm.pack(fill="x", padx=10, pady=10)

        # Booking
        tk.Label(frm, text="Booking:").grid(row=0, column=0, sticky="e", pady=3)
        self.cbo_booking = ttk.Combobox(frm, width=40, state="readonly")
        self.cbo_booking.grid(row=0, column=1, sticky="w", pady=3)
        self.cbo_booking.bind("<<ComboboxSelected>>", self.on_booking_selected)

        # Customer (readonly, tự điền)
        tk.Label(frm, text="Customer:").grid(row=1, column=0, sticky="e", pady=3)
        self.var_customer = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_customer, state="readonly", width=40).grid(
            row=1, column=1, sticky="w", pady=3)

        # Room
        tk.Label(frm, text="Room:").grid(row=2, column=0, sticky="e", pady=3)
        self.var_room = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_room, state="readonly", width=40).grid(
            row=2, column=1, sticky="w", pady=3)

        # Check in / Check out
        tk.Label(frm, text="Check in:").grid(row=3, column=0, sticky="e", pady=3)
        self.var_checkin = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_checkin, state="readonly", width=40).grid(
            row=3, column=1, sticky="w", pady=3)

        tk.Label(frm, text="Check out:").grid(row=4, column=0, sticky="e", pady=3)
        self.var_checkout = tk.StringVar()
        tk.Entry(frm, textvariable=self.var_checkout, state="readonly", width=40).grid(
            row=4, column=1, sticky="w", pady=3)

        # Room price
        tk.Label(frm, text="Room price:").grid(row=5, column=0, sticky="e", pady=3)
        self.var_price = tk.StringVar(value="0")
        tk.Entry(frm, textvariable=self.var_price, state="readonly", width=40).grid(
            row=5, column=1, sticky="w", pady=3)

        # Extra fee (nhập tay - phí phát sinh: minibar, giặt ủi...)
        tk.Label(frm, text="Extra fee:").grid(row=6, column=0, sticky="e", pady=3)
        self.var_extra = tk.StringVar(value="0")
        entry_extra = tk.Entry(frm, textvariable=self.var_extra, width=40)
        entry_extra.grid(row=6, column=1, sticky="w", pady=3)
        entry_extra.bind("<KeyRelease>", lambda e: self.recalc_total())

        # Total (tự tính)
        tk.Label(frm, text="Total:").grid(row=7, column=0, sticky="e", pady=3)
        self.var_total = tk.StringVar(value="0")
        tk.Entry(frm, textvariable=self.var_total, state="readonly", width=40).grid(
            row=7, column=1, sticky="w", pady=3)

        # Status
        tk.Label(frm, text="Status:").grid(row=8, column=0, sticky="e", pady=3)
        self.cbo_status = ttk.Combobox(frm, values=["Unpaid", "Paid", "Cancelled"],
                                        state="readonly", width=37)
        self.cbo_status.set("Unpaid")
        self.cbo_status.grid(row=8, column=1, sticky="w", pady=3)

        # Payment method
        tk.Label(frm, text="Payment:").grid(row=9, column=0, sticky="e", pady=3)
        self.cbo_payment = ttk.Combobox(frm, values=["Cash", "BankTransfer"],
                                         state="readonly", width=37)
        self.cbo_payment.set("Cash")
        self.cbo_payment.grid(row=9, column=1, sticky="w", pady=3)

        # Buttons
        btn_frm = tk.Frame(frm)
        btn_frm.grid(row=10, column=0, columnspan=2, pady=10)
        tk.Button(btn_frm, text="Create", width=10, command=self.on_create).pack(side="left", padx=5)
        tk.Button(btn_frm, text="Update", width=10, command=self.on_update).pack(side="left", padx=5)
        tk.Button(btn_frm, text="Export", width=10, command=self.on_export).pack(side="left", padx=5)
        tk.Button(btn_frm, text="Clear", width=10, command=self.on_clear).pack(side="left", padx=5)

    # -------------------------------------------------------------
    # TABLE (phần dưới)
    # -------------------------------------------------------------
    def _build_table(self):
        table_frm = tk.LabelFrame(self, text="Invoice list", padx=10, pady=10)
        table_frm.pack(fill="both", expand=True, padx=10, pady=10)

        # Bộ lọc nhanh
        filter_frm = tk.Frame(table_frm)
        filter_frm.pack(fill="x", pady=(0, 5))
        tk.Label(filter_frm, text="Status:").pack(side="left")
        self.cbo_filter_status = ttk.Combobox(
            filter_frm, values=["All", "Unpaid", "Paid", "Cancelled"],
            state="readonly", width=12)
        self.cbo_filter_status.set("All")
        self.cbo_filter_status.pack(side="left", padx=5)
        tk.Button(filter_frm, text="Filter", command=self.refresh_table).pack(side="left", padx=5)

        columns = ("id", "booking", "customer", "room", "amount", "status", "payment", "created_at")
        self.tree = ttk.Treeview(table_frm, columns=columns, show="headings", height=10)
        headers = ["ID", "Booking", "Customer", "Room", "Amount", "Status", "Payment", "Created At"]
        widths = [40, 70, 130, 80, 100, 80, 100, 140]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    # -------------------------------------------------------------
    # DATA LOADING
    # -------------------------------------------------------------
    def refresh_bookings(self):
        """Đổ danh sách booking CHƯA có hóa đơn vào combobox."""
        self.bookings_cache.clear()
        rows = inv_srv.get_bookings_without_invoice()
        labels = []
        for r in rows:
            label = f"{r['booking_id']:03d} - {r['customer_name']} - Room {r['room_number']}"
            self.bookings_cache[label] = r
            labels.append(label)
        self.cbo_booking["values"] = labels

    def refresh_table(self):
        status = self.cbo_filter_status.get() if hasattr(self, "cbo_filter_status") else "All"
        rows = inv_srv.get_invoices(status_filter=status)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=(
                r["id"], r["booking_id"], r["customer_name"], r["room_number"],
                f"{float(r['amount']):,.0f}", r["status"], r["payment_method"],
                r["created_at"]
            ))

    # -------------------------------------------------------------
    # EVENTS
    # -------------------------------------------------------------
    def on_booking_selected(self, event=None):
        label = self.cbo_booking.get()
        b = self.bookings_cache.get(label)
        if not b:
            return
        self.var_customer.set(b["customer_name"])
        self.var_room.set(f"{b['room_number']} - {b['room_type']}")
        self.var_checkin.set(str(b["checkin_date"]))
        self.var_checkout.set(str(b["checkout_date"]))
        self.var_price.set(str(b["price"]))
        self.recalc_total()

    def recalc_total(self):
        label = self.cbo_booking.get()
        b = self.bookings_cache.get(label)
        if not b:
            return
        try:
            extra = float(self.var_extra.get() or 0)
        except ValueError:
            extra = 0
        nights = inv_srv.calc_nights(b["checkin_date"], b["checkout_date"])
        total = inv_srv.calc_total(b["price"], nights, extra)
        self.var_total.set(f"{total:,.0f}")

    def on_create(self):
        label = self.cbo_booking.get()
        b = self.bookings_cache.get(label)
        if not b:
            messagebox.showwarning("Warning", "Please select a booking first.")
            return
        try:
            total = float(self.var_total.get().replace(",", ""))
            new_id = inv_srv.create_invoice(
                booking_id=b["booking_id"],
                amount=total,
                payment_method=self.cbo_payment.get(),
                status=self.cbo_status.get(),
            )
            messagebox.showinfo("Success", f"Invoice #{new_id} created.")
            self.on_clear()
            self.refresh_bookings()
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_update(self):
        if not self.current_invoice_id:
            messagebox.showwarning("Warning", "Please select an invoice from the list first.")
            return
        try:
            total = float(self.var_total.get().replace(",", ""))
            inv_srv.update_invoice(
                self.current_invoice_id,
                amount=total,
                status=self.cbo_status.get(),
                payment_method=self.cbo_payment.get(),
            )
            messagebox.showinfo("Success", "Invoice updated.")
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_export(self):
        if not self.current_invoice_id:
            messagebox.showwarning("Warning", "Please select an invoice from the list first.")
            return
        try:
            path = inv_srv.export_invoice_pdf(self.current_invoice_id)
            messagebox.showinfo("Success", f"Exported: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_clear(self):
        self.current_invoice_id = None
        self.cbo_booking.set("")
        self.var_customer.set("")
        self.var_room.set("")
        self.var_checkin.set("")
        self.var_checkout.set("")
        self.var_price.set("0")
        self.var_extra.set("0")
        self.var_total.set("0")
        self.cbo_status.set("Unpaid")
        self.cbo_payment.set("Cash")

    def on_row_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.current_invoice_id = int(values[0])
        # Điền lại form từ dữ liệu đầy đủ trong DB
        inv = inv_srv.get_invoice_full(self.current_invoice_id)
        if not inv:
            return
        self.var_customer.set(inv["customer_name"])
        self.var_room.set(f"{inv['room_number']} - {inv['room_type']}")
        self.var_checkin.set(str(inv["checkin_date"]))
        self.var_checkout.set(str(inv["checkout_date"]))
        self.var_price.set(str(inv["price"]))
        self.var_total.set(f"{float(inv['amount']):,.0f}")
        self.cbo_status.set(inv["status"])
        self.cbo_payment.set(inv["payment_method"])
        self.var_extra.set("0")  # extra fee không lưu riêng nên không khôi phục được


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Invoices")
    root.geometry("650x700")
    InvoiceFrame(root).pack(fill="both", expand=True)
    root.mainloop()
