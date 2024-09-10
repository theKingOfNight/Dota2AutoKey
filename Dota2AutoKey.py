import pyautogui
import time
import threading
import tkinter as tk
import json
import os
import random
import keyboard
import re

keys_with_intervals = {}
running = False
config_file = "keys_config.json"
special_keys = {
    'alt': 'altleft',
}
lock = threading.Lock()


def parse_key_sequence(key_sequence):
    keys = []
    parts = re.split(r'(\[.*?\])', key_sequence)
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            key_name = part[1:-1].lower()
            if key_name in special_keys:
                keys.append(special_keys[key_name])
        else:
            keys.extend(list(part))
    return keys


def press_key_sequence(keys, interval):
    while True:
        with lock:
            if not running:
                break
        special_keys_held = []
        try:
            for key in keys:
                if key in special_keys.values() and key not in special_keys_held:
                    pyautogui.keyDown(key)
                    special_keys_held.append(key)

            for key in keys:
                if key not in special_keys.values():
                    pyautogui.press(key)

            for key in special_keys_held:
                pyautogui.keyUp(key)
        except Exception as e:
            print(f"Error pressing keys {keys}: {e}")
        time.sleep(interval + random.uniform(0.1, 0.3))


def start_pressing():
    global running
    running = True
    keys_with_intervals.clear()
    for i in range(8):
        key_sequence = key_entries[i].get()
        interval = interval_entries[i].get()
        if key_sequence and interval:
            interval = float(interval)
            parsed_keys = parse_key_sequence(key_sequence)
            with lock:
                keys_with_intervals[tuple(parsed_keys)] = interval
    save_keys()
    for key_sequence, interval in keys_with_intervals.items():
        thread = threading.Thread(target=press_key_sequence, args=(key_sequence, interval))
        thread.daemon = True
        thread.start()


def stop_pressing():
    global running
    with lock:
        running = False


def save_keys():
    data = {
        "keys": [key.get() for key in key_entries],
        "intervals": [interval.get() for interval in interval_entries]
    }
    with open(config_file, "w") as f:
        json.dump(data, f)


def load_keys():
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
                for i in range(8):
                    key_entries[i].insert(0, data["keys"][i])
                    interval_entries[i].insert(0, data["intervals"][i])
        except (IOError, ValueError, KeyError) as e:
            print(f"Error loading config file: {e}")


def on_key_event(event):
    if event.name in special_keys:
        current_entry = root.focus_get()
        if isinstance(current_entry, tk.Entry):
            current_text = current_entry.get()
            if f'[{event.name.upper()}]' not in current_text:
                current_entry.insert(tk.END, f'[{event.name.upper()}]')


root = tk.Tk()
root.title("自动按键器")
root.geometry("1000x250")
root.configure(padx=20, pady=20)

key_entries = []
interval_entries = []

frame_left = tk.Frame(root)
frame_left.grid(row=0, column=0, padx=10, pady=10)
frame_right = tk.Frame(root)
frame_right.grid(row=0, column=1, padx=10, pady=10)

for i in range(4):
    key_label = tk.Label(frame_left, text=f"按键 {i + 1}:")
    key_label.grid(row=i, column=0, padx=5, pady=5, sticky="e")
    key_entry = tk.Entry(frame_left)
    key_entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
    key_entries.append(key_entry)

    interval_label = tk.Label(frame_left, text=f"间隔时间 (秒):")
    interval_label.grid(row=i, column=2, padx=5, pady=5, sticky="e")
    interval_entry = tk.Entry(frame_left)
    interval_entry.grid(row=i, column=3, padx=5, pady=5, sticky="w")
    interval_entries.append(interval_entry)

for i in range(4, 8):
    key_label = tk.Label(frame_right, text=f"按键 {i + 1}:")
    key_label.grid(row=i - 4, column=0, padx=5, pady=5, sticky="e")
    key_entry = tk.Entry(frame_right)
    key_entry.grid(row=i - 4, column=1, padx=5, pady=5, sticky="w")
    key_entries.append(key_entry)

    interval_label = tk.Label(frame_right, text=f"间隔时间 (秒):")
    interval_label.grid(row=i - 4, column=2, padx=5, pady=5, sticky="e")
    interval_entry = tk.Entry(frame_right)
    interval_entry.grid(row=i - 4, column=3, padx=5, pady=5, sticky="w")
    interval_entries.append(interval_entry)

button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=20)

start_button = tk.Button(button_frame, text="开始", command=start_pressing, width=15)
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(button_frame, text="停止", command=stop_pressing, width=15)
stop_button.grid(row=0, column=1, padx=10)

root.bind("<Button-1>", lambda event: event.widget.focus_set())

load_keys()
keyboard.hook(on_key_event)

root.mainloop()
