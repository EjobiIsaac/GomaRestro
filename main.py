import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import database
import settings as settings_logic
import backup as backup_logic

database.init_db()
current_user = "Admin"

root = tk.Tk()
root.title("GomaRestro - Restaurant & Lounge System")
root.geometry("1100x650")
root.configure(bg="#0B2C4A")

# --- TOP BAR ---
top = tk.Frame(root, bg="#0B2C4A", height=70)
top.pack(fill="x")
tk.Label(top, text="🍽️  GomaRestro", font=("Arial", 22, "bold"), bg="#0B2C4A", fg="white").pack(side="left", padx=20, pady=10)
tk.Label(top, text="Restaurant & Lounge System  |  Kampala", font=("Arial", 10), bg="#0B2C4A", fg="#FFC107").pack(side="left")
tk.Label(top, text="👤 Admin", font=("Arial", 11, "bold"), bg="#0B2C4A", fg="white").pack(side="right", padx=20)

# --- SETTINGS WINDOW ---
def show_settings():
    win = tk.Toplevel(root)
    win.title("⚙️ Settings - Management Can Change Everything")
    win.geometry("620x580")
    s = settings_logic.get_settings()

    fields = {}
    labels = [
        ("Business Name", "business_name"),
        ("Phone", "phone"),
        ("Location", "location"),
        ("TIN", "tin"),
        ("Receipt Footer", "receipt_footer"),
        ("VAT %", "vat_percent"),
        ("Service Charge %", "service_charge"),
    ]
    y = 20
    for label, key in labels:
        tk.Label(win, text=label, font=("Arial", 11, "bold")).place(x=30, y=y)
        e = tk.Entry(win, width=38, font=("Arial", 11))
        e.insert(0, str(s.get(key, "")))
        e.place(x=230, y=y)
        fields[key] = e
        y += 45

    def save():
        try:
            settings_logic.update_settings(
                fields["business_name"].get(), fields["phone"].get(), fields["location"].get(),
                fields["tin"].get(), fields["receipt_footer"].get(),
                float(fields["vat_percent"].get() or 0), float(fields["service_charge"].get() or 0)
            )
            settings_logic.log_activity(current_user, f"Changed settings to {fields['business_name'].get()}")
            messagebox.showinfo("Saved", "✅ Settings Saved! Business name, phone, VAT updated.")
            win.destroy()
            refresh_tables()
        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def do_flash():
        path = filedialog.askdirectory(title="Select Flash Drive")
        if path:
            dest = backup_logic.backup_to_flash(path)
            messagebox.showinfo("Backup", f"✅ Backup saved to:\n{dest}")

    tk.Button(win, text="💾  SAVE SETTINGS", bg="#28A745", fg="white", font=("Arial", 12, "bold"), command=save).place(x=200, y=y+10, width=220, height=42)
    tk.Button(win, text="💾 Backup to Flash", bg="#FFC107", font=("Arial", 11, "bold"), command=do_flash).place(x=200, y=y+60, width=220, height=35)
    tk.Button(win, text="📋 View Activity Log", bg="#0B2C4A", fg="white", font=("Arial", 11, "bold"), command=show_log).place(x=200, y=y+105, width=220, height=35)

def show_log():
    win = tk.Toplevel(root)
    win.title("📋 Activity Log")
    win.geometry("600x400")
    txt = tk.Text(win, font=("Arial", 10))
    txt.pack(fill="both", expand=True, padx=10, pady=10)
    for r in settings_logic.get_activity_log():
        txt.insert("end", f"{r['date_time']} - {r['user']} - {r['action']}\n")
    txt.config(state="disabled")

# --- MENU BAR ---
bar = tk.Frame(root, bg="white")
bar.pack(fill="x", pady=5)
tk.Button(bar, text="🪑 Tables", font=("Arial", 11, "bold"), bg="#0B2C4A", fg="white", width=14).pack(side="left", padx=5)
tk.Button(bar, text="🍗 Menu", font=("Arial", 11, "bold"), width=14, command=lambda: messagebox.showinfo("Menu", "Coming in V1.1 - Menu Management")).pack(side="left", padx=5)
tk.Button(bar, text="🧾 Orders", font=("Arial", 11, "bold"), width=14, command=lambda: messagebox.showinfo("Orders", "Coming in V1.1 - Orders + Kitchen")).pack(side="left", padx=5)
tk.Button(bar, text="📦 Stock", font=("Arial", 11, "bold"), width=14, command=lambda: messagebox.showinfo("Stock", "Coming in V1.2 - Stock")).pack(side="left", padx=5)
tk.Button(bar, text="📊 Reports", font=("Arial", 11, "bold"), width=14, command=lambda: messagebox.showinfo("Reports", "Coming in V1.2 - Reports")).pack(side="left", padx=5)
tk.Button(bar, text="⚙️ Settings", font=("Arial", 11, "bold"), bg="#FFC107", command=show_settings).pack(side="left", padx=5)

# --- TABLES AREA ---
tk.Label(root, text="🪑  TABLES - Click a table to open order  |  🟢 Free   🔴 Occupied   🟡 Bill Requested", bg="white", font=("Arial", 11, "bold")).pack(fill="x", pady=5)
tables_frame = tk.Frame(root, bg="white")
tables_frame.pack(fill="both", expand=True, padx=20, pady=10)

def refresh_tables():
    for w in tables_frame.winfo_children():
        w.destroy()
    rows = settings_logic.get_all_tables()
    for i, t in enumerate(rows):
        color = "#28A745" if t["status"] == "Free" else "#DC3545"
        btn = tk.Button(tables_frame, text=f"🪑\n{t['name']}\n{t['capacity']} seats\n{t['status']}", bg=color, fg="white", font=("Arial", 12, "bold"), width=16, height=5,
                        command=lambda n=t['name']: messagebox.showinfo("Table", f"Opening {n}\nOrders coming in V1.1"))
        btn.grid(row=i//4, column=i%4, padx=10, pady=10)

refresh_tables()

def on_close():
    backup_logic.auto_backup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
