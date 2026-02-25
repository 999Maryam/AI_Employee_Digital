import time
import shutil
from pathlib import Path
from datetime import datetime
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

VAULT_PATH = Path.cwd()
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"


class DropHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        src_path = Path(event.src_path)
        original_name = src_path.name
        dest_name = f"FILE_{original_name}.md"
        dest_path = NEEDS_ACTION_PATH / dest_name
        meta_name = f"FILE_{original_name}_meta.md"
        meta_path = NEEDS_ACTION_PATH / meta_name

        try:
            # Wait briefly for the file to finish writing
            time.sleep(0.5)

            # Copy file to Needs_Action with FILE_ prefix
            NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_path), str(dest_path))

            # Create metadata file
            created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            suffix = src_path.suffix.lower()
            file_type = suffix.lstrip(".") if suffix else "unknown"

            meta_content = (
                f"---\n"
                f"type: file_drop\n"
                f"original_name: {original_name}\n"
                f"created: {created_time}\n"
                f"file_type: {file_type}\n"
                f"---\n\n"
                f"# File Drop: {original_name}\n\n"
                f"## Info\n"
                f"- **Original name:** {original_name}\n"
                f"- **Detected type:** {file_type}\n"
                f"- **Dropped at:** {created_time}\n\n"
                f"## Suggested Actions\n"
                f"- [ ] Review file contents\n"
                f"- [ ] Categorize and tag\n"
                f"- [ ] Create a plan if action is needed\n"
                f"- [ ] Move to Done when complete\n"
            )
            meta_path.write_text(meta_content, encoding="utf-8")

            print(f"New file processed: {original_name} → {dest_name}")

        except Exception as e:
            print(f"Error processing {original_name}: {e}")


def main():
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)

    handler = DropHandler()
    observer = PollingObserver(timeout=3)
    observer.schedule(handler, str(INBOX_PATH), recursive=False)
    observer.start()

    print(f"Watching Inbox → Needs_Action (polling every 3s)")
    print(f"Vault: {VAULT_PATH}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()

    observer.join()
    print("Watcher stopped.")


if __name__ == "__main__":
    main()
