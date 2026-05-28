import os
import zipfile
import time
import shutil
import sys

# Configure stdout and stderr to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# --- Configuration ---
HOME_DIR = os.path.expanduser("~")
SOURCE_DIR = r"c:\Users\msist\OneDrive\Desktop\Antigravity(DOLUNAY)"
BACKUP_DIR = os.path.join(HOME_DIR, "Desktop", "_backups")
MAX_BACKUPS = 4
DATE_STR = time.strftime("%Y-%m-%d")
BACKUP_NAME = f"Antigravity_backup_{DATE_STR}.zip"
BACKUP_PATH = os.path.join(BACKUP_DIR, BACKUP_NAME)
LOG_FILE = os.path.join(BACKUP_DIR, "backup_log.txt")

def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except Exception as e:
        print(f"Log write error: {e}")

def create_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        log_message(f"📁 Yedek dizini oluşturuldu: {BACKUP_DIR}")

def perform_backup():
    start_time = time.time()
    
    if os.path.exists(BACKUP_PATH):
        try:
            os.remove(BACKUP_PATH)
            log_message(f"⚠️ Aynı tarihli eski yedek silindi: {BACKUP_NAME}")
        except Exception as e:
            log_message(f"Error removing old backup: {e}")
            
    # Files to exclude (relative patterns)
    exclude_folders = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.gemini'}
    exclude_extensions = {'.mp4', '.mov', '.pyc', '.zip'}
    
    log_message("🚀 Yedekleme başlatılıyor...")
    log_message(f"📂 Kaynak: {SOURCE_DIR}")
    log_message(f"📦 Hedef: {BACKUP_PATH}")
    
    parent_dir = os.path.dirname(SOURCE_DIR)
    base_folder = os.path.basename(SOURCE_DIR)
    
    try:
        with zipfile.ZipFile(BACKUP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(SOURCE_DIR):
                # Filter directories in-place to prevent scanning excluded folders
                dirs[:] = [d for d in dirs if d not in exclude_folders]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    # Check extensions
                    _, ext = os.path.splitext(file.lower())
                    if ext in exclude_extensions:
                        continue
                    if file == ".env":
                        continue
                        
                    # Calculate path inside zip
                    arcname = os.path.relpath(file_path, parent_dir)
                    zipf.write(file_path, arcname)
                    
        end_time = time.time()
        duration = int(end_time - start_time)
        size_bytes = os.path.getsize(BACKUP_PATH)
        size_str = f"{size_bytes / (1024*1024):.2f} MB"
        
        return size_str, duration
    except Exception as e:
        log_message(f"❌ HATA: Yedekleme sırasında hata oluştu: {e}")
        return None, 0

def cleanup_old_backups():
    if not os.path.exists(BACKUP_DIR):
        return 0
    
    files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith("Antigravity_backup_") and f.endswith(".zip")]
    # Sort files by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    
    deleted = 0
    if len(files) > MAX_BACKUPS:
        for old_file in files[MAX_BACKUPS:]:
            try:
                os.remove(old_file)
                deleted += 1
                log_message(f"🗑️ Eski yedek silindi: {os.path.basename(old_file)}")
            except Exception as e:
                log_message(f"Error removing old backup {old_file}: {e}")
    return deleted

def count_backups():
    if not os.path.exists(BACKUP_DIR):
        return 0
    files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("Antigravity_backup_") and f.endswith(".zip")]
    return len(files)

def main():
    create_backup_dir()
    if not os.path.exists(SOURCE_DIR):
        log_message(f"❌ HATA: Kaynak dizin bulunamadı: {SOURCE_DIR}")
        return
        
    size, duration = perform_backup()
    if size:
        deleted = cleanup_old_backups()
        remaining = count_backups()
        log_message(f"✅ Backup başarılı: {BACKUP_NAME} ({size}) | Süre: {duration}s | Tutulan: {remaining} yedek")
        
        print("\n" + "="*50)
        print(f"✅ Yedekleme tamamlandı!")
        print(f"📦 Dosya: {BACKUP_NAME}")
        print(f"💾 Boyut: {size}")
        print(f"⏱️ Süre: {duration} saniye")
        print(f"📊 Toplam yedek: {remaining}/{MAX_BACKUPS}")
        if deleted > 0:
            print(f"🗑️ Silinen eski yedek: {deleted}")
        print("="*50 + "\n")

if __name__ == "__main__":
    main()
