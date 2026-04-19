#!/usr/bin/env python3
"""
Smart System Automation & Monitoring Suite - Python Application

This application implements:
- Directory status modeling
- Menu-driven interaction
- File automation (organize, rename, remove, copy, move)
- Logging and operation tracking
- Analytical report generation
- Robust error handling
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"
OPERATIONS_FILE = DATA_DIR / "operations_history.json"
DIRECTORY_CONFIG_FILE = DATA_DIR / "directories.json"
APP_LOG_FILE = LOG_DIR / "automation.log"


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class DirectoryInfo:
    path: str
    file_count: int
    last_accessed: str
    last_updated: str
    status: str


class OperationTracker:
    def __init__(self, history_file: Path) -> None:
        self.history_file = history_file
        self.history: List[Dict[str, str]] = self._load()

    def _load(self) -> List[Dict[str, str]]:
        if not self.history_file.exists():
            return []
        try:
            data = json.loads(self.history_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
        return []

    def _save(self) -> None:
        self.history_file.write_text(json.dumps(self.history, indent=2), encoding="utf-8")

    def record(
        self,
        action: str,
        directory: str = "",
        status: str = "SUCCESS",
        message: str = "",
        error_type: str = "",
    ) -> None:
        event = {
            "timestamp": now_str(),
            "action": action,
            "directory": directory,
            "status": status,
            "message": message,
            "error_type": error_type,
        }
        self.history.append(event)
        self._save()

    def analytics(self) -> Dict[str, object]:
        total = len(self.history)
        success = sum(1 for entry in self.history if entry.get("status") == "SUCCESS")
        failure = sum(1 for entry in self.history if entry.get("status") == "ERROR")

        directories = [entry["directory"] for entry in self.history if entry.get("directory")]
        most_frequent_directories = Counter(directories).most_common(5)

        trend_counter: Dict[str, int] = defaultdict(int)
        for entry in self.history:
            day = entry.get("timestamp", "")[:10]
            if day:
                trend_counter[day] += 1

        error_stats = Counter(
            entry.get("error_type", "Unknown")
            for entry in self.history
            if entry.get("status") == "ERROR"
        )

        return {
            "total_operations": total,
            "successful_operations": success,
            "failed_operations": failure,
            "most_frequent_directories": most_frequent_directories,
            "usage_trends": dict(sorted(trend_counter.items())),
            "error_statistics": dict(error_stats),
        }

    def write_report(self, report_path: Path) -> None:
        data = self.analytics()
        lines = [
            "SMART SYSTEM AUTOMATION SUITE - PYTHON ANALYTICS REPORT",
            f"Generated at: {now_str()}",
            "",
            "1) Total operations performed",
            str(data["total_operations"]),
            "",
            "2) Successful and failed operations",
            f"Successful: {data['successful_operations']}",
            f"Failed: {data['failed_operations']}",
            "",
            "3) Most frequently accessed directories",
        ]

        directories = data["most_frequent_directories"]
        if directories:
            for index, (directory, count) in enumerate(directories, start=1):
                lines.append(f"{index}. {directory} -> {count} operations")
        else:
            lines.append("No directory operations recorded yet.")

        lines.extend(["", "4) System usage trends (by day)"])
        usage_trends: Dict[str, int] = data["usage_trends"]  # type: ignore[assignment]
        if usage_trends:
            for day, count in usage_trends.items():
                lines.append(f"{day}: {count} operations")
        else:
            lines.append("No trend data available yet.")

        lines.extend(["", "5) Error statistics"])
        error_statistics: Dict[str, int] = data["error_statistics"]  # type: ignore[assignment]
        if error_statistics:
            for error_name, count in error_statistics.items():
                lines.append(f"{error_name}: {count}")
        else:
            lines.append("No errors recorded.")

        report_path.write_text("\n".join(lines), encoding="utf-8")


class DirectoryRegistry:
    def __init__(self, config_file: Path) -> None:
        self.config_file = config_file
        self.tracked_paths = self._load_tracked_paths()

    def _default_paths(self) -> List[str]:
        return [
            "~/Documents",
            "~/Downloads",
            str(BASE_DIR),
        ]

    def _load_tracked_paths(self) -> List[str]:
        if not self.config_file.exists():
            defaults = self._default_paths()
            self._save_tracked_paths(defaults)
            return defaults

        try:
            payload = json.loads(self.config_file.read_text(encoding="utf-8"))
            paths = payload.get("tracked_directories", [])
            if isinstance(paths, list) and paths:
                return [str(item) for item in paths]
        except json.JSONDecodeError:
            pass

        defaults = self._default_paths()
        self._save_tracked_paths(defaults)
        return defaults

    def _save_tracked_paths(self, paths: List[str]) -> None:
        content = {"tracked_directories": paths}
        self.config_file.write_text(json.dumps(content, indent=2), encoding="utf-8")

    def add_directory(self, path: Path) -> bool:
        normalized = str(path)
        if normalized in self.tracked_paths:
            return False
        self.tracked_paths.append(normalized)
        self._save_tracked_paths(self.tracked_paths)
        return True

    def remove_directory(self, path: Path) -> bool:
        normalized = str(path)
        if normalized not in self.tracked_paths:
            return False
        self.tracked_paths.remove(normalized)
        self._save_tracked_paths(self.tracked_paths)
        return True

    def _directory_info(self, path: Path) -> DirectoryInfo:
        if not path.exists():
            return DirectoryInfo(
                path=str(path),
                file_count=0,
                last_accessed="N/A",
                last_updated="N/A",
                status="MISSING",
            )

        if not path.is_dir():
            return DirectoryInfo(
                path=str(path),
                file_count=1,
                last_accessed=datetime.fromtimestamp(path.stat().st_atime).strftime("%Y-%m-%d %H:%M:%S"),
                last_updated=datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                status="FILE",
            )

        file_count = 0
        latest_mtime = path.stat().st_mtime
        last_access = path.stat().st_atime

        for root, _, files in os.walk(path, onerror=lambda _: None):
            file_count += len(files)
            try:
                root_mtime = Path(root).stat().st_mtime
                if root_mtime > latest_mtime:
                    latest_mtime = root_mtime
            except OSError:
                pass

            for filename in files:
                file_path = Path(root) / filename
                try:
                    file_stat = file_path.stat()
                    if file_stat.st_mtime > latest_mtime:
                        latest_mtime = file_stat.st_mtime
                except OSError:
                    continue

        return DirectoryInfo(
            path=str(path),
            file_count=file_count,
            last_accessed=datetime.fromtimestamp(last_access).strftime("%Y-%m-%d %H:%M:%S"),
            last_updated=datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            status="AVAILABLE",
        )

    def collect_status(self) -> List[DirectoryInfo]:
        statuses: List[DirectoryInfo] = []
        for raw_path in self.tracked_paths:
            resolved = Path(raw_path).expanduser().resolve()
            statuses.append(self._directory_info(resolved))
        return statuses


class FileAutomationEngine:
    @staticmethod
    def _unique_destination(destination: Path) -> Path:
        if not destination.exists():
            return destination
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        index = 1
        while True:
            candidate = parent / f"{stem}_{index}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    def organize_files(self, directory: Path) -> int:
        if not directory.exists() or not directory.is_dir():
            raise NotADirectoryError(f"Invalid directory: {directory}")

        moved_count = 0
        for item in directory.iterdir():
            if not item.is_file():
                continue
            extension = item.suffix.lower().lstrip(".") or "no_extension"
            target_dir = directory / f"{extension}_files"
            target_dir.mkdir(exist_ok=True)
            target_path = self._unique_destination(target_dir / item.name)
            shutil.move(str(item), str(target_path))
            moved_count += 1
        return moved_count

    def rename_file(self, file_path: Path, new_name: str) -> Path:
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not new_name.strip():
            raise ValueError("New file name cannot be empty.")

        destination = file_path.with_name(new_name.strip())
        if destination.exists():
            raise FileExistsError(f"Target already exists: {destination}")

        file_path.rename(destination)
        return destination

    def remove_item(self, target_path: Path) -> None:
        if not target_path.exists():
            raise FileNotFoundError(f"Path not found: {target_path}")
        if target_path.is_file():
            target_path.unlink()
        elif target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            raise ValueError(f"Unsupported path type: {target_path}")

    def copy_item(self, source: Path, destination_directory: Path) -> Path:
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        destination_directory.mkdir(parents=True, exist_ok=True)

        destination = self._unique_destination(destination_directory / source.name)
        if source.is_file():
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination)
        return destination

    def move_item(self, source: Path, destination_directory: Path) -> Path:
        if not source.exists():
            raise FileNotFoundError(f"Source not found: {source}")
        destination_directory.mkdir(parents=True, exist_ok=True)

        destination = self._unique_destination(destination_directory / source.name)
        shutil.move(str(source), str(destination))
        return destination


class SmartAutomationApp:
    def __init__(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            filename=APP_LOG_FILE,
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
        self.logger = logging.getLogger("smart_automation")
        self.tracker = OperationTracker(OPERATIONS_FILE)
        self.registry = DirectoryRegistry(DIRECTORY_CONFIG_FILE)
        self.engine = FileAutomationEngine()

    @staticmethod
    def _read_input(prompt: str) -> str:
        return input(prompt).strip()

    def _record_success(self, action: str, directory: str, message: str) -> None:
        self.logger.info("%s | SUCCESS | %s | %s", action, directory, message)
        self.tracker.record(action=action, directory=directory, status="SUCCESS", message=message)

    def _record_error(self, action: str, directory: str, exc: Exception) -> None:
        error_message = str(exc)
        error_type = type(exc).__name__
        self.logger.exception("%s | ERROR | %s | %s", action, directory, error_message)
        self.tracker.record(
            action=action,
            directory=directory,
            status="ERROR",
            message=error_message,
            error_type=error_type,
        )

    def _resolve_path(self, raw_input: str) -> Path:
        if not raw_input:
            raise ValueError("Path input cannot be empty.")
        return Path(raw_input).expanduser().resolve()

    def _execute_with_guard(self, action: str, directory: str, job: Callable[[], str]) -> None:
        try:
            result_message = job()
            self._record_success(action, directory, result_message)
            print(f"\nSUCCESS: {result_message}\n")
        except Exception as exc:  # pylint: disable=broad-except
            self._record_error(action, directory, exc)
            print(f"\nERROR: {exc}\n")

    def show_directory_status(self) -> None:
        statuses = self.registry.collect_status()
        if not statuses:
            print("\nNo directories tracked yet.\n")
            return

        print("\nTracked Directory Status\n")
        print(f"{'Path':55} {'Files':>8} {'Last Accessed':20} {'Last Updated':20} {'Status':10}")
        print("-" * 120)
        for info in statuses:
            row = asdict(info)
            print(
                f"{row['path'][:55]:55} "
                f"{row['file_count']:>8} "
                f"{row['last_accessed'][:20]:20} "
                f"{row['last_updated'][:20]:20} "
                f"{row['status']:10}"
            )
        print()

    def add_directory_to_model(self) -> None:
        raw_path = self._read_input("Enter directory path to track: ")
        path = self._resolve_path(raw_path)

        def job() -> str:
            if not path.exists() or not path.is_dir():
                raise NotADirectoryError(f"Directory does not exist: {path}")
            added = self.registry.add_directory(path)
            if not added:
                return f"Directory already tracked: {path}"
            return f"Directory added to model: {path}"

        self._execute_with_guard("ADD_DIRECTORY", str(path), job)

    def remove_directory_from_model(self) -> None:
        raw_path = self._read_input("Enter tracked directory path to remove: ")
        path = self._resolve_path(raw_path)

        def job() -> str:
            removed = self.registry.remove_directory(path)
            if not removed:
                return f"Directory was not in tracked list: {path}"
            return f"Directory removed from model: {path}"

        self._execute_with_guard("REMOVE_DIRECTORY", str(path), job)

    def organize_files(self) -> None:
        raw_path = self._read_input("Enter directory path to organize: ")
        directory = self._resolve_path(raw_path)

        def job() -> str:
            moved = self.engine.organize_files(directory)
            return f"Organized {moved} files by extension inside: {directory}"

        self._execute_with_guard("ORGANIZE_FILES", str(directory), job)

    def rename_file(self) -> None:
        raw_path = self._read_input("Enter full file path to rename: ")
        new_name = self._read_input("Enter new file name: ")
        file_path = self._resolve_path(raw_path)

        def job() -> str:
            destination = self.engine.rename_file(file_path, new_name)
            return f"Renamed file to: {destination}"

        self._execute_with_guard("RENAME_FILE", str(file_path.parent), job)

    def remove_item(self) -> None:
        raw_path = self._read_input("Enter file/directory path to remove: ")
        confirm = self._read_input("Type YES to confirm deletion: ")
        target = self._resolve_path(raw_path)

        def job() -> str:
            if confirm != "YES":
                return "Deletion cancelled by user."
            self.engine.remove_item(target)
            return f"Removed: {target}"

        self._execute_with_guard("REMOVE_ITEM", str(target.parent), job)

    def copy_item(self) -> None:
        raw_source = self._read_input("Enter source file/directory path: ")
        raw_dest = self._read_input("Enter destination directory path: ")
        source = self._resolve_path(raw_source)
        destination_dir = self._resolve_path(raw_dest)

        def job() -> str:
            destination = self.engine.copy_item(source, destination_dir)
            return f"Copied '{source}' to '{destination}'"

        self._execute_with_guard("COPY_ITEM", str(destination_dir), job)

    def move_item(self) -> None:
        raw_source = self._read_input("Enter source file/directory path: ")
        raw_dest = self._read_input("Enter destination directory path: ")
        source = self._resolve_path(raw_source)
        destination_dir = self._resolve_path(raw_dest)

        def job() -> str:
            destination = self.engine.move_item(source, destination_dir)
            return f"Moved '{source}' to '{destination}'"

        self._execute_with_guard("MOVE_ITEM", str(destination_dir), job)

    def execute_automated_bundle(self) -> None:
        raw_path = self._read_input("Enter directory path for automated bundle: ")
        directory = self._resolve_path(raw_path)

        def job() -> str:
            moved = self.engine.organize_files(directory)
            report_file = REPORT_DIR / f"bundle_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
            directory_info = self.registry._directory_info(directory)  # noqa: SLF001
            lines = [
                "AUTOMATED TASK BUNDLE REPORT",
                f"Generated at: {now_str()}",
                f"Directory: {directory}",
                f"Files organized by type: {moved}",
                f"Current file count: {directory_info.file_count}",
                f"Last updated: {directory_info.last_updated}",
                f"Status: {directory_info.status}",
            ]
            report_file.write_text("\n".join(lines), encoding="utf-8")
            return f"Automated bundle complete. Report generated: {report_file}"

        self._execute_with_guard("AUTOMATED_BUNDLE", str(directory), job)

    def generate_analytics_report(self) -> None:
        report_path = REPORT_DIR / f"analytics_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        def job() -> str:
            self.tracker.write_report(report_path)
            return f"Analytics report generated: {report_path}"

        self._execute_with_guard("GENERATE_ANALYTICS", str(REPORT_DIR), job)

    def show_analytics_summary(self) -> None:
        data = self.tracker.analytics()
        print("\nAnalytics Summary\n")
        print(f"Total operations: {data['total_operations']}")
        print(f"Successful operations: {data['successful_operations']}")
        print(f"Failed operations: {data['failed_operations']}")

        print("\nMost frequent directories:")
        directories = data["most_frequent_directories"]
        if directories:
            for idx, item in enumerate(directories, start=1):
                print(f"{idx}. {item[0]} -> {item[1]} operations")
        else:
            print("No directory usage data yet.")

        print("\nError statistics:")
        errors = data["error_statistics"]
        if errors:
            for name, count in errors.items():
                print(f"{name}: {count}")
        else:
            print("No errors recorded.")
        print()

    def menu(self) -> None:
        print("Smart System Automation Suite - Python Application")
        print("User:", os.getenv("USER") or os.getenv("USERNAME") or "unknown")

        actions = {
            "1": self.show_directory_status,
            "2": self.add_directory_to_model,
            "3": self.remove_directory_from_model,
            "4": self.organize_files,
            "5": self.rename_file,
            "6": self.remove_item,
            "7": self.copy_item,
            "8": self.move_item,
            "9": self.execute_automated_bundle,
            "10": self.generate_analytics_report,
            "11": self.show_analytics_summary,
        }

        while True:
            print("Menu:")
            print("1. View directory status")
            print("2. Add directory to model")
            print("3. Remove directory from model")
            print("4. Organize files by type")
            print("5. Rename a file")
            print("6. Remove file/folder")
            print("7. Copy file/folder")
            print("8. Move file/folder")
            print("9. Execute automated task bundle")
            print("10. Generate analytics report")
            print("11. View analytics summary")
            print("0. Exit")

            choice = self._read_input("Select an option: ")
            if choice == "0":
                print("\nExiting application.\n")
                self.tracker.record(
                    action="EXIT",
                    directory="",
                    status="SUCCESS",
                    message="Application exited normally.",
                )
                break

            action = actions.get(choice)
            if action is None:
                print("\nInvalid option. Please choose a valid menu number.\n")
                self.tracker.record(
                    action="INVALID_INPUT",
                    directory="",
                    status="ERROR",
                    message=f"Invalid menu option: {choice}",
                    error_type="InvalidInputError",
                )
                continue

            try:
                action()
            except Exception as exc:  # pylint: disable=broad-except
                # Defensive guard to keep application alive under unexpected failures.
                self._record_error("UNEXPECTED_FAILURE", "", exc)
                print(f"\nUnexpected error handled safely: {exc}\n")


def main() -> None:
    app = SmartAutomationApp()
    app.menu()


if __name__ == "__main__":
    main()
