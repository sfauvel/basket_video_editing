

from datetime import timedelta, datetime
from enum import Enum
import glob
import os
import re
import shutil
import sys
import unittest

import moviepy.editor as mpy
from moviepy.video import fx
from moviepy.video.tools.segmenting import findObjects
from moviepy.editor import VideoFileClip, concatenate_videoclips

WHITE = (255, 255, 255)
# SCREEN_SIZE = (640, 50)
SCREEN_SIZE = (250, 30)

SB_LOGO_PATH = "./SBL_Logo_OK_light.jpg"

class EQUIPE(Enum):
    A=1,
    B=2,
    
def generate_score(points):
    a=0
    b=0
    time=0
    score_evolution = [(a,b,time)]
    for point in points:
        if point[1] == EQUIPE.A:
            a += point[0]
        else:
            b += point[0]
        time = point[2]
        score_evolution.append((a,b,time))
    return score_evolution

class TestVideoGenerator(unittest.TestCase):

    def test_event_record_to_csv(self):
        assert "3;A;12;2" == EventRecord(3, "A", 12, 2).to_csv()
        
    def test_event_record_to_csv_without_quarter(self):
        assert "3;A;12" == EventRecord(3, "A", 12, None).to_csv()


    def test_event_record_from_csv(self):
        record = EventRecord.from_csv("3;A;12;2")
        assert 3 == record.points
        assert "A" == record.team
        assert 12 == record.time_in_seconds
        assert 2 == record.quarter_time

    def test_event_record_from_csv_without_quarter(self):
        record = EventRecord.from_csv("3;A;12")
        assert None == record.quarter_time
        
    def test_event_record_from_csv_with_time_in_minutes(self):
        record = EventRecord.from_csv("3;A;4:25;2")
        assert 4*60+25 == record.time_in_seconds

    def test_generate_score(self):
        self.assertEqual([
                (0, 0, 0),
                (2, 0, 3),
                (2, 2, 5),
                (3, 2, 8),
            ], 
            generate_score([
                (2, EQUIPE.A, 3),
                (2, EQUIPE.B, 5),
                (1, EQUIPE.A, 8),
            ])
        )
    
    def test_extract_infos(self):
        infos = EventFile().extract_lines_infos([
            "2;A;3",
            "1;B;5",
            "3;A;7",
            "0;A;10",
        ], 0, 0, "A", "B", 0)
        assert infos[0] == ("A 0 - 0 B", 0, 0, 0, 3)
        assert infos[1] == ("A 2 - 0 B", 2, 0, 3, 5)
        assert infos[2] == ("A 2 - 1 B", 2, 1, 5, 7)
        assert infos[3] == ("A 5 - 1 B", 5, 1, 7, 10)
        assert len(infos) == 4
        
    def test_extract_infos_with_several_formats(self):
        infos = EventFile().extract_lines_infos([
            "2;A;3s",
            "1;B;5",
            "3;A;3:12",
            "0;A;1:02:14",
        ], 0, 0, "A", "B", 0)
        assert infos[0] == ("A 0 - 0 B", 0, 0, 0, 3)
        assert infos[1] == ("A 2 - 0 B", 2, 0, 3, 5)
        assert infos[2] == ("A 2 - 1 B", 2, 1, 5, 192)
        assert infos[3] == ("A 5 - 1 B", 5, 1, 192, 3734)
        assert len(infos) == 4
        
    def test_extract_infos_with_several_formats_with_an_initial_score_and_time(self):
        infos = EventFile().extract_lines_infos([
            "2;A;3s",
            "0;A;8s",
        ], 5, 8, "A", "B", 10)
        
        assert infos[0] == ("A 5 - 8 B", 5, 8, 10, 13), infos[0]
        assert infos[1] == ("A 7 - 8 B", 7, 8, 13, 18), infos[1]

    def test_time_to_seconds(self):
        assert 5 == time_to_seconds("5")
        assert 5 == time_to_seconds("5s")
        assert 4*60+25 == time_to_seconds("4:25")
        assert 2*3600+14*60+25 == time_to_seconds("2:14:25")

    def test_display_score(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        match = MatchVideo("", "A", "B")
        match.csv_folder = "tmp"
        output = match.display_score()
        assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B"
        
    def test_display_score_from_several_files(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        events = [EventRecord(3,"B",2),EventRecord(2,"A",4),EventRecord(0,"X",10)]
        with (open("tmp/tmp2.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        match = MatchVideo("", "A", "B")
        match.csv_folder = "tmp"
        output = match.display_score()
        assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B\n11: A 5 - 4 B\n13: A 7 - 4 B", output
        
        

###################################################################

def generate_test_video():

    sb_logo = mpy.ImageClip(SB_LOGO_PATH).\
        set_position(('left', 0)).\
        resize(width=20)

    infos = [
        ("0 - 0", 0, 0, 0, 2),
        ("0 - 2", 0, 2, 2, 4),
        ("2 - 2", 2, 2, 4, 6),
        ("3 - 2", 3, 2, 6, 8),
        
        # ("3 - 4", 0, 0, 0, 5),
        #("5 - 4", 0, 0, 0, 5),
    ]
    clips = [sb_logo] + generate_score_clips(infos)
    
    screen_size = (250, 60)
    final_clip = (
        # mpy.CompositeVideoClip([sb_logo, txt_clip] + rotate(stars), size=SCREEN_SIZE)
        mpy.CompositeVideoClip(
            clips, 
            size=screen_size)
        .on_color(color=WHITE, col_opacity=1)
        .set_duration(infos[-1][4])
    )
    final_clip.write_videofile("video_with_python.mp4", fps=10)

class Recorder:
    def wait_for_points(self, ):
        print("Entrez les points et l'équipe (exemple: 2a, 1a,...)")
        x = input()
        score = re.match(r'(\d)([a|b])', x)
        while not score:
            print("Erreur de saisie, retaper les points marqués (exemple: 2a, 1a,...)")
            x = input()
            score = re.match(r'(\d)([a|b])', x)

        return (int(score[1]), score[2].upper())

    def ask_quarter(self):
        while True:
            print("Entrer le numéro du quart-temps ou juste 'ENTRER'...")
            quarter = input()
            if quarter == "":
                print("Aucun quart temps saisi")
                return None
            elif quarter.isdigit():
                print(f"Quart temps: {quarter}")
                return int(quarter)
            print("Erreur de saisie!")
        
        

    # Launch this method to record points scored during the game.
    # Type 'Enter' to indicate that there is a point scored.
    # After that indicate how many points and the team (example: 2a, 1b, ...)
    # When the video is finished, type 'e' to exit.
    # Tips: launch the video first and this program after so you always add the points after they are scored.
    # The output file do not contains score to simplify correction. 
    # You just have to add,remove or modify lines and there is nothing else to modify in the file.
    # If you want to restart after the beginning ??? TODO restart a new file from the time to restart and pass a list of file that will be concatenated
    def record_input(self, filename):

        start_time = datetime.now()

        score = Score()
        records=[]
       
        quarter = self.ask_quarter()
                
        while True:
            print("Tapez 'ENTRER' au prochain panier ou 'e' pour finir...")
            x = input()
            
            next_time = datetime.now()-start_time
            if x == "e":
                records.append(EventRecord(0, "X", round(timedelta.total_seconds(next_time)), quarter))
                break

            (points, team) = self.wait_for_points()
            
            score = score.add(points, team)

            print(f'{team} +{points} => {score.team_a} - {score.team_b} | {str(next_time).split(".")[0]}')
            records.append(EventRecord(points, team, round(timedelta.total_seconds(next_time)), quarter))
        
        print(f"Score final: {score.team_a} - {score.team_b}")
        
        output = "\n".join([r.to_csv() for r in records])
        with open(filename, "w") as output_file:
            output_file.write(output)
        
        return score

class EventRecord:    
    def __init__(self, points, team, time_in_seconds, quarter_time=None):
        self.points = points
        self.team = team
        self.time_in_seconds = time_in_seconds
        self.quarter_time = quarter_time
        
    def to_csv(self):
        values = [str(self.points), self.team, str(self.time_in_seconds)]
        if self.quarter_time:
            values.append(str(self.quarter_time))
        return ";".join(values)
    
    def from_csv(csv):
        print(csv)
        split = csv.split(";")
        print(str(split) + " " + str(len(split)))
        quarter = int(split[3]) if len(split) > 3 else None 
        return EventRecord(int(split[0]), split[1], time_to_seconds(split[2]), quarter) 
        
class Score:
    def __init__(self, team_a = 0, team_b = 0):
        self.team_a = team_a
        self.team_b = team_b
        
    def add(self, points, team):
        if (team == "A"):
            return Score(self.team_a+points, self.team_b)
        else:
            return Score(self.team_a, self.team_b+points)
class EventFile:
    
    def extract_lines_infos(self, lines, a, b, team_a, team_b, initial_start_time):
        infos = []
        score = Score(a, b)
        start_time = initial_start_time
        for line in lines:
            record = EventRecord.from_csv(line)
            points = record.points
            team = record.team
            end_time = record.time_in_seconds + initial_start_time
            
            infos.append((MatchVideo("", team_a, team_b).format_score(score), a, b, start_time, end_time))
                       
            score = score.add(points, team)
            a = score.team_a
            b = score.team_b
            start_time = end_time
                
        return infos


    # Generate information to insert in the video
    def extract_infos(self, input_name, a, b, team_a, team_b, start_time=0):
        infos=[]
        with open(input_name, "r") as input_file:
            lines = input_file.readlines()
            return self.extract_lines_infos(lines, a, b, team_a, team_b, start_time)
    
def time_to_seconds(time):
    seconds = re.match(r"(\d+)s?$", time)
    if seconds:
        return int(seconds[1])
    
    minutes_seconds = re.match(r"(\d+):(\d+)$", time)
    if minutes_seconds:
        return int(minutes_seconds[1])*60+int(minutes_seconds[2])
    
    hours_minutes_seconds = re.match(r"(\d+):(\d+):(\d+)$", time)
    if hours_minutes_seconds:
        return int(hours_minutes_seconds[1])*3600+int(hours_minutes_seconds[2])*60+int(hours_minutes_seconds[3])
    


    
# Generate score and logo to display
def generate_score_clips(infos):
    sb_logo = mpy.ImageClip(SB_LOGO_PATH)\
        .set_position(('left', 0))\
        .resize(width=80)

    clips = [sb_logo]
    for (score,_,_,start_time,end_time) in infos:
        print(f"{start_time} -> {end_time}")
        score_clip = mpy.TextClip(
                score,
                font="Charter-bold",
                color="Yellow",
                kerning=4,
                fontsize=50,
            )\
            .set_position(("center", 0))\
            .set_start(start_time)\
            .set_end(end_time)
        clips.append(score_clip)
    return clips

def generate_from_dir(csv_folder, video_folder, output_folder, team_a, team_b):
    files = glob.glob(f'{video_folder}/*.mp4')
    a=0
    b=0
    files.sort()
    for file in files:
        print(f"Compute {file}")
        filename=re.sub(r"\.mp4$", "", os.path.basename(file))
        (a,b) = generate_from_video(filename, csv_folder, video_folder, output_folder, a, b, team_a, team_b)
   
# Get information from the file and insert the score to the video.
# Info should be in file [csv_folder]/[filename].csv.
# The original video is in [video_folder]/[filename].mp4.
# `a` and `b` represent the score at the beginning of the video.
# A video is generated in [output_folder]/[filename].output.mp4.
# The method return the score at the end of the video.
#
# If the output file already exists, is not regenerated 
# so we can stop the process and relaunch it to continue the execution.
def generate_from_video(filename, csv_folder, video_folder, output_folder, a, b, team_a, team_b):

    clip_filename = f"{video_folder}/{filename}.mp4"
    print(f"    Video: {clip_filename}")  
    video_clip = mpy.VideoFileClip(clip_filename)
    screen_size = video_clip.size
    duration = video_clip.duration
    
    clips = [video_clip]
    
    csv_file=f"{csv_folder}/{filename}.csv" 
    print(f"    CSV: {csv_file}")  
    if os.path.isfile(csv_file):
        infos=EventFile.extract_infos(f"{csv_file}", a, b, team_a, team_b)
        print(f"{infos}")
        clips += generate_score_clips(infos)
        (_,a,b,_,_) = infos[-1]
    else:
        print("    No csv file")
    
    final_clip = (
        mpy.CompositeVideoClip(
            clips, 
            size=screen_size,
        )
        .set_duration(duration)  # start of the last clip which is the end
    )
    output_file=f"{output_folder}/{filename}.output.mp4"
    print(f"    Output video: {output_file}")
    # Do not generate when the output file already exists
    if not os.path.isfile(output_file):
        pass
        # preset values: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow,
        final_clip.write_videofile(output_file, threads=8, preset="veryfast", fps=None)
    else:
        print("File {output_file} already exists. It's not regenerated")
    
    print(f"    Points A: {a} B: {b}")
    return (a,b)

def OLD_concat_file(folder, pattern="*.output.mp4", output_filename="full.mp4"):
    files = glob.glob(f'{folder}/{pattern}')
    files.sort()
    clips=[]
    padding=1
    fade_color=(30,30,30)
    for file in files:
        print(file)
        clip = VideoFileClip(file)
        clip=fx.all.fadeout(clip, padding, final_color=fade_color)
        clip=fx.all.fadein(clip, padding, initial_color=fade_color)        
        clips.append(clip)
    
    # clips = clips[0:2]
    # print("Only 2 videos for test!!!")
    print(f"nb clips: {len(clips)}")
    # Do we need method=compose ?
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(f"{folder}/{output_filename}", threads=8, preset="veryfast", fps=None)
    
    
def concat_file(folder, pattern="*.output.mp4", output_filename="full.mp4"):

    original_dir = os.getcwd()
    os.chdir(folder)
    files = glob.glob(f'{pattern}')
    files.sort()
    with open(f"file_list.txt", "w") as file_list_file:
        file_list_file.write("\n".join([f"file '{filename}'" for filename in files]))
  
    print(f"Output: {output_filename}")
    prog = f'ffmpeg -f concat -i file_list.txt -c copy {output_filename}'
    print(prog)
    os.system(prog)
    os.chdir(original_dir)

    # ffmpeg -ss [start time] -t [duration] -i [input file] -c copy [output file]ffmpeg -ss [start time] -t [duration] -i [input file] -c copy [output file]
    #ffmpeg -ss 3 -i [input file] -c copy output.mp4
    
    # ffmpeg -i VID_20240204_110141.mp4 -c copy intermediate2.ts
    # ...
    # ffmpeg -i "concat:intermediate1.ts|intermediate1.ts|..." -c copy output.mp4
    
    # printf "file '%s'\n" *.mp4 > list.txt
    # ffmpeg -f concat -i list.txt -c copy outfile.mp4


# preset values: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow,
def compress(clip_filename, output_file="compress.mp4", preset="veryfast"):
    clip = mpy.VideoFileClip(clip_filename)
    
    # clip = (
    #     mpy.CompositeVideoClip(
    #         [clip], 
    #         size=clip.size,
    #     )
    #     .set_duration(clip.duration)  # start of the last clip which is the end
    # )
    
    print(f"Check {output_file}")
    if not os.path.isfile(output_file):
        print(f"generate {output_file}")
        clip.write_videofile(output_file, threads=8, preset=preset, fps=None)
    else:
        print("File {output_file} already exists. It's not regenerated")
        
    
def higlights(csv_folder, video_folder, output_folder):
    def extract_line_info(line):
        #print(f"-- {line}")
        (points,team,time) = line.split(";")
        start = time_to_seconds(time)
        return (points,team,start)
    
    
    files = glob.glob(f'{csv_folder}/*.csv')
    files.sort()
    clips = []
    
    print(f"{csv_folder}, {video_folder}, {output_folder}")
    
    padding=1
    fade_color=(30,30,30)
    for file in files:
        print(file)
        
        filename=os.path.basename(file).replace(".csv", "")
                   
        original_clip = VideoFileClip(f"{video_folder}/{filename}.output.mp4") 
        infos=[]
        with open(f"{csv_folder}/{filename}.csv", "r") as input_file:
            lines = input_file.readlines()
            infos = [extract_line_info(line) for line in lines]
            infos = [(points,team,start) for (points,team,start) in infos if int(points) > 1 and team.upper() == "A"]
            
        for (points,team,start) in infos:
            duration_before = 7
            duration_after = 1
            print(f"Subclip {start-duration_before} -> {start+duration_after}")
            
            clip = original_clip.subclip(start-duration_before, start+duration_after).set_start((duration_before+duration_after)*len(clips))
            clip=fx.all.fadeout(clip, padding, final_color=fade_color)
            clip=fx.all.fadein(clip, padding, initial_color=fade_color)
            clips.append(clip)
            
            # for line in lines:
            #     print(f"-- {line}")
            #     # (points,team,time) = line.split(";")
            #     # start = time_to_seconds(time)
            #     (points,team,start) = extract_line_info(line)
                
            #     # 0 point at the end and we don't show 1 point.
            #     if int(points) > 1 and team.upper() == "A":
            #         print(f"Subclip {start-3} -> {start}")
            #         duration_before = 7
            #         duration_after = 1
                    
            #         clip = original_clip.subclip(start-duration_before, start+duration_after).set_start((duration_before+duration_after)*len(clips))
            #         clip=fx.all.fadeout(clip, padding, final_color=fade_color)
            #         clip=fx.all.fadein(clip, padding, initial_color=fade_color)
            #         clips.append(clip)
  
        print(infos)
    clip = mpy.CompositeVideoClip(clips)   
    clip.write_videofile(f"{output_folder}/highlight.mp4", threads=8, preset="veryfast")

def audio_analyze(filename):       
    # 1000/s
    # audio_fps / 10 => audio_fpms
    audio_fpms = 100
    audio_fps = audio_fpms * 10
    video_clip = VideoFileClip(filename, audio_fps=audio_fps)
    # 10s => 441000 values
    # audio_fps = 44100 by default
    # with audio_fps=10000 => 1000 values/s => 100 values/ms

    audio_clip = video_clip.audio
    # print(audioclip)
    # audio_array = audioclip.to_soundarray()
    #print(audio_array)
    
    # Extract the audio as a list of samples
    audio_samples = list(audio_clip.iter_frames())
    import numpy
    # Convert the list of samples to a NumPy array
    sound_array = numpy.array(audio_samples)
    print(len(sound_array))
    
    import datetime
    for time_ms in range(0, int(video_clip.duration*1000), 100):
        max_value = max([value for (value, _) in sound_array[time_ms:time_ms+audio_fpms]])
        if max_value > 0.2:
            date_time = datetime.datetime.fromtimestamp(time_ms/1000.0)
            print(date_time.strftime("%H:%M:%S") + " {:.1f}".format(time_ms/1000) + ": " + "{:.3f}".format(max_value) + ("" if max_value < 0.6 else " ***"))
        
    # for (index, sound) in enumerate(sound_array[:-audio_fpms]):        
    #     max_value = max([value for (value, _) in sound_array[index:index+audio_fpms]])
    #    # print(sound_array[index:index+99])
    #     print(f"{index}: \t" + "{:.2f}".format(sound[0]) + "\t" + "{:.2f}".format(sound[1]) + "\t" + str(max_value))
        
        
    max_volume = audio_clip.max_volume()
    print(f"Max volume: {max_volume}")
    max_volume = max([value for (value, _) in sound_array])
    print(f"Max volume: {max_volume}")
    max_volume = max([value for (_, value) in sound_array])
    print(f"Max volume: {max_volume}")
      

class MatchVideo:
    def __init__(self, root_folder, team_a="LOCAUX", team_b="VISITEUR"):
        self.root_folder = root_folder
        self.csv_folder = f"{self.root_folder}/csv"
        self.video_folder = f"{self.root_folder}/video"
        self.output_folder = f"{self.root_folder}/output"
        self.team_a = team_a
        self.team_b = team_b
    
    def format_score(self, score):
        return f"{self.team_a} {score.team_a} - {score.team_b} {self.team_b}"
        
    def generate(self):
        generate_from_dir(
            csv_folder=self.csv_folder, 
            video_folder=self.video_folder, 
            output_folder=self.output_folder,
            team_a=self.team_a, 
            team_b=self.team_b,
        )
        concat_file(folder=self.output_folder)
        
    def highlight(self):
        higlights(self.csv_folder, self.output_folder, self.root_folder)
    
    def display_score(self):
        files = glob.glob(f'{self.csv_folder}/*.csv')
        files.sort()
        score = Score()
        
        infos = [(self.format_score(score), score.team_a, score.team_b, 0, 0)]
        start_time = 0
        for file in files:
            print(file)
            filename=os.path.basename(file).replace(".csv", "")
            extracted_infos = EventFile().extract_infos(f"{self.csv_folder}/{filename}.csv", score.team_a, score.team_b, self.team_a, self.team_b)
            infos += [(self.format_score(Score(info[1], info[2])), info[1], info[2], start_time+info[3], start_time+info[4]) for info in extracted_infos[1:]]
            
            (_,a,b,_,start_time) = infos[-1]
            score = Score(a, b)
            
        output = "\n".join([f"{time}: {text}" for (text, _,_, time, _) in infos])
        return output
    
if __name__ == "__main__":
    # Launch without arguments to run tests.
    # add `run` argument to launch program.
    args = sys.argv
    folder = args[2] if len(args) > 2 else "Match"
    match = MatchVideo(folder, "SLB", "USCB")
    if len(args) == 1:
        unittest.main()
    elif args[1] == "spike":
        #generate_test_video()
        #ffmpeg_concat_file("short")
        print(match.display_score())
        
        #concat_file(folder="/home/sfauvel/Documents/projects/perso/video/Match/mi-temps2", pattern="*.compress.mp4")
        
        # original_dir = os.getcwd()
        # os.chdir("/media/sfauvel/USB DISK/Match_20024_02_11")
        # files = glob.glob(f'*.mp4')
        # for file in files:
        #     print(file)
        #     compress(file, output_file=f"/home/sfauvel/Documents/projects/perso/video/Match/{file}.compress.mp4", preset="veryfast")
        #compress("Match/mi-temps1/VID_20240211_113451.mp4.compress.mp4", output_file=f"Match/compress.mp4", preset="medium")
        # Original 640,6Mo
        # Compress with CompositeVideoClip veryfast: 518.1mo
        # Compress with CompositeVideoClip medium: 472.1mo
        # Compress with direct write_videofile fps=None: 518.1mo
        # Compress with direct write_videofile fps=24: 457.8mo
        # Compress with direct write_videofile fps=24, medium: 473.6.8mo
        #audio_analyze("Match_2024_02_04/output/VID_20240204_110324.output.mp4")
    elif args[1] == "record":
        Recorder().record_input("output.csv")    
    elif args[1] == "generate":
        #spike("VID_20240204_105730")
        generate_from_dir("short", "short", "short", team_a="SLB", team_b="VISITOR")
    elif args[1] == "concat":
        concat_file("short")
    elif args[1] == "compress":
        # compress("/media/sfauvel/USB DISK1/Match_2024_02_04/VID_20240204_105730.mp4")
        compress("short/full.output.mp4", output_file="short/compress.output.mp4")
    elif args[1] == "full":
        folder = args[2] if len(args) > 2 else "Match"
        MatchVideo(folder, "SLB", "USCB").generate()
        #compress("short/full.mp4", output_file="short/compress.mp4")
    elif args[1] == "highlight":
        folder = args[2] if len(args) > 2 else "Match"
        MatchVideo(folder, "SLB", "USCB").highlight()
    else:
        print(f"Unrecognized command `{args[1]}`")