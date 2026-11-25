import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3, os, json, shutil, datetime, sys

# ---------- PATHS & DB ----------
BASE = os.path.join(os.path.expanduser("~"), "GomaRestro")
os.makedirs(BASE, exist_ok=True)
os.makedirs(os.path.join(BASE, "Backups"), exist_ok=True)
DB = os.path.join(BASE, "goma.db")
SETTINGS_FILE = os.path.join(BASE, "settings.json")

DEFAULT_SETTINGS = {
    "business": "GomaRestro Demo - Sky Lounge",
    "phone": "+256 700 000000",
    "location": "Kampala, Uganda",
    "tin": "123456789",
    "vat": 18.0,
    "service": 5.0,
    "footer": "Thank you, Come Again! - GomaRestro"
}
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            d=json.load(open(SETTINGS_FILE))
            for k,v in DEFAULT_SETTINGS.items():
                if k not in d: d[k]=v
            return d
        except: return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()
def save_settings(s):
    json.dump(s, open(SETTINGS_FILE,"w"), indent=2)

SETTINGS = load_settings()
con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS tables_tbl(id INTEGER PRIMARY KEY, name TEXT, status TEXT DEFAULT 'Free')")
cur.execute("CREATE TABLE IF NOT EXISTS menu(id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL, stock INTEGER DEFAULT 100)")
cur.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, table_name TEXT, items TEXT, total REAL, status TEXT, created TEXT, cashier TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY, msg TEXT, created TEXT)")
con.commit()
# seed tables
if cur.execute("SELECT COUNT(*) FROM tables_tbl").fetchone()[0]==0:
    for n in ["Table 1","Table 2","Table 3","VIP 1","Garden 1","Bar Counter"]:
        cur.execute("INSERT INTO tables_tbl(name,status) VALUES(?,?)",(n,"Free"))
    con.commit()
# seed menu
if cur.execute("SELECT COUNT(*) FROM menu").fetchone()[0]==0:
    demo=[("Grilled Chicken","Food",35000,50),("Beef Pilau","Food",25000,50),("Pizza","Food",40000,30),("Soda","Drinks",5000,100),("Juice","Drinks",8000,80),("Coffee","Drinks",7000,80),("Beer","Bar",10000,100),("Water","Drinks",3000,200)]
    for n,c,p,s in demo:
        cur.execute("INSERT INTO menu(name,category,price,stock) VALUES(?,?,?,?)",(n,c,p,s))
    con.commit()

def log(msg):
    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute("INSERT INTO logs(msg,created) VALUES(?,?)",(msg,now))
    con.commit()

def backup_now():
    try:
        ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dst=os.path.join(BASE,"Backups",f"backup_{ts}.db")
        shutil.copy(DB,dst)
        # keep last 30
        files=sorted([os.path.join(BASE,"Backups",f) for f in os.listdir(os.path.join(BASE,"Backups"))])
        for f in files[:-30]:
            os.remove(f)
        return dst
    except Exception as e:
        return str(e)

USERS={"1234":("Admin","Admin"),"1111":("Waiter","Waiter"),"2222":("Cashier","Cashier")}
current_user=["Guest","Guest"]

# ---------- APP ----------
root=tk.Tk()
root.title(f"GomaRestro - {SETTINGS['business']}")
root.geometry("1050x650")
root.configure(bg="#f2f2f2")

# HEADER
header=tk.Frame(root,bg="#0f2a44",height=55)
header.pack(fill="x")
tk.Label(header,text="🍽️ GomaRestro",fg="white",bg="#0f2a44",font=("Arial",18,"bold")).pack(side="left",padx=12,pady=8)
user_lbl=tk.Label(header,text="Not logged in",fg="white",bg="#0f2a44",font=("Arial",10))
user_lbl.pack(side="right",padx=12)
def do_login():
    pin=simpledialog.askstring("Login","Enter PIN: Admin 1234 / Waiter 1111 / Cashier 2222",show="*")
    if pin in USERS:
        current_user[0],current_user[1]=USERS[pin]
        user_lbl.config(text=f"{current_user[0]} ({current_user[1]})")
        log(f"{current_user[0]} logged in")
        messagebox.showinfo("Welcome",f"Welcome {current_user[0]}!")
        refresh_all()
    elif pin:
        messagebox.showerror("Error","Wrong PIN")
tk.Button(header,text="Login",command=do_login,bg="#f5a623",font=("Arial",10,"bold")).pack(side="right",padx=5)

# TABS
nb=ttk.Notebook(root)
nb.pack(fill="both",expand=True,padx=8,pady=8)
tab_tables=tk.Frame(nb,bg="#f2f2f2"); tab_menu=tk.Frame(nb,bg="#f2f2f2")
tab_kitchen=tk.Frame(nb,bg="#f2f2f2"); tab_reports=tk.Frame(nb,bg="#f2f2f2")
tab_settings=tk.Frame(nb,bg="#f2f2f2"); tab_log=tk.Frame(nb,bg="#f2f2f2")
for t,txt in [(tab_tables,"📋 Tables & Orders"),(tab_menu,"🍔 Menu & Stock"),(tab_kitchen,"👨‍🍳 Kitchen"),(tab_reports,"📊 Sales Report"),(tab_settings,"⚙️ Settings"),(tab_log,"📜 Activity Log")]:
    nb.add(t,text=txt)

# ---------- TABLES & ORDERS ----------
tk.Label(tab_tables,text="Tap a Table to Take Order",font=("Arial",13,"bold"),bg="#f2f2f2").pack(pady=6)
tables_frame=tk.Frame(tab_tables,bg="#f2f2f2"); tables_frame.pack(fill="both",expand=True,padx=10)
cart={} # menu_id -> qty
current_table=[None]
def refresh_tables():
    for w in tables_frame.winfo_children(): w.destroy()
    rows=cur.execute("SELECT name,status FROM tables_tbl").fetchall()
    for i,(name,status) in enumerate(rows):
        col="#2ecc71" if status=="Free" else "#e74c3c"
        f=tk.Frame(tables_frame,bg=col,bd=2,relief="raised",width=160,height=90)
        f.grid(row=i//3,column=i%3,padx=10,pady=10,sticky="nsew")
        tk.Label(f,text=name,bg=col,fg="white",font=("Arial",12,"bold")).pack(pady=4)
        tk.Label(f,text=status,bg=col,fg="white").pack()
        tk.Button(f,text="Open Order",command=lambda n=name: open_order(n),bg="white").pack(pady=4)
    for c in range(3): tables_frame.grid_columnconfigure(c,weight=1)

def open_order(table_name):
    current_table[0]=table_name
    cart.clear()
    win=tk.Toplevel(root); win.title(f"Order - {table_name}"); win.geometry("700x550")
    tk.Label(win,text=f"ORDER FOR {table_name} - Cashier: {current_user[0]}",font=("Arial",12,"bold")).pack(pady=8)
    # menu list
    items=cur.execute("SELECT id,name,price,stock FROM menu").fetchall()
    listbox=tk.Listbox(win,font=("Arial",11),height=12); listbox.pack(fill="x",padx=10)
    for _id,n,p,s in items:
        listbox.insert("end",f"{n} - UGX {int(p):,}  (Stock: {s})")
    cart_lbl=tk.Label(win,text="Cart: Empty",font=("Arial",11),fg="#0f2a44"); cart_lbl.pack(pady=5)
    def add_item():
        sel=listbox.curselection()
        if not sel: return
        _id,n,p,s=items[sel[0]]
        if s<=0:
            messagebox.showerror("Stock","Out of stock!"); return
        cart[_id]=cart.get(_id,0)+1
        update_cart()
    def update_cart():
        total=0; txt=[]
        for _id,q in cart.items():
            n,p=cur.execute("SELECT name,price FROM menu WHERE id=?",(_id,)).fetchone()
            total+=p*q; txt.append(f"{n} x{q} = {int(p*q):,}")
        cart_lbl.config(text=" | ".join(txt) if txt else "Cart: Empty")
        total_lbl.config(text=f"Subtotal: UGX {int(total):,} | VAT {SETTINGS['vat']}% + Service {SETTINGS['service']}% = Grand: UGX {int(total*(1+SETTINGS['vat']/100+SETTINGS['service']/100)):,}")
    tk.Button(win,text="➕ Add Selected Item",command=add_item,bg="#2ecc71",fg="white",font=("Arial",11,"bold")).pack(pady=5)
    total_lbl=tk.Label(win,text="Subtotal: UGX 0",font=("Arial",11,"bold")); total_lbl.pack()
    def send_order():
        if not cart:
            messagebox.showerror("Error","Cart is empty"); return
        total=0; desc=[]
        for _id,q in cart.items():
            n,p,s=cur.execute("SELECT name,price,stock FROM menu WHERE id=?",(_id,)).fetchone()
            total+=p*q; desc.append(f"{n} x{q}")
            cur.execute("UPDATE menu SET stock=stock-? WHERE id=?",(q,_id))
        grand=total*(1+SETTINGS['vat']/100+SETTINGS['service']/100)
        now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cur.execute("INSERT INTO orders(table_name,items,total,status,created,cashier) VALUES(?,?,?,?,?,?)",(table_name,", ".join(desc),grand,"Pending",now,current_user[0]))
        cur.execute("UPDATE tables_tbl SET status='Occupied' WHERE name=?",(table_name,))
        con.commit(); log(f"New order {table_name}: {', '.join(desc)} = {int(grand):,}")
        messagebox.showinfo("Sent","Order sent to Kitchen!"); win.destroy(); refresh_all()
    def bill_and_close():
        if not cart and True:
            # bill existing pending order for this table
            pass
        send_order()
        # after send, ask print
        messagebox.showinfo("Receipt",f"--- {SETTINGS['business']} ---\n{SETTINGS['location']} | {SETTINGS['phone']}\nTIN: {SETTINGS['tin']}\nTable: {table_name}\n{cart_lbl.cget('text')}\n{total_lbl.cget('text')}\n{SETTINGS['footer']}\nThank you!")
    tk.Button(win,text="📤 Send to Kitchen",command=send_order,bg="#0f2a44",fg="white",font=("Arial",12,"bold")).pack(pady=6,fill="x",padx=20)
    tk.Button(win,text="🧾 Send + Print Receipt",command=bill_and_close,bg="#f5a623",font=("Arial",12,"bold")).pack(pady=4,fill="x",padx=20)

# ---------- MENU & STOCK ----------
tk.Label(tab_menu,text="Menu - Double-click price to edit, use buttons below",font=("Arial",11,"bold"),bg="#f2f2f2").pack(pady=6)
menu_tree=ttk.Treeview(tab_menu,columns=("ID","Name","Category","Price","Stock"),show="headings",height=14)
for c in ("ID","Name","Category","Price","Stock"): menu_tree.heading(c,text=c)
menu_tree.pack(fill="both",expand=True,padx=10)
def refresh_menu():
    for i in menu_tree.get_children(): menu_tree.delete(i)
    for r in cur.execute("SELECT id,name,category,price,stock FROM menu"):
        menu_tree.insert("", "end", values=(r[0],r[1],r[2],f"{int(r[3]):,}",r[4]))
        if r[4]<10: pass
def add_menu():
    n=simpledialog.askstring("Add Item","Item name (e.g. Rolex):")
    if not n: return
    c=simpledialog.askstring("Category","Category (Food/Drinks/Bar):") or "Food"
    p=simpledialog.askstring("Price","Price in UGX:")
    s=simpledialog.askstring("Stock","Starting stock:") or "50"
    try:
        cur.execute("INSERT INTO menu(name,category,price,stock) VALUES(?,?,?,?)",(n,c,float(p),int(s))); con.commit(); log(f"Added menu {n}"); refresh_menu()
    except: messagebox.showerror("Error","Enter valid numbers")
def del_menu():
    sel=menu_tree.selection()
    if not sel: return
    _id=menu_tree.item(sel[0])["values"][0]
    cur.execute("DELETE FROM menu WHERE id=?",(_id,)); con.commit(); refresh_menu()
def restock():
    sel=menu_tree.selection()
    if not sel: return
    _id=menu_tree.item(sel[0])["values"][0]
    q=simpledialog.askstring("Restock","Add how many?")
    if q:
        cur.execute("UPDATE menu SET stock=stock+? WHERE id=?",(int(q),_id)); con.commit(); refresh_menu()
mf=tk.Frame(tab_menu,bg="#f2f2f2"); mf.pack(pady=6)
for txt,cmd,col in [("➕ Add Item",add_menu,"#2ecc71"),("🗑️ Delete",del_menu,"#e74c3c"),("📦 Restock",restock,"#f5a623")]:
    tk.Button(mf,text=txt,command=cmd,bg=col,fg="white" if col!="#f5a623" else "black").pack(side="left",padx=5)

# ---------- KITCHEN ----------
tk.Label(tab_kitchen,text="Kitchen - Pending Orders",font=("Arial",12,"bold"),bg="#f2f2f2").pack(pady=6)
kitchen_list=tk.Listbox(tab_kitchen,font=("Arial",11),height=15); kitchen_list.pack(fill="both",expand=True,padx=10)
def refresh_kitchen():
    kitchen_list.delete(0,"end")
    for r in cur.execute("SELECT id,table_name,items,total,created FROM orders WHERE status='Pending' ORDER BY id"):
        kitchen_list.insert("end",f"#{r[0]} | {r[1]} | {r[2]} | UGX {int(r[3]):,} | {r[4]}")
def complete_order():
    sel=kitchen_list.curselection()
    if not sel: return
    txt=kitchen_list.get(sel[0]); oid=int(txt.split("|")[0].replace("#","").strip())
    table=txt.split("|")[1].strip()
    cur.execute("UPDATE orders SET status='Done' WHERE id=?",(oid,))
    # if no more pending for table, free it
    if cur.execute("SELECT COUNT(*) FROM orders WHERE table_name=? AND status='Pending'",(table,)).fetchone()[0]==0:
        cur.execute("UPDATE tables_tbl SET status='Free' WHERE name=?",(table,))
    con.commit(); log(f"Order #{oid} completed"); refresh_all()
    messagebox.showinfo("Done","Order marked Done, Table freed if no pending")
tk.Button(tab_kitchen,text="✅ Mark Selected as Done / Free Table",command=complete_order,bg="#2ecc71",fg="white",font=("Arial",11,"bold")).pack(pady=6)
tk.Button(tab_kitchen,text="🔄 Refresh Kitchen",command=refresh_kitchen,bg="#0f2a44",fg="white").pack(pady=2)

# ---------- REPORTS ----------
tk.Label(tab_reports,text="Daily Sales Report",font=("Arial",12,"bold"),bg="#f2f2f2").pack(pady=6)
rep_lbl=tk.Label(tab_reports,text="",font=("Arial",11),bg="#f2f2f2",justify="left"); rep_lbl.pack(padx=10,anchor="w")
rep_list=tk.Listbox(tab_reports,font=("Arial",10),height=12); rep_list.pack(fill="both",expand=True,padx=10,pady=5)
def refresh_reports():
    today=datetime.datetime.now().strftime("%Y-%m-%d")
    rows=cur.execute("SELECT * FROM orders WHERE created LIKE ?", (today+"%",)).fetchall()
    total=sum(r[3] for r in rows) if rows else 0
    rep_lbl.config(text=f"Today ({today})\nTotal Orders: {len(rows)}\nTotal Sales: UGX {int(total):,}")
    rep_list.delete(0,"end")
    for r in rows: rep_list.insert("end",f"#{r[0]} {r[1]} | {r[2]} | UGX {int(r[3]):,} | {r[4]} | {r[6]}")

# ---------- SETTINGS ----------
tk.Label(tab_settings,text="Business Settings",font=("Arial",12,"bold"),bg="#f2f2f2").pack(pady=6)
entries={}
for key,label in [("business","Business Name"),("phone","Phone"),("location","Location"),("tin","TIN"),("vat","VAT %"),("service","Service Charge %"),("footer","Receipt Footer")]:
    f=tk.Frame(tab_settings,bg="#f2f2f2"); f.pack(fill="x",padx=20,pady=3)
    tk.Label(f,text=label,width=20,anchor="w",bg="#f2f2f2").pack(side="left")
    e=tk.Entry(f,width=40); e.insert(0,str(SETTINGS[key])); e.pack(side="left",fill="x",expand=True); entries[key]=e
def save_set():
    for k,e in entries.items():
        try:
            if k in ("vat","service"): SETTINGS[k]=float(e.get())
            else: SETTINGS[k]=e.get()
        except: pass
    save_settings(SETTINGS); log("Settings updated"); root.title(f"GomaRestro - {SETTINGS['business']}")
    messagebox.showinfo("Saved","Settings saved!")
tk.Button(tab_settings,text="💾 Save Settings",command=save_set,bg="#2ecc71",fg="white",font=("Arial",11,"bold")).pack(pady=8)
tk.Button(tab_settings,text="💾 Backup Now",command=lambda: messagebox.showinfo("Backup",backup_now()),bg="#0f2a44",fg="white").pack(pady=4)
tk.Button(tab_settings,text="💾 Backup to Flash (Pick Folder)",command=lambda: messagebox.showinfo("Flash","Copy file from GomaRestro/Backups to your Flash - or use File Explorer"),bg="#f5a623").pack(pady=4)

# ---------- LOG ----------
log_list=tk.Listbox(tab_log,font=("Arial",10),height=20); log_list.pack(fill="both",expand=True,padx=10,pady=10)
def refresh_log():
    log_list.delete(0,"end")
    for msg,created in cur.execute("SELECT msg,created FROM logs ORDER BY id DESC LIMIT 100"):
        log_list.insert("end",f"{created} - {msg}")

def refresh_all():
    refresh_tables(); refresh_menu(); refresh_kitchen(); refresh_reports(); refresh_log()

refresh_all()
# auto backup on close
def on_close():
    backup_now(); root.destroy()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
