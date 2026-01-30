import customtkinter as ctk
from tkinter import messagebox, ttk
import csv
from datetime import datetime, timedelta
import calendar
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

ctk.set_appearance_mode("System")  # モードをシステム設定に合わせる
ctk.set_default_color_theme("blue")  # テーマカラーを設定


class PomodroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("KeepTimer")
        self.master.geometry("280x210")
        self.master.attributes("-topmost", True)

        self.working_min = 90
        self.rest_min = 10

        self.time_left = self.working_min * 60
        self.is_break = False
        self.is_running = False
        self.duration_time = 0

        self.label = ctk.CTkLabel(master, text="90:00", font=("Arial", 48))
        self.label.pack(pady=20)

        self.button = ctk.CTkButton(master, text="Start", command=self.start_timer)
        self.button.pack(pady=0)

        self.stats_button = ctk.CTkButton(
            master, text="Analysis", command=self.show_stats
        )
        self.stats_button.pack(pady=10)

        self.config_button = ctk.CTkButton(
            master, text="Config", command=self.set_config
        )
        self.config_button.pack(pady=0)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.child_windows = []

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.button.configure(text="Stop")
            self.update_timer()
        else:
            self.is_running = False
            self.button.configure(text="Start")

    def update_timer(self):
        if self.is_running:
            self.time_left -= 1
            if not self.is_break:
                self.duration_time += 1
            minutes, seconds = divmod(self.time_left, 60)
            time_string = f"{minutes:02d}:{seconds:02d}"
            self.label.configure(text=time_string)

            if self.time_left <= 0:
                if not self.is_break:
                    self.record_session()
                    messagebox.showinfo(
                        "Pomodoro", "作業セッション終了！休憩を取りましょう。"
                    )
                    self.time_left = self.rest_min * 60
                    self.is_break = True
                    self.duration_time = 0
                else:
                    messagebox.showinfo("Pomodoro", "休憩終了！作業を再開しましょう。")
                    self.time_left = self.working_min * 60
                    self.is_break = False

            self.master.after(1000, self.update_timer)

    def set_new_timer(self, working_min, rest_min):
        try:
            working_min = int(working_min)
            rest_min = int(rest_min)
        except ValueError:
            messagebox.showerror("エラー", "数値を入力してください")
            return

        if working_min <= 0 or rest_min <= 0:
            messagebox.showerror("エラー", "正の整数を入力してください")
            return

        if self.is_running:
            self.is_running = False
            self.button.configure(text="Start")

        if self.duration_time != 0:
            if messagebox.askyesno("保存", "現在の作業時間を保存しますか？"):
                self.record_session()

        self.working_min = working_min
        self.rest_min = rest_min
        self.time_left = self.working_min * 60
        self.is_break = False
        self.duration_time = 0

        minutes, seconds = divmod(self.time_left, 60)
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.label.configure(text=time_string)

        messagebox.showinfo(
            "設定完了", f"作業時間: {working_min}分\n休憩時間: {rest_min}分"
        )

    def record_session(self):
        end_time = datetime.now()
        td = timedelta(seconds=self.duration_time)
        with open("pomodoro_sessions.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([end_time.strftime("%Y-%m-%d"), str(td)])

    def on_closing(self):
        for child in self.child_windows:
            child.after_cancel("check_dpi_scaling")  # すべてのafter呼び出しをキャンセル
            child.destroy()
        self.master.after_cancel("update")
        if self.is_running:
            self.is_running = False
            self.button.configure(text="Start")
        if self.duration_time != 0:
            if messagebox.askyesno("保存", "現在の作業時間を保存しますか？"):
                self.record_session()
        self.master.quit()
        self.master.destroy()
        self.master.quit()

    def set_config(self):
        config_window = ctk.CTkToplevel(self.master)
        config_window.title("Config")
        config_window.geometry("240x220")

        label_work = ctk.CTkLabel(
            config_window, text="Working time (min)", font=("Arial", 14)
        )
        label_work.pack(pady=10)
        entry_working_min = ctk.CTkEntry(config_window)
        entry_working_min.insert(0, str(self.working_min))
        entry_working_min.pack()

        label_rest = ctk.CTkLabel(
            config_window, text="Rest time (min)", font=("Arial", 14)
        )
        label_rest.pack(pady=10)
        entry_rest_min = ctk.CTkEntry(config_window)
        entry_rest_min.insert(0, str(self.rest_min))
        entry_rest_min.pack()

        button = ctk.CTkButton(
            config_window,
            text="Set",
            command=lambda: self.set_new_timer(
                entry_working_min.get(), entry_rest_min.get()
            ),
        )
        button.pack(pady=20)
        self.child_windows.append(config_window)

    def show_stats(self):
        stats_window = ctk.CTkToplevel(self.master)
        stats_window.title("Analysis")
        stats_window.geometry("800x770")

        # TreeviewをCustomTkinterのスタイルに合わせて調整
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="mintcream",
            fieldbackground="mintcream",
            foreground="black",
        )

        tree = ttk.Treeview(
            stats_window,
            columns=("Year", "Month", "Total Time"),
            show="headings",
        )
        tree.heading("Year", text="Year")
        tree.heading("Month", text="Month")
        tree.heading("Total Time", text="total time")
        tree.pack(pady=10, padx=10, fill=ctk.BOTH, expand=True)

        monthly_stats = self.calculate_monthly_stats()
        self.child_windows.append(stats_window)

        for (year, month), total_time in monthly_stats.items():
            tree.insert(
                "", "end", values=(year, calendar.month_abbr[month], str(total_time))
            )

        daily_stats = self.calculate_daily_stats()

        # グラフの作製と表示
        plt.rcParams["font.family"] = "Arial"
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("mintcream")  # figure全体の背景色を設定
        ax.set_facecolor("mintcream")
        dates = list(daily_stats.keys())
        # 辞書オブジェクトの値側をtotaltimeとして取得
        hours = [
            total_time.total_seconds() / 3600 for total_time, _ in daily_stats.values()
        ]
        weekdays = [weekday for _, weekday in daily_stats.values()]
        color_map = {
            "Monday": "slateblue",
            "Tuesday": "tomato",
            "Wednesday": "cyan",
            "Thursday": "palegreen",
            "Friday": "goldenrod",
            "Saturday": "rosybrown",
            "Sunday": "gold",
        }
        bar_colors = [color_map[weekday] for weekday in weekdays]
        ax.bar(dates, hours, color=bar_colors)
        ax.set_xlabel("Date")
        ax.set_ylabel("Hours")
        ax.set_title("Working Time (Last 30 Days)")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.grid()

        # 凡例
        handles = [
            plt.Rectangle((0, 0), 1, 1, color=color) for color in color_map.values()
        ]
        labels = list(color_map.keys())
        plt.legend(
            handles,
            labels,
            title="Weekdays",
            loc="upper left",
            bbox_to_anchor=(0, 1),
            fontsize=8,
        )

        canvas = FigureCanvasTkAgg(fig, stats_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=ctk.BOTH, expand=True)
        plt.close(fig)  # メモリリークを防ぐためにfigureを閉じる

    def calculate_monthly_stats(self):
        monthly_stats = defaultdict(timedelta)

        try:
            with open("pomodoro_sessions.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    date = datetime.strptime(row[0], "%Y-%m-%d")
                    duration = datetime.strptime(row[1], "%H:%M:%S")
                    time_delta = timedelta(
                        hours=duration.hour,
                        minutes=duration.minute,
                        seconds=duration.second,
                    )
                    monthly_stats[(date.year, date.month)] += time_delta
        except FileNotFoundError:
            messagebox.showwarning("警告", "CSVファイルが見つかりません。")
        except Exception as e:
            messagebox.showerror(
                "エラー", f"データの読み込み中にエラーが発生しました: {str(e)}"
            )

        return dict(sorted(monthly_stats.items(), reverse=True))

    def calculate_daily_stats(self):
        daily_stats = defaultdict(timedelta)
        today = datetime.now().date()
        thirty_days_ago = today - timedelta(days=29)

        try:
            df = pd.read_csv("pomodoro_sessions.csv", names=["date", "duration"])
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df["duration"] = pd.to_timedelta(df["duration"])

            # 直近30日のデータをフィルタリング
            df_filtered = df[(df["date"] >= thirty_days_ago) & (df["date"] <= today)]

            # 日ごとの合計時間を計算(辞書型で保存される)
            daily_stats = df_filtered.groupby("date")["duration"].sum().to_dict()

            # 30日分のデータを確保（データがない日は0で埋める）
            all_dates = [thirty_days_ago + timedelta(days=i) for i in range(30)]
            daily_stats = {
                date: daily_stats.get(date, timedelta(0)) for date in all_dates
            }
            # 曜日の情報を付加する
            daily_stats_with_weekday = {
                date: (total_time, date.strftime("%A"))
                for date, total_time in daily_stats.items()
            }
        except FileNotFoundError:
            messagebox.showwarning("警告", "CSVファイルが見つかりません。")
        except Exception as e:
            messagebox.showerror(
                "エラー", f"データの読み込み中にエラーが発生しました: {str(e)}"
            )
        return daily_stats_with_weekday


root = ctk.CTk()
app = PomodroTimer(root)
root.mainloop()
