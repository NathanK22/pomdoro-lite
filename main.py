import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import time
import threading
from plyer import notification

class PomodoroTimer:
    def __init__(self, master):
        self.master = master
        self.master.title("Pomodoro Timer")
        self.master.geometry("300x400")

        self.style = ttk.Style()
        self.style.theme_use('solar')
        
        #Global font
        default_font = ("Garamond", 11)
        self.style.configure(".", font=default_font)
        self.style.configure("TLabel", font=default_font)
        self.style.configure("TButton", font=default_font)
        self.style.configure("TEntry", font=default_font)
        
        
        
        self.style.configure("Custom.TEntry", font=default_font)
        self.style.map("Custom.TEntry",
                       foreground=[("disabled", "#726748")]
                       #,fieldbackground=[("disabled", "gray80")]
        )

        self.timer_running = False
        self.pomodoro_count = 0

        self.create_widgets()

    def create_widgets(self):
        # Work time input
        ttk.Label(self.master, text="Work Time (minutes):").pack(pady=5)
        self.work_time = ttk.Entry(self.master, style="Custom.TEntry", validate="key")
        self.work_time["validatecommand"] = (self.work_time.register(self.validate_integer), "%P")
        self.work_time.pack(pady=5)
        self.work_time.insert(0, "50")

        # Break time input
        ttk.Label(self.master, text="Break Time (minutes):").pack(pady=5)
        self.break_time = ttk.Entry(self.master, style="Custom.TEntry", validate="key")
        self.break_time["validatecommand"] = (self.break_time.register(self.validate_integer), "%P")
        self.break_time.pack(pady=(5, 0))
        self.break_time.insert(0, "10")
        
        #Error message space
        self.error_label = ttk.Label(self.master, text="", foreground="red", font=("Garamond", 11))
        self.error_label.pack(pady=0)

        # Timer display
        self.timer_display = ttk.Label(self.master, text="00:00", font=("TkDefaultFont", 42))
        self.timer_display.pack(pady=(0, 0))
        
        # Pomodoro count display
        self.count_display = ttk.Label(self.master, text=f"Work time: 0 minutes")
        self.count_display.pack(pady=(0, 10))
        
        #toggle button
        self.toggle_button = ttk.Button(self.master, text="Start", command=self.toggle_timer, style="success.TButton")
        self.toggle_button.pack(pady=10)

        # Start button
        #self.start_button = ttk.Button(self.master, text="Start", command=self.start_timer, style='success.TButton')
        #self.start_button.pack(pady=10)

        # Stop button
        #self.stop_button = ttk.Button(self.master, text="Stop", command=self.stop_timer, style='danger.TButton')
        #self.stop_button.pack(pady=10)

    def validate_integer(self, value):
        if value == "":
            return True
        if " " in value:
            return False
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def validate_inputs(self):
        work_time = self.work_time.get().strip()
        break_time = self.break_time.get().strip()
        return work_time.isdigit() and int(work_time) > 0 and break_time.isdigit() and int(break_time) > 0
        
    def toggle_timer(self):
        self.error_label.config(text="")
        self.master.update()
        time.sleep(0.1)
        
        if not self.timer_running:
            if self.validate_inputs():
                self.start_timer()
            else:
                self.error_label.config(text="Enter valid work and break time")
        else: 
            self.stop_timer()

    def start_timer(self):

        self.timer_running = True
        self.toggle_button.config(text="Stop", style="danger.TButton")
        self.work_time.config(state='disabled')
        self.break_time.config(state='disabled')
        self.error_label.config(text="") #clear
        threading.Thread(target=self.run_timer, daemon=True).start()

    def stop_timer(self):
        self.timer_running = False
        self.toggle_button.config(text="Start", style="success.TButton")
        self.work_time.config(state='normal')
        self.break_time.config(state='normal')
        self.master.title("Pomodoro Timer")

    def run_timer(self):
        while self.timer_running:
            # Work
            self.countdown(int(self.work_time.get()) * 60, "Work")
            if not self.timer_running:
                break

            self.pomodoro_count += 1
            self.count_display.config(text=f"Work Time: {int(self.work_time.get())*self.pomodoro_count} minutes")
            
            # Work ends noti
            self.send_notification("Work session ended", "Enjoy your break!")
            
            # Break 
            self.countdown(int(self.break_time.get()) * 60, "Break")
            if not self.timer_running:
                break

            # Break ends noti
            self.send_notification("Break ended", "Enjoy your work!")
            
        self.timer_display.config(text="00:00")
        
    def send_notification(self, title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Pomodoro Timer",
            timeout=5
        )

    def countdown(self, seconds, session_type):
        while seconds > 0 and self.timer_running:
            mins, secs = divmod(seconds, 60)
            time_string = f"{mins:02d}:{secs:02d}"
            self.master.after(0, self.timer_display.config, {"text": time_string})
            self.master.title(f"{session_type}: {time_string}")
            time.sleep(1)
            seconds -= 1

if __name__ == "__main__":
    root = ttk.Window()
    app = PomodoroTimer(root)
    root.mainloop()