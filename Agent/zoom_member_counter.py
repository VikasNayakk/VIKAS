from __future__ import annotations

import csv
import re
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext

import cv2
import numpy as np
import pyautogui
import pytesseract


@dataclass
class MonitorRegion:
    x: int
    y: int
    w: int
    h: int


class ZoomMemberCounter:
    def __init__(self, on_status=None) -> None:
        self.on_status = on_status
        self.region: MonitorRegion | None = None
        self.interval_seconds = 300
        self.output_file = Path(__file__).resolve().parent.parent / "Aliens-Meeting" / "Main" / "Table" / f"MemberCount-{datetime.now().strftime('%m-%d-%Y')}.csv"

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def _emit(self, message: str) -> None:
        print(message)
        if self.on_status:
            self.on_status(message)

    @staticmethod
    def _preprocess(image_bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        # Otsu threshold helps with mixed backgrounds in Zoom UI
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def _extract_count(text: str) -> int | None:
        lowered = text.lower()

        patterns = [
            r"participants?\s*[:\-]?\s*(\d{1,4})",
            r"members?\s*[:\-]?\s*(\d{1,4})",
            r"attendees?\s*[:\-]?\s*(\d{1,4})",
            r"\((\d{1,4})\)",
        ]
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                return int(match.group(1))

        # Fallback: choose the largest number from OCR text.
        numbers = [int(n) for n in re.findall(r"\b\d{1,4}\b", lowered)]
        if numbers:
            return max(numbers)
        return None

    def set_region(self, region: MonitorRegion | None) -> None:
        self.region = region
        if region is None:
            self._emit("INFO: Count region cleared.")
        else:
            self._emit(f"INFO: Count region set to x={region.x}, y={region.y}, w={region.w}, h={region.h}")

    def set_interval_minutes(self, minutes: float) -> None:
        self.interval_seconds = max(5, int(minutes * 60))

    def set_output_file(self, output_path: str) -> None:
        self.output_file = Path(output_path)

    def open_meeting_link(self, url: str) -> None:
        self._emit("ACTION: Opening Zoom meeting link in default browser.")
        webbrowser.open(url)

    def select_count_region(self) -> None:
        self._emit("ACTION: Select area where participant count appears, then press Enter.")
        screenshot = pyautogui.screenshot()
        frame_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        roi = cv2.selectROI("Select Participant Count Area", frame_bgr, showCrosshair=True, fromCenter=False)
        cv2.destroyWindow("Select Participant Count Area")

        x, y, w, h = (int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3]))
        if w <= 0 or h <= 0:
            self._emit("INFO: Region selection canceled.")
            return

        self.set_region(MonitorRegion(x=x, y=y, w=w, h=h))

    def _capture_text_and_count(self) -> tuple[str, int | None]:
        if self.region is None:
            return "", None

        shot = pyautogui.screenshot(region=(self.region.x, self.region.y, self.region.w, self.region.h))
        frame_bgr = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        processed = self._preprocess(frame_bgr)

        config = "--psm 6"
        text = pytesseract.image_to_string(processed, config=config)
        count = self._extract_count(text)
        return text.strip(), count

    def _ensure_csv_header(self) -> None:
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        if self.output_file.exists():
            return
        with self.output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "member_count", "raw_ocr_text"])

    def _append_csv(self, timestamp: str, count: int | None, raw_text: str) -> None:
        with self.output_file.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, "" if count is None else count, raw_text.replace("\n", " | ")])

    def start(self) -> None:
        if self.region is None:
            self._emit("ERROR: Please select participant count area first.")
            return
        if self._thread is not None and self._thread.is_alive():
            self._emit("INFO: Monitoring already running.")
            return

        self._ensure_csv_header()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._emit(f"INFO: Monitoring started. Interval: {self.interval_seconds // 60} minute(s).")
        self._emit(f"INFO: Saving logs to: {self.output_file}")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)
        self._emit("INFO: Monitoring stopped.")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            raw_text, count = self._capture_text_and_count()
            self._append_csv(timestamp, count, raw_text)

            if count is None:
                self._emit(f"{timestamp} | Count not detected. OCR='{raw_text}'")
            else:
                self._emit(f"{timestamp} | Member count: {count}")

            slept = 0
            while slept < self.interval_seconds and not self._stop_event.is_set():
                time.sleep(1)
                slept += 1


class ZoomCounterUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Zoom Member Counter (Every 5 Minutes)")
        self.root.geometry("860x540")

        self.counter = ZoomMemberCounter(on_status=self._append_log_threadsafe)

        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=12, pady=(12, 6))

        tk.Label(top, text="Zoom Join Link:").grid(row=0, column=0, sticky="w")
        self.url_var = tk.StringVar(value="https://us02web.zoom.us/wc/83477481447/join?pwd=941533")
        tk.Entry(top, textvariable=self.url_var, width=95).grid(row=0, column=1, sticky="we", padx=8)
        tk.Button(top, text="Open Join Link", width=16, command=self.open_join_link).grid(row=0, column=2)

        tk.Label(top, text="Interval (minutes):").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.interval_var = tk.StringVar(value="5")
        tk.Entry(top, textvariable=self.interval_var, width=8).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        tk.Label(top, text="CSV Output:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.output_var = tk.StringVar(value=str(self.counter.output_file))
        tk.Entry(top, textvariable=self.output_var, width=95).grid(row=2, column=1, sticky="we", padx=8, pady=(8, 0))
        tk.Button(top, text="Browse", width=16, command=self.pick_output_file).grid(row=2, column=2, pady=(8, 0))

        top.grid_columnconfigure(1, weight=1)

        controls = tk.Frame(self.root)
        controls.pack(fill=tk.X, padx=12, pady=8)

        tk.Button(controls, text="1) Select Count Area", width=20, command=self.select_count_area).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(controls, text="2) Start Counting", width=20, command=self.start_counting).pack(side=tk.LEFT, padx=8)
        tk.Button(controls, text="Stop", width=16, command=self.stop_counting).pack(side=tk.LEFT, padx=8)

        self.log = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._append_log("Steps: Open Join Link -> Join meeting -> Open Participants panel -> Select Count Area -> Start Counting")

    def _append_log_threadsafe(self, message: str) -> None:
        self.root.after(0, lambda: self._append_log(message))

    def _append_log(self, message: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def open_join_link(self) -> None:
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a Zoom link.")
            return
        self.counter.open_meeting_link(url)

    def pick_output_file(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="Choose CSV output file",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"MemberCount-{datetime.now().strftime('%m-%d-%Y')}.csv",
        )
        if selected:
            self.output_var.set(selected)

    def select_count_area(self) -> None:
        self.counter.select_count_region()

    def start_counting(self) -> None:
        try:
            interval_minutes = float(self.interval_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Interval must be a number.")
            return

        self.counter.set_interval_minutes(interval_minutes)
        self.counter.set_output_file(self.output_var.get().strip())
        self.counter.start()

    def stop_counting(self) -> None:
        self.counter.stop()

    def on_close(self) -> None:
        self.counter.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = ZoomCounterUI()
    app.run()
