import os
import sys
import time
import tkinter as tk
import vlc
from tkinter import filedialog
from datetime import timedelta

class Event:
    def __init__(self, time, points, team_name):
        self.time = time
        self.points = points
        self.team_name = team_name

    def __str__(self):
        return f"{self.time}: {self.points} pts for {self.team_name}"

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return self.time == other.time and self.points == other.points and self.team_name == other.team_name
class EventData:
    def __init__(self):
        self.events = []

    def add_event(self, time, points, team_name):
        self.events.append(Event(time, points, team_name))
        self.events = sorted(self.events, key=lambda event: event.time)
    
    def save(self, stream):
        cvs_format = lambda event: f"{event.points};{event.team_name};{event.time}"
        "\n".join([cvs_format(event) for event in self.events])
        
        stream.write("\n".join([cvs_format(event) for event in self.events]))
    

def build_time_str(milliseconds):
    td = timedelta(milliseconds=max(0, milliseconds))
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)
    
class MediaPlayerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Media Player")
        self.geometry("800x800")
        self.configure(bg="#f0f0f0")
        self.initialize_player()
        self.model=EventData()
        
    def initialize_player(self):
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.current_file = None
        self.playing_video = False
        self.video_paused = False
        self.rate=1
        self.create_widgets()

    def create_widgets(self):
        self.media_canvas = tk.Canvas(self, bg="black", width=800, height=400)
        self.media_canvas.pack(pady=0, fill=tk.BOTH, expand=True)
        
        self.progress_bar = VideoProgressBar(
            self, self.set_video_position, bg="#e0e0e0", highlightthickness=0
        )
        self.progress_bar.pack(fill=tk.X, padx=10, pady=0)
        
        # Add a scroll bar to scroll through the listbox
        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)       
        # Create a listbox to display the points
        self.points_listbox = tk.Listbox(self, height=10, width=30)
        self.points_listbox.pack(side=tk.RIGHT, pady=5, fill=tk.BOTH)
        self.points_listbox.config(yscrollcommand = self.scrollbar.set) 
        self.scrollbar.config(command = self.points_listbox.yview)
        
        
        self.select_file_frame = tk.Frame(self, bg="#f0f0f0")
        self.select_file_frame.pack(pady=5, fill=tk.BOTH)
        
        
        self.rate_label = tk.Label(self.select_file_frame, text=f"x{self.rate}", fg="#555555", bg="#f0f0f0",)
        self.rate_label.place(x=0, y=0)
        
        
        self.files_frame = tk.Frame(self.select_file_frame, bg="#f0f0f0")
        self.files_frame.pack(pady=5)
        self.select_file_button = tk.Button(
            self.files_frame,
            text="Select File",
            font=("Arial", 12, "bold"),
            command=self.select_file,
        )
        self.select_file_button.pack(side=tk.LEFT, pady=5, padx=5)
        
        self.save_file_button = tk.Button(
            self.files_frame,
            text="Save",
            font=("Arial", 12, "bold"),
            command=self.save_file,
        )
        self.save_file_button.pack(side=tk.LEFT, pady=5, padx=5)
        
        self.time_label = tk.Label(
            self,
            text=self.build_time_label(),
            font=("Arial", 12, "bold"),
            fg="#555555",
            bg="#f0f0f0",
        )
        self.time_label.pack(pady=5)
        self.control_buttons_frame = tk.Frame(self, bg="#f0f0f0")
        self.control_buttons_frame.pack(pady=5)
        self.play_button = tk.Button(
            self.control_buttons_frame,
            text="Play",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.play_video,
        )
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.pause_button = tk.Button(
            self.control_buttons_frame,
            text="Pause",
            font=("Arial", 12, "bold"),
            bg="#FF9800",
            fg="white",
            command=self.pause_video,
        )
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.stop_button = tk.Button(
            self.control_buttons_frame,
            text="Stop",
            font=("Arial", 12, "bold"),
            bg="#F44336",
            fg="white",
            command=self.stop,
        )
        self.stop_button.pack(side=tk.LEFT, pady=5)
        self.fast_forward_button = tk.Button(
            self.control_buttons_frame,
            text="Fast Forward",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            command=self.fast_forward,
        )
        self.fast_forward_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.rewind_button = tk.Button(
            self.control_buttons_frame,
            text="Rewind",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            command=self.rewind,
        )
        self.rewind_button.pack(side=tk.LEFT, pady=5)
        
        # Event buttons
        self.event_buttons_frame = tk.Frame(self, bg="#f0f0f0")
        self.event_buttons_frame.pack(pady=5)
        
        def point_button(team, points, shortcut):
            command = lambda: self.point(points, team[0])
            button = tk.Button(
                self.event_buttons_frame,
                text=f"{points} pts ({shortcut.replace('<','').replace('>','')})",
                font=("Arial", 12, "bold"),
                bg=team[1],
                fg="white",
                command=command,
            )
            button.pack(side=tk.LEFT, pady=5, padx=2)
            
            self.bind(shortcut, lambda event: command())
            return button
        
        A=("A", "#2196F3")
        B=("B", "#F44336")
        shortcuts = ["<q>", "<s>", "<d>", "<w>", "<x>", "<c>"]
        iterator = iter(shortcuts)
        self.point1a_button = point_button(A, 1, next(iterator))
        self.point2a_button = point_button(A, 2, next(iterator))
        self.point3a_button = point_button(A, 3, next(iterator))
        self.point1b_button = point_button(B, 1, next(iterator))
        self.point2b_button = point_button(B, 2, next(iterator))
        self.point3b_button = point_button(B, 3, next(iterator))
        
            
        def read_backwards():
            # How stop this loop ?
            self.relative_move(-100)
            self.after(200, read_backwards)
        
        def pause_and_read_backwards():
            self.pause_video()
            read_backwards()
            
        self.bind("<space>", lambda e: self.pause_video())
        #self.bind("<Left>", lambda e: self.relative_move(-100))
        #self.bind("<Right>", lambda e: self.relative_move(100))
        self.bind("<Control-Left>", lambda e: self.relative_move(-10000))
        self.bind("<Control-Right>", lambda e: self.relative_move(10000))
        #self.bind("<Shift-Left>", lambda e: pause_and_read_backwards())
        self.bind("<Shift-Right>", lambda e: self._pause_video(True))
        
        # TODO this line change the value for the os !!!!
        os.system('xset r off')
        self.auto_repeat_rewind_flag = False
        def auto_repeat_step_by_step(value):
            if self.auto_repeat_rewind_flag:
                self.relative_move(value)
                self.after(200, lambda: auto_repeat_step_by_step(value))
                
        def rewind_pressed(event):
            step_by_step_pressed(-50)
        
        def forward_pressed(event):
            step_by_step_pressed(50)
            
        def step_by_step_pressed(value):
            if not self.video_paused:
                self.pause_video()
            self.auto_repeat_rewind_flag = True
            auto_repeat_step_by_step(value)
            
        def key_released(event):
            self.auto_repeat_rewind_flag = False
            
        self.bind("<KeyPress-Left>", rewind_pressed)
        self.bind("<KeyPress-Right>", forward_pressed)
        self.bind("<KeyRelease>", key_released)
            
        def delete_event(event):
            selection = event.widget.curselection()
            
            if selection:
                index = selection[0]
                self.model.events.pop(index)
                self.refresh_events()
            
        # https://tcl.tk/man/tcl8.6/TkCmd/keysyms.htm
        self.bind("<KP_1>", lambda e: self.set_rate(1))
        self.bind("<KP_2>", lambda e: self.set_rate(2))
        self.bind("<KP_3>", lambda e: self.set_rate(4))
        self.bind("1", lambda e: self.set_rate(1))
        self.bind("2", lambda e: self.set_rate(2))
        self.bind("3", lambda e: self.set_rate(4))
        self.bind("<Delete>", delete_event)


        def callback_select_event(event):
            selection = event.widget.curselection()
            
            if selection:
                index = selection[0]
                data = event.widget.get(index)
                print(f"{index}: {data}")
                
                # Set video position to this event
                time_position = self.model.events[index].time
                self.media_player.set_time(time_position)
            else:
                print(f"deselect")
                #label.configure(text="")

        self.points_listbox.bind("<<ListboxSelect>>", callback_select_event)
        
    def set_rate(self, rate):
        print(f"Setting rate to {rate}")
        self.rate=rate
        self.rate_label.config(text=f"x{self.rate}")
        self.media_player.set_rate(self.rate)
    
    def point(self, points, team_name):
        if self.playing_video:
            current_time = self.media_player.get_time()
            current_time_str = str(timedelta(milliseconds=current_time))[:-3]
            
            print(f"{points} point for team {team_name}: {current_time_str}")  
            
            print(f"point time: {current_time}")
            self.model.add_event(current_time, points, team_name)
            self.refresh_events()
        
    def refresh_events(self):
        self.points_listbox.delete(0, tk.END)
        for event in self.model.events:
            time_str = build_time_str(event.time)
            self.points_listbox.insert(tk.END, f"{time_str}: Team {event.team_name}: {event.points} pts")
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Media Files", "*.mp4 *.avi")]
        )
        self.launch_video(file_path)
        
    def save_file(self):
        if self.current_file:
            base = os.path.basename(self.current_file)
            filename, _ = os.path.splitext(base)
            csv_filename = f"{filename}.csv"
        else:
            csv_filename = "output.csv"
   
        file_path = filedialog.asksaveasfilename(
            initialfile=csv_filename,
            filetypes=[("CSV", "*.csv")]
        )
        with open(file_path, "w") as file:
            self.model.save(file)
        
    def build_time_label(self):
        total_duration = max(self.media_player.get_length(), 0)
        current_time = max(self.media_player.get_time(), 0)
        
        # When the progress_bar is set, sometimes the set_video_position is called
        # and the video freezes for a few seconds.
        # progress_percentage = 0 if (total_duration == 0) else (current_time / total_duration) * 100
        # self.progress_bar.set(progress_percentage) 
        
        current_time_str = build_time_str(milliseconds=current_time)
        total_duration_str = build_time_str(milliseconds=total_duration)
        return f"{current_time_str} / {total_duration_str}"
    
    def refresh_time(self):
        time_label=self.build_time_label()
        self.time_label.config(text=time_label)
            
    def launch_video(self, video_path):
        if video_path:
            self.current_file = video_path
            self.refresh_time()
            self.play_video()

    def play_video(self):
        if not self.playing_video:
            media = self.instance.media_new(self.current_file)
            self.media_player.set_media(media)
            #self.media_player.set_hwnd(self.media_canvas.winfo_id())
            self.media_player.set_xwindow(self.media_canvas.winfo_id())
            self.set_rate(1)
            self.media_player.play()
            self.playing_video = True
            
    def relative_move(self, duration):
        if self.playing_video:
            print(f"relative_move Current time: {self.media_player.get_time()}")
            current_time = self.media_player.get_time() + duration
            self.media_player.set_time(current_time)

    def fast_forward(self):
        self.relative_move(10000)

    def rewind(self):
        self.relative_move(-10000)

    def pause_video(self):
        self._pause_video(self.video_paused)
                
    def _pause_video(self, video_paused):
        
        print(f"_pause_video Current time: {self.media_player.get_time()}")
        if self.playing_video:
            if video_paused:
                self.media_player.play()
                self.video_paused = False
                self.pause_button.config(text="Pause")
            else:
                self.media_player.pause()
                self.video_paused = True
                self.pause_button.config(text="Resume")

    def stop(self):
        if self.playing_video:
            self.media_player.stop()
            self.playing_video = False
        self.refresh_time()

    def set_video_position(self, value):
        # Set video position only when video is paused.
        # Otherwise a "get_buffer() failed" occurs when the scrollbar is set
        # and the video freezzes a few seconds.
        if self.playing_video:
            total_duration = self.media_player.get_length()
            position = int((float(value) / 100) * total_duration)
            print(f"Setting position to {position}")
            
            self.media_player.set_time(position)

    def update_video_progress(self):
        if self.playing_video:
            self.refresh_time()
        self.after(1000, self.update_video_progress)


class VideoProgressBar(tk.Scale):
    def __init__(self, master, command, **kwargs):
        kwargs["showvalue"] = False
        super().__init__(
            master,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=800,
            command=command,
            **kwargs,
        )
        self.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.cget("state") == tk.NORMAL:
            value = (event.x / self.winfo_width()) * 100
            self.set(value)


if __name__ == "__main__":
    
    # Get first parameter from command line
    
    video_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    app = MediaPlayerApp()
    app.update_video_progress()
    app.launch_video(video_path)
    app.mainloop()