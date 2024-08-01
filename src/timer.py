import tkinter as tk
from tkinter import messagebox
import csv
from datetime import datetime, timedelta
import subprocess


class PomodroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("Pomodoro Timer")
        self.master.geometry("300x150")
        self.master.attributes("-topmost", True)  # ウィンドウを最前面に表示

        self.time_left = 90 * 60  # 25分（秒単位）
        self.is_break = False
        self.is_running = False

        self.label = tk.Label(master, text="90:00", font=("Arial", 48))
        self.label.pack(pady=20)

        self.button = tk.Button(master, text="Start", command=self.start_timer)
        self.button.pack()
        self.duration_time = 0

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # タイマーのスタートとストップを切り替えるためのスクリプト
    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.button.config(text="Stop")
            self.update_timer()
        else:
            self.is_running = False
            self.button.config(text="Start")

    def update_timer(self):
        if self.is_running:
            self.time_left -= 1
            if self.is_running:
                self.duration_time += 1
            minutes, seconds = divmod(self.time_left, 60)
            time_string = f"{minutes:02d}:{seconds:02d}"
            self.label.config(text=time_string)

            if self.time_left <= 0:
                if not self.is_break:
                    self.record_session()
                    messagebox.showinfo(
                        "Pomodoro", "作業セッション終了！休憩を取りましょう。"
                    )
                    self.time_left = 10 * 60  # 10分休憩
                    self.is_break = True
                    self.duration_time = 0  # duration_timeを0に変える
                else:
                    messagebox.showinfo("Pomodoro", "休憩終了！作業を再開しましょう。")
                    self.time_left = 90 * 60  # 90分作業
                    self.is_break = False

            self.master.after(1000, self.update_timer)

    def record_session(self):
        end_time = datetime.now()
        td = timedelta(seconds=self.duration_time)
        with open("pomodoro_sessions.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    end_time.strftime("%Y-%m-%d"),
                    str(td),
                ]
            )

    def on_closing(self):
        if messagebox.askyesno("保存", "現在の作業時間を保存しますか？"):
            self.record_session()
        self.master.destroy()


root = tk.Tk()
app = PomodroTimer(root)
# 静止画面の生成のために必要
root.mainloop()
