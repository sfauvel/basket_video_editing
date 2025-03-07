import os
import sys
import time
import tkinter as tk
import vlc
from tkinter import filedialog, Listbox
from tkinter.ttk import Combobox
from datetime import timedelta

class Event:
    def __init__(self, time, points, team_name, quarter=None):
        self.time = time
        self.points = points
        self.team_name = team_name
        self.quarter = quarter

    def __str__(self):
        return f"{self.time}: {self.points} pts for {self.team_name}"

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return self.time == other.time and self.points == other.points and self.team_name == other.team_name
class EventData:
    def __init__(self):
        self.events = []

    def add_event(self, time, points, team_name, quarter=None):
        event = Event(time, points, team_name, quarter)
        self.events.append(event)
        self.events = sorted(self.events, key=lambda event: event.time)
        return event
    
    def save(self, stream):
        cvs_format = lambda event: f"{event.points};{event.team_name};{build_time_str(event.time)};{event.quarter}"
        "\n".join([cvs_format(event) for event in self.events])
        
        stream.write("\n".join([cvs_format(event) for event in self.events]))
    

def build_time_str(milliseconds):
    td = timedelta(milliseconds=max(0, milliseconds))
    mm, ss = divmod(td.seconds, 60)
    hh, mm = divmod(mm, 60)
    return "%d:%02d:%02d" % (hh, mm, ss)
    
class ButtonType():
    def __init__(self, bg, fg):
        self.bg = bg
        self.fg = fg

BACKGROUND="#f0f0f0" 
ButtonType.STANDARD = ButtonType(None, None)
ButtonType.BLUE = ButtonType("#2196F3", BACKGROUND)
ButtonType.GREEN = ButtonType("#4CAF50", BACKGROUND)
ButtonType.ORANGE = ButtonType("#FF9800", BACKGROUND)
ButtonType.RED = ButtonType("#F44336", BACKGROUND)

class TEAM():
    def __init__(self, name, button_type):
        self.name=name
        self.button_type=button_type
    
TEAM.A=TEAM("A", ButtonType.BLUE)
TEAM.B=TEAM("B", ButtonType.RED)
TEAM.START=TEAM(">", ButtonType.STANDARD)
TEAM.END=TEAM("<", ButtonType.STANDARD)

class MediaPlayerApp(tk.Tk):
    def __init__(self, score="0-0"):
        self.score=score
        super().__init__()
        self.title("Media Player")
        self.geometry("800x800")
        self.model=EventData()
        self.configure(bg=BACKGROUND)
        self.initialize_player()
        
    def initialize_player(self):
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.current_file = None
        self.video_paused = False
        self.needs_to_start_and_end_events = False
        self.rate=1
        self.create_widgets()
        
        def length_changed(event):
            total_duration = event.u.new_length
            if len(self.model.events) == 0 or self.needs_to_start_and_end_events:
                self.needs_to_start_and_end_events = False
                self.add_start_and_end_events(total_duration)
            
        self.media_player.event_manager().event_attach(vlc.EventType.MediaPlayerLengthChanged, length_changed)
        
    def add_start_and_end_events(self, total_duration):
        quarter = self.quarter_listbox.get()
        self.model.add_event(0, int(0), "-", quarter)
        self.model.add_event(total_duration, int(0), "-", quarter)
        self.refresh_events()
        
    def create_widgets(self):

        def mk_button(master, text, command, type=ButtonType.STANDARD):
            return tk.Button(
                master,
                text=text,
                font=("Arial", 12, "bold"),
                command=command,
                bg=type.bg,
                fg=type.fg,
            )
            
        def mk_label(master, text):
            return tk.Label(master, text=text, font=("Arial", 12, "bold"), fg="#555555", bg=BACKGROUND)
            
        def mk_media_component():    
            self.media_canvas = tk.Canvas(self, bg="black", width=800, height=400)
            self.media_canvas.pack(pady=0, fill=tk.BOTH, expand=True)
            
            self.progress_bar = VideoProgressBar(
                self, None, bg="#e0e0e0", highlightthickness=0
                # self, self.set_video_position, bg="#e0e0e0", highlightthickness=0
            )
            self.progress_bar.pack(fill=tk.X, padx=10, pady=0)
            self.progress_bar.bind("<Button-1>", self.click_on_progress_bar)
        
        def mk_event_component():
            # Add a scroll bar to scroll through the listbox
            self.scrollbar = tk.Scrollbar(self)
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)       
            # Create a listbox to display the points
            self.points_listbox = tk.Listbox(self, height=10, width=35, 
                font=("Courier", 12),)
            self.points_listbox.pack(side=tk.RIGHT, pady=5, fill=tk.BOTH)
            self.points_listbox.config(yscrollcommand = self.scrollbar.set) 
            self.scrollbar.config(command = self.points_listbox.yview)
        
        def mk_files_component(master):
            self.files_frame = tk.Frame(master, bg=BACKGROUND)
            self.files_frame.pack(pady=5)
            
            self.select_file_button = mk_button(self.files_frame, "Select File", self.select_file)
            self.select_file_button.pack(side=tk.LEFT, pady=5, padx=5)
            
            self.save_file_button = mk_button(self.files_frame, "Save", self.save_file)
            self.save_file_button.pack(side=tk.LEFT, pady=5, padx=5)
            
            self.load_csv_file_button = mk_button(self.files_frame, "Load", self.select_csv)
            self.load_csv_file_button.pack(side=tk.LEFT, pady=5, padx=5)
            
            self.quarter_listbox = Combobox(self.files_frame, height=20, width=2, values=["1","2","3","4"], state="readonly", font="Verdana 16")
            self.quarter_listbox.pack(pady=5)
            self.quarter_listbox.set("1")
            self.quarter_listbox.bind("<<ComboboxSelected>>", self.select_quarter_event) 
            
        def mk_point_button(team, points, shortcut):
            command = lambda: self.point(points, team.name)
            button = mk_button(self.event_buttons_frame, f"{points} pts ({shortcut.replace('<','').replace('>','')})", command, team.button_type)
            button.pack(side=tk.LEFT, pady=5, padx=2)
            
            self.bind(shortcut, lambda event: command())
            return button
        
        # Create components
        mk_media_component()
        mk_event_component()
        
        self.select_file_frame = tk.Frame(self, bg=BACKGROUND)
        self.select_file_frame.pack(pady=5, fill=tk.BOTH)
             
        self.rate_label = mk_label(self.select_file_frame, f"x{self.rate}")
        self.rate_label.place(x=0, y=0)
        
        mk_files_component(self.select_file_frame)
        
        
        self.time_and_score = tk.Frame(self, bg=BACKGROUND)
        self.time_and_score.pack(pady=5)
        self.time_label = mk_label(self.time_and_score, self.build_time_label())
        self.time_label.pack(side=tk.LEFT, pady=5)
        
        self.score_label = mk_label(self.time_and_score, self.build_score(self.score))
        self.score_label.pack(side=tk.LEFT, pady=5, padx=20)
        
        self.control_buttons_frame = tk.Frame(self, bg=BACKGROUND)
        self.control_buttons_frame.pack(pady=5)
        
        self.play_button = mk_button(self.control_buttons_frame, "Play", self.play_video, ButtonType.GREEN)
        self.play_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pause_button = mk_button(self.control_buttons_frame, "Pause", self.pause_video, ButtonType.ORANGE)
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.stop_button = mk_button(self.control_buttons_frame, "Stop", self.stop, ButtonType.RED)
        self.stop_button.pack(side=tk.LEFT, pady=5)
        
        self.fast_forward_button = mk_button(self.control_buttons_frame, "Fast Forward", self.fast_forward, ButtonType.BLUE)
        self.fast_forward_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.rewind_button = mk_button(self.control_buttons_frame, "Rewind", self.rewind, ButtonType.BLUE)
        self.rewind_button.pack(side=tk.LEFT, pady=5)
        
        # Event buttons
        self.event_buttons_frame = tk.Frame(self, bg=BACKGROUND)
        self.event_buttons_frame.pack(pady=5)
            
        shortcuts = ["<q>", "<s>", "<d>", "<w>", "<x>", "<c>", "<m>", "<M>"]
        iterator = iter(shortcuts)
        self.point1a_button = mk_point_button(TEAM.A, 1, next(iterator))
        self.point2a_button = mk_point_button(TEAM.A, 2, next(iterator))
        self.point3a_button = mk_point_button(TEAM.A, 3, next(iterator))
        self.point1b_button = mk_point_button(TEAM.B, 1, next(iterator))
        self.point2b_button = mk_point_button(TEAM.B, 2, next(iterator))
        self.point3b_button = mk_point_button(TEAM.B, 3, next(iterator))
        self.event_button = mk_point_button(TEAM.START, 0, next(iterator))
        self.event_button = mk_point_button(TEAM.END, 0, next(iterator))

        def read_backwards():
            # How stop this loop ?
            self.relative_move(-100)
            self.after(200, read_backwards)
        
        def pause_and_read_backwards():
            self.pause_video()
            read_backwards()
            
        self.auto_repeat_rewind_flag = False
        def auto_repeat_step_by_step(value):
            self.relative_move(value)
            time.sleep(0.1)
                
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
            
        def delete_event(event):
            selection = event.widget.curselection()
            
            if selection:
                index = selection[0]
                self.model.events.pop(index)
                self.refresh_events()
                
        def select_event_index(event, next_index):
            if isinstance(event.widget, Listbox):
                selection = event.widget.curselection()
                if selection:
                    index = selection[0]
                    max_value = event.widget.size()-1
                    min_value = 0
                    self.select_event_in_list(event.widget, max(min(next_index(index), max_value),min_value))
                
                
        def select_next_event(event):
            select_event_index(event, lambda index: index+1)
        
        def select_previous_event(event):
            select_event_index(event, lambda index: index-1)
            
        self.bind("<space>", lambda e: self.pause_video())
        #self.bind("<Left>", lambda e: self.relative_move(-100))
        #self.bind("<Right>", lambda e: self.relative_move(100))
        self.bind("<Control-Left>", lambda e: self.relative_move(-10000))
        self.bind("<Control-Right>", lambda e: self.relative_move(10000))
        #self.bind("<Shift-Left>", lambda e: pause_and_read_backwards())
        self.bind("<Shift-Right>", lambda e: self._pause_video(True))
        
        self.bind("<KeyPress-Left>", rewind_pressed)
        self.bind("<KeyPress-Right>", forward_pressed)
        self.bind("<KeyRelease>", key_released)
            
        # https://tcl.tk/man/tcl8.6/TkCmd/keysyms.htm
        self.bind("<KP_1>", lambda e: self.set_rate(1))
        self.bind("<KP_2>", lambda e: self.set_rate(2))
        self.bind("<KP_3>", lambda e: self.set_rate(4))
        self.bind("&", lambda e: self.set_rate(1))
        self.bind("1", lambda e: self.set_rate(1))
        self.bind("<eacute>", lambda e: self.set_rate(2))
        self.bind("2", lambda e: self.set_rate(2))
        self.bind("\"", lambda e: self.set_rate(3))
        self.bind("3", lambda e: self.set_rate(3))
        self.bind("'", lambda e: self.set_rate(4))
        self.bind("4", lambda e: self.set_rate(4))
        self.bind("(", lambda e: self.set_rate(5))
        self.bind("5", lambda e: self.set_rate(5))
        self.bind("<Delete>", delete_event)
        self.bind("<n>", select_next_event)
        self.bind("<p>", select_previous_event)

        def callback_select_event(event):
            selection = event.widget.curselection()
            
            if selection:
                self.select_event_in_list(event.widget, selection[0])
            else:
                print(f"deselect")
                #label.configure(text="")

        # self.points_listbox.bind("<<ListboxSelect>>", callback_select_event) # Ne pas binder sur Select sinon le <espace> déclenche l'évenement
        self.points_listbox.bind("<ButtonRelease-1>", callback_select_event)

    def click_on_progress_bar(self, event):
        print("click_on_progress_bar")
        if self.progress_bar.cget("state") == tk.NORMAL:
            print("set")
            value = (event.x / self.progress_bar.winfo_width()) * 100
            self.set_video_position(value)
            self.update_video_progress()

    def select_event_in_list(self, widget, index):
        self.points_listbox.selection_clear(0, tk.END)
        self.points_listbox.selection_set(index)
        self.points_listbox.activate(index)
        self.points_listbox.see(index)
        data = widget.get(index)
        print(f"{index}: {data}")
        
        # Set video position to this event
        time_position = self.model.events[index].time
        # time_position -= 3000
        total_duration = max(self.media_player.get_length(), 0)
        progress_percentage = 0 if (total_duration == 0) else (time_position / total_duration) * 100
        #self.progress_bar.set(progress_percentage)
        # We need to set media timeand not the progress bar that is less precise
        self.media_player.set_time(time_position)
        #self.points_listbox.selection_clear(0, tk.END)
        
    def build_score(self, score):
        return f"Score: {score[0]} - {score[1]}"
        
    def set_rate(self, rate):
        print(f"Setting rate to {rate}")
        self.rate=rate
        self.rate_label.config(text=f"x{self.rate}")
        self.media_player.set_rate(self.rate)
    
    def point(self, points, team_name):
        current_time = self.media_player.get_time()
        current_time_str = str(timedelta(milliseconds=current_time))[:-3]
        
        print(f"{points} point for team {team_name}: {current_time_str}")  
        
        event = self.model.add_event(current_time, points, team_name, self.quarter_listbox.get())
        self.refresh_events()
        self.select_events_in_listbox(event)
        
           
    def select_quarter_event(self, event):
        quarter = self.quarter_listbox.get()
        for event in self.model.events:
            event.quarter = quarter
        self.refresh_events()
    
    def select_events_in_listbox(self, event):
        event_label = self.build_event_label(event)
        for index, label in enumerate(self.points_listbox.get(0, tk.END)):
            if label.startswith(event_label):
                self.points_listbox.selection_clear(0, tk.END)
                self.points_listbox.selection_set(index)
                self.points_listbox.activate(index)
                self.points_listbox.see(index)
                return
        
        
    def build_event_label(self, event):
        time_str = build_time_str(event.time)
        return f"{time_str}:Team {event.team_name}: {event.points}pts"
           
    def refresh_events(self):
        index = self.points_listbox.curselection()
        self.points_listbox.delete(0, tk.END)
        score = self.score
        for event in self.model.events:
            quarter = f", {event.quarter}/4" if event.quarter else ""
            if event.team_name == "A":
                score = (score[0] + event.points, score[1])
            else:
                score = (score[0], score[1] + event.points)
            self.points_listbox.insert(tk.END, f"{self.build_event_label(event)} => {score[0]}-{score[1]}{quarter}")
        
        if index:
            self.points_listbox.selection_set(index)
            self.points_listbox.activate(index)
            self.points_listbox.see(index)
            
        self.score_label.config(text=self.build_score(score))
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Media Files", "*.mp4 *.avi")]
        )
        self.launch_video(file_path)
        
    
    def select_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv *.tmp")]
        )
        self.load_csv_file(file_path)
        
    def save_file(self):
        if self.current_file:
            base = os.path.basename(self.current_file)
            filename, _ = os.path.splitext(base)
            csv_filename = f"{filename}.csv"
        else:
            csv_filename = "output.csv"
   
        file_path = filedialog.asksaveasfilename(
            initialfile=csv_filename,
            filetypes=[("CSV", "*.csv *.tmp")]
        )
        with open(file_path, "w") as file:
            self.model.save(file)
        
    def load_csv_file(self, file_path):
        def time_to_milliseconds(time_str):
            hh, mm, ss = time_str.split(":")
            return int(hh) * 3600000 + int(mm) * 60000 + int(ss) * 1000
        
        self.model = EventData()
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                points, team_name, time, quarter = line.strip().split(";")
                self.model.add_event(time_to_milliseconds(time), int(points), team_name, quarter)
        self.refresh_events()
    
    def build_time_label(self):
        total_duration = max(self.media_player.get_length(), 0)
        current_time = max(self.media_player.get_time(), 0)
        
        # When the progress_bar is set, sometimes the set_video_position is called
        # and the video freezes for a few seconds.
        progress_percentage = 0 if (total_duration == 0) else (current_time / total_duration) * 100
        self.progress_bar.set(progress_percentage) 
        
        current_time_str = build_time_str(milliseconds=current_time)
        total_duration_str = build_time_str(milliseconds=total_duration)
        return f"{current_time_str} / {total_duration_str}"
    
    def refresh_time(self):
        time_label=self.build_time_label()
        self.time_label.config(text=time_label)
            
    def launch_video(self, video_path):
        if video_path:            
            self.model.events = []
            self.refresh_events()
            
            self.current_file = video_path
            self.title(video_path)
            self.refresh_time()
            self.play_video()
            
    def play_video(self):
        media = self.instance.media_new(self.current_file)
        self.media_player.set_media(media)
        #self.media_player.set_hwnd(self.media_canvas.winfo_id())
        self.media_player.set_xwindow(self.media_canvas.winfo_id())
        self.set_rate(1)
        
        self.media_player.play()
            
    def relative_move(self, duration):
        current_time = max(0, self.media_player.get_time() + duration)
        self.media_player.set_time(current_time)

    def fast_forward(self):
        self.relative_move(10000)

    def rewind(self):
        self.relative_move(-10000)

    def pause_video(self):
        self._pause_video(not self.video_paused)
                
    def _pause_video(self, video_paused):
        self.video_paused = video_paused
        if video_paused:
            self.media_player.pause()
        else:
            self.media_player.play()

        self.pause_button.config(text="Pause" if self.video_paused else "Resume")
                
    def stop(self):
        self.media_player.stop()
        self.refresh_time()

    def set_video_position(self, value):
        self.media_player.set_position((float(value) / 100))

    def update_video_progress(self):
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

def argument_parser(): 
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", default=None,
        help="Chemin vers le fichier video")
    ap.add_argument("-s", "--score", default="0-0",
        help="Score initial: -s 15-6")
    ap.add_argument("-c", "--csv", default=None,
        help="Load csv from folder")
    return ap
    
if __name__ == "__main__":
    
    args = vars(argument_parser().parse_args())
    
    # # Get first parameter from command line    
    # video_path = sys.argv[1] if len(sys.argv) > 1 else None
    video_path=args["video"]
    csv_path=args["csv"]
    
    splitted_score=args["score"].split("-")
    initial_score=(int(splitted_score[0]), int(splitted_score[1]))

    app = MediaPlayerApp(initial_score)
    app.update_video_progress()
    app.launch_video(video_path)
    if csv_path and video_path:
        filename = os.path.basename(video_path)
        print( os.path.splitext(filename)[0])
        csv_filename = csv_path + "/" + os.path.splitext(filename)[0].replace(".output", "") + ".csv"
        print(csv_filename)
        app.load_csv_file(csv_filename)
        app.needs_to_start_and_end_events = True
        print(app.media_player.get_length())
        
    app.mainloop()