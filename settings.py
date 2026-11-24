from database import get_db

def get_settings():
    conn = get_db()
    row = conn.execute("SELECT * FROM settings WHERE id=1").fetchone()
    conn.close()
    return dict(row) if row else {}

def update_settings(business_name, phone, location, tin, footer, vat, service):
    conn = get_db()
    conn.execute("""
        UPDATE settings SET business_name=?, phone=?, location=?, tin=?,
        receipt_footer=?, vat_percent=?, service_charge=? WHERE id=1
    """, (business_name, phone, location, tin, footer, vat, service))
    conn.commit()
    conn.close()

def get_all_tables():
    conn = get_db()
    rows = conn.execute("SELECT * FROM tables ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_table(name, capacity):
    conn = get_db()
    try:
        conn.execute("INSERT INTO tables (name, capacity) VALUES (?,?)", (name, capacity))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def delete_table(table_id):
    conn = get_db()
    conn.execute("DELETE FROM tables WHERE id=?", (table_id,))
    conn.commit()
    conn.close()

def get_menu():
    conn = get_db()
    rows = conn.execute("SELECT * FROM menu ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_menu_item(name, category, price, cost):
    conn = get_db()
    conn.execute("INSERT INTO menu (name, category, price, cost) VALUES (?,?,?,?)", (name, category, price, cost))
    conn.commit()
    conn.close()

def update_menu_price(item_id, new_price):
    conn = get_db()
    conn.execute("UPDATE menu SET price=? WHERE id=?", (new_price, item_id))
    conn.commit()
    conn.close()

def log_activity(user, action):
    from datetime import datetime
    conn = get_db()
    conn.execute("INSERT INTO activity_log (user, action, date_time) VALUES (?,?,?)",
                 (user, action, datetime.now().strftime("%d-%b-%Y %I:%M %p")))
    conn.commit()
    conn.close()

def get_activity_log():
    conn = get_db()
    rows = conn.execute("SELECT * FROM activity_log ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]
