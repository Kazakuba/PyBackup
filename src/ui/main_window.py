import os
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QProgressBar, QLabel, QTextEdit, QFileDialog, QRadioButton, 
    QButtonGroup, QMessageBox, QInputDialog
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Local Imports
from src.core.worker import BackupWorker
from src.utils.helpers import resource_path

CONFIG_FILE = "backups.json"

class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyBackup: Differential File Utility")
        self.resize(650, 550)

        # Icon setup
        icon_path = resource_path("assets/app.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.backups = self.load_backups()
        self.worker = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Saved Backup Tasks:"))
        self.list = QListWidget()
        self.list.addItems(self.backups.keys())
        self.list.itemDoubleClicked.connect(self.edit_backup_name)
        layout.addWidget(self.list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add New Task")
        self.del_btn = QPushButton("🗑️ Delete Task")
        self.run_btn = QPushButton("▶️ Run Backup")
        self.stop_btn = QPushButton("🛑 Stop Backup")
        self.stop_btn.setEnabled(False)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)

        self.verify_group = QButtonGroup(self)
        self.none_radio = QRadioButton("None")
        self.size_radio = QRadioButton("Size Only (Fast)")
        self.deep_radio = QRadioButton("Deep (Checksum)")
        self.none_radio.setChecked(True)
        self.verify_group.addButton(self.none_radio)
        self.verify_group.addButton(self.size_radio)
        self.verify_group.addButton(self.deep_radio)
        
        vr = QHBoxLayout()
        vr.addWidget(QLabel("Verification Mode:"))
        vr.addWidget(self.none_radio)
        vr.addWidget(self.size_radio)
        vr.addWidget(self.deep_radio)
        layout.addLayout(vr)

        layout.addWidget(QLabel("Overall Progress:"))
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Activity Log:"))
        self.clear_btn = QPushButton("Clear Log")
        status_row.addWidget(self.clear_btn, alignment=Qt.AlignRight)
        layout.addLayout(status_row)

        self.status = QTextEdit()
        self.status.setReadOnly(True)
        layout.addWidget(self.status)

        self.setLayout(layout)

        self.add_btn.clicked.connect(self.add_backup)
        self.del_btn.clicked.connect(self.delete_backup)
        self.run_btn.clicked.connect(self.run_backup)
        self.stop_btn.clicked.connect(self.stop_backup)
        self.clear_btn.clicked.connect(self.clear_log)

    def load_backups(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_backups(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.backups, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Could not save config: {e}")

    def add_backup(self):
        src = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if not src: return
        dst = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dst: return
        
        name, ok = QInputDialog.getText(self, "Backup Name", "Enter task name:")
        if ok and name and name not in self.backups:
            self.backups[name] = {"source": src, "destination": dst}
            self.save_backups()
            self.list.addItem(name)
            self.status.append(f"Task '{name}' added.")
        elif ok:
            QMessageBox.warning(self, "Error", "Invalid name or already exists.")

    def delete_backup(self):
        item = self.list.currentItem()
        if not item: return
        name = item.text()
        if QMessageBox.question(self, "Confirm", f"Delete '{name}'?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            del self.backups[name]
            self.save_backups()
            self.list.takeItem(self.list.row(item))

    def edit_backup_name(self, item):
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if ok and new_name and new_name != old_name and new_name not in self.backups:
            self.backups[new_name] = self.backups.pop(old_name)
            self.save_backups()
            item.setText(new_name)

    def get_verify_mode(self):
        if self.size_radio.isChecked(): return "size"
        if self.deep_radio.isChecked(): return "deep"
        return None

    def set_running_state(self, is_running):
        self.run_btn.setEnabled(not is_running)
        self.stop_btn.setEnabled(is_running)
        self.add_btn.setEnabled(not is_running)
        self.del_btn.setEnabled(not is_running)
        self.list.setEnabled(not is_running)
        self.none_radio.setEnabled(not is_running)
        self.size_radio.setEnabled(not is_running)
        self.deep_radio.setEnabled(not is_running)

    def run_backup(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Select a backup task.")
            return

        name = item.text()
        data = self.backups[name]
        mode = self.get_verify_mode()

        self.status.append(f"--- Starting: {name} ---")
        self.set_running_state(True)
        self.progress.setValue(0)

        self.worker = BackupWorker(data["source"], data["destination"], mode)
        self.worker.progress.connect(self.update_progress)
        self.worker.message.connect(self.show_message)
        self.worker.finished.connect(self.backup_finished)
        self.worker.start()

    def stop_backup(self):
        if self.worker and self.worker.isRunning():
            self.worker._is_running = False
            self.status.append("🛑 Stopping worker...")

    def update_progress(self, copied, skipped, total, processed):
        self.progress.setMaximum(total if total > 0 else 1)
        self.progress.setValue(processed)
        if total > 0:
            pct = int((processed / total) * 100)
            self.progress.setFormat(f"Processing... {processed}/{total} ({pct}%)")
        else:
            self.progress.setFormat("Scanning...")

    def show_message(self, msg):
        self.status.append(msg)

    def backup_finished(self, status):
        self.set_running_state(False)
        self.progress.setFormat("Complete.")
        if status == "done":
            QMessageBox.information(self, "Success", "Backup finished!")
        elif status == "error":
            QMessageBox.warning(self, "Failure", "Errors occurred. Check log.")

    def clear_log(self):
        self.status.clear()