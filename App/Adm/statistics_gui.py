"""
gui_report.py
Frame Tkinter cho tab "Reports" - lọc theo khoảng ngày, hiển thị thống kê
và xuất báo cáo Excel.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

import App.Adm.statistics_service as rpt_srv


class ReportFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self._build_filter()
        self._build_summary()
        self._build_table()
        self.load_report()

    # -------------------------------------------------------------
    def _build_filter(self):
        frm = tk.LabelFrame(self, text="Filter", padx=10, pady=10)
        frm.pack(fill="x", padx=10, pady=10)

        today = date.today()
        first_of_month = today.replace(day=1)

        tk.Label(frm, text="From (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5)
        self.var_from = tk.StringVar(value=str(first_of_month))
        tk.Entry(frm, textvariable=self.var_from, width=15).grid(row=0, column=1, padx=5)

        tk.Label(frm, text="To (YYYY-MM-DD):").grid(row=0, column=2, sticky="e", padx=5)
        self.var_to = tk.StringVar(value=str(today))
        tk.Entry(frm, textvariable=self.var_to, width=15).grid(row=0, column=3, padx=5)

        tk.Button(frm, text="Load", command=self.load_report).grid(row=0, column=4, padx=10)
        tk.Button(frm, text="Export Excel", command=self.on_export_excel).grid(row=0, column=5, padx=5)

    def _build_summary(self):
        frm = tk.LabelFrame(self, text="Summary", padx=10, pady=10)
        frm.pack(fill="x", padx=10, pady=5)

        self.var_revenue = tk.StringVar(value="0")
        self.var_unpaid = tk.StringVar(value="0")
        self.var_bookings = tk.StringVar(value="0")
        self.var_customers = tk.StringVar(value="0")
        self.var_cash = tk.StringVar(value="0")
        self.var_bank = tk.StringVar(value="0")

        rows = [
            ("Total revenue (Paid):", self.var_revenue),
            ("Total unpaid:", self.var_unpaid),
            ("Total bookings:", self.var_bookings),
            ("Total customers:", self.var_customers),
            ("Revenue - Cash:", self.var_cash),
            ("Revenue - Bank transfer:", self.var_bank),
        ]
        for i, (label, var) in enumerate(rows):
            r, c = divmod(i, 2)
            tk.Label(frm, text=label, font=("Arial", 10, "bold")).grid(
                row=r, column=c * 2, sticky="e", padx=5, pady=3)
            tk.Label(frm, textvariable=var).grid(row=r, column=c * 2 + 1, sticky="w", padx=5, pady=3)

    def _build_table(self):
        frm = tk.LabelFrame(self, text="Invoice details", padx=10, pady=10)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "booking", "customer", "room", "type", "amount", "status", "payment", "created_at")
        self.tree = ttk.Treeview(frm, columns=columns, show="headings", height=10)
        headers = ["ID", "Booking", "Customer", "Room", "Type", "Amount", "Status", "Payment", "Created At"]
        widths = [40, 60, 110, 60, 70, 90, 70, 100, 130]
        for col, head, w in zip(columns, headers, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)

    # -------------------------------------------------------------
    def load_report(self):
        try:
            start = self.var_from.get()
            end = self.var_to.get()
            stats = rpt_srv.get_statistics(start, end)
            rows = rpt_srv.get_invoice_rows(start, end)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.var_revenue.set(f"{stats['total_revenue']:,.0f}")
        self.var_unpaid.set(f"{stats['total_unpaid']:,.0f}")
        self.var_bookings.set(stats["total_bookings"])
        self.var_customers.set(stats["total_customers"])
        self.var_cash.set(f"{stats['revenue_by_payment'].get('Cash', 0):,.0f}")
        self.var_bank.set(f"{stats['revenue_by_payment'].get('BankTransfer', 0):,.0f}")

        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in rows:
            self.tree.insert("", "end", values=(
                r["id"], r["booking_id"], r["customer_name"], r["room_number"],
                r["room_type"], f"{float(r['amount']):,.0f}", r["status"],
                r["payment_method"], r["created_at"]
            ))

    def on_export_excel(self):
        try:
            path = rpt_srv.export_report_excel(self.var_from.get(), self.var_to.get())
            messagebox.showinfo("Success", f"Report exported: {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Reports")
    root.geometry("800x650")
    ReportFrame(root).pack(fill="both", expand=True)
    root.mainloop()
