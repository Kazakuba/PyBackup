import os
import shutil
import hashlib
from PySide6.QtCore import QThread, Signal

class BackupWorker(QThread):
    progress = Signal(int, int, int, int)
    finished = Signal(str)
    message = Signal(str)

    def __init__(self, source, destination, verify_mode):
        super().__init__()
        self.source = source
        self.destination = destination
        self.verify_mode = verify_mode
        self._is_running = True

    def file_same(self, src, dst):
        return os.path.exists(dst) and os.path.getsize(src) == os.path.getsize(dst)

    def hash_file(self, path):
        h = hashlib.md5()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception as e:
            self.message.emit(f"Error hashing {path}: {e}")
            return None

    def verify_backup(self, deep=False):
        mismatches = []
        for root, _, files in os.walk(self.source):
            if not self._is_running: break
            
            rel_path = os.path.relpath(root, self.source)
            dest_dir = os.path.join(self.destination, rel_path)
            
            for file in files:
                if not self._is_running: break
                
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir, file)
                
                if not os.path.exists(dst_file):
                    mismatches.append((src_file, "missing"))
                    continue
                
                if os.path.getsize(src_file) != os.path.getsize(dst_file):
                    mismatches.append((src_file, "size mismatch"))
                    continue
                
                if deep:
                    src_hash = self.hash_file(src_file)
                    dst_hash = self.hash_file(dst_file)
                    if src_hash is None or dst_hash is None:
                        continue

                    if src_hash != dst_hash:
                        mismatches.append((src_file, "hash mismatch"))
        return mismatches

    def run(self):
        self.message.emit(f"Worker started for {self.source}")
        
        if not os.path.exists(self.source):
            self.message.emit("Error: Source folder not found!")
            self.finished.emit("error")
            return

        total_files = sum(len(files) for _, _, files in os.walk(self.source))
        copied = skipped = processed = 0

        for root, _, files in os.walk(self.source):
            if not self._is_running:
                self.message.emit("Backup process cancelled.")
                break
            
            rel_path = os.path.relpath(root, self.source)
            dest_dir = os.path.join(self.destination, rel_path)
            os.makedirs(dest_dir, exist_ok=True)

            for file in files:
                if not self._is_running: break
                
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dest_dir, file)

                try:
                    if self.file_same(src_file, dst_file):
                        skipped += 1
                    else:
                        shutil.copy2(src_file, dst_file)
                        copied += 1
                except Exception as e:
                    self.message.emit(f"Error processing {src_file}: {e}")
                
                processed += 1
                self.progress.emit(copied, skipped, total_files, processed)

        if self.verify_mode and self._is_running:
            self.message.emit(f"Verification mode active: {self.verify_mode}. Starting check...")
            deep = self.verify_mode == "deep"
            mismatches = self.verify_backup(deep=deep)
            
            if mismatches:
                self.message.emit(f"Verification failed: Found {len(mismatches)} discrepancies!")
                for src_file, reason in mismatches:
                    self.message.emit(f"  - {reason}: {src_file}")
                self.finished.emit("error")
                return
            else:
                self.message.emit("Verification successful. ✅")

        if self._is_running:
            self.message.emit(f"Backup complete. Copied: {copied}, Skipped: {skipped}.")
            self.finished.emit("done")
        else:
            self.finished.emit("cancelled")