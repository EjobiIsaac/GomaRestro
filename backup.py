import shutil
import os
from datetime import datetime
from database import DB_PATH, BACKUP_DIR

def auto_backup():
    """Called when program closes. Keeps last 30 backups."""
    if not os.path.exists(DB_PATH):
        return None
    name = f"backup-{datetime.now().strftime('%d-%b-%Y-%I-%M%p')}.db"
    dest = os.path.join(BACKUP_DIR, name)
    shutil.copy2(DB_PATH, dest)
    # Keep last 30 only
    files = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")])
    for old in files[:-30]:
        try:
            os.remove(old)
        except:
            pass
    return dest

def backup_to_flash(flash_path):
    """Copy latest backup to Flash Drive."""
    latest = auto_backup()
    if latest and flash_path:
        dest = os.path.join(flash_path, f"GomaRestro-{datetime.now().strftime('%d-%b-%Y')}.db")
        shutil.copy2(latest, dest)
        return dest
    return None

def list_backups():
    """Return list of backup files for Restore screen."""
    if not os.path.exists(BACKUP_DIR):
        return []
    files = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")], reverse=True)
    return [os.path.join(BACKUP_DIR, f) for f in files]

def restore_backup(backup_file):
    """Restore database from a backup file."""
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, DB_PATH)
        return True
    return False
