# PyBackup: Differential File Backup Utility

A robust, GUI-based backup tool built with Python and PySide6. This application uses a multithreaded architecture to perform differential backups, ensuring that only modified or new files are copied, saving time and storage space.

## 🚀 Features

* **Differential Backup Logic:** Skips files that already exist and haven't changed (based on size/metadata).
* **Multithreaded Architecture:** Uses `QThread` to keep the UI responsive during heavy I/O operations.
* **Integrity Verification:**
    * *Quick Mode:* Verifies based on file size.
    * *Deep Mode:* Calculates MD5 checksums to ensure bit-perfect backups.
* **Profile Management:** Save multiple source/destination pairs for quick access.
* **Professional UI:** Dark theme with real-time progress bars and activity logging.

## 🛠️ Architecture

The project follows a modular structure separating concerns:
* `src/core`: Business logic (Threading, File I/O, Hashing).
* `src/ui`: Interface logic and Stylesheets.
* `src/utils`: Helper functions.

## 📦 Installation

You can just run portable .exe file inside dist or > 

1.  Clone the repository:
    ```bash
    git clone [https://github.com/yourusername/pybackup.git](https://github.com/yourusername/pybackup.git)
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the application:
    ```bash
    python main.py
    ```

## 🖥️ Usage

1.  Click **Add New Task** to select a source folder and a destination folder.
2.  Select a verification mode (None, Size, or Deep).
3.  Click **Run Backup**.
4.  Monitor progress in the real-time log.
