


import glob
import os
import re
import sys

import moviepy.editor as mpy
from moviepy.video import fx
from moviepy.editor import VideoFileClip, concatenate_videoclips


from video_match import *
from video_recorder import *

SB_LOGO_PATH = "./SBL_Logo_OK_light.jpg"


def create_text_clip(text, font_size, color):
    return mpy.TextClip(
                text,
                font="Charter-bold",
                color=color,
                kerning=4,
                fontsize=font_size,
            )

def position_left_from(clip, clip_from, margin_x, margin_y=0):
    from_right_pos = clip_from.pos(0)[0]
    return clip.set_position((from_right_pos-clip.size[0]-margin_x, margin_y))

def position_right_from(clip, clip_from, margin_x, margin_y=0):
    from_left_pos = clip_from.pos(0)[0]+clip_from.size[0]
    return clip.set_position((from_left_pos+margin_x, margin_y))

def center(clip, video_size):
    return clip.set_position((video_size[0]/2-clip.size[0]/2, 0))
    
def create_score_clip(text):
    return create_text_clip(text, font_size=SCORE_FONT_SIZE, color="Yellow")
    
def create_team_names(team_a, team_b, separator_clip):
     # Should be compute with score_a_clip width with value 100
    team_font_size = 40
    delta_x_label = 140
    delta_y_label = SCORE_FONT_SIZE-team_font_size
    
    team_a_clip = create_text_clip(team_a, font_size=team_font_size, color="White")
    team_a_clip = position_left_from(team_a_clip, separator_clip, delta_x_label, delta_y_label)
    
    team_b_clip = create_text_clip(team_b, font_size=team_font_size, color="White")
    team_b_clip = position_right_from(team_b_clip, separator_clip, delta_x_label, delta_y_label)
    
    return [team_a_clip, team_b_clip]
       
    
# Generate score and logo to display
SCORE_FONT_SIZE = 50
def generate_score_clips(states, team_a, team_b, size):
        
    sb_logo = mpy.ImageClip(SB_LOGO_PATH)\
        .set_position(('left', 0))\
        .resize(width=80)

    all_clips = [sb_logo]
    
    
    for state in states:
        clips = []
        separator_clip = center(create_score_clip("-"), size)
        clips.append(separator_clip)
        
        score_a_clip = position_left_from(create_score_clip(f"{state.score.team_a}"), separator_clip, 10)
        clips.append(score_a_clip)
        
        score_b_clip = position_right_from(create_score_clip(f"{state.score.team_b}"), separator_clip, 10)
        clips.append(score_b_clip)
        
        clips += create_team_names(team_a, team_b, separator_clip)
        
        if state.quarter_time != None:
            quarter_clip = create_text_clip(str(state.quarter_time), font_size=20, color="White")
            quarter_clip = quarter_clip.set_position((size[0]/2-quarter_clip.size[0]/2, 0))
            clips.append(quarter_clip)
            
        all_clips += [clip.set_start(state.start).set_end(state.end) for clip in clips]
    
    return all_clips

def generate_from_dir(csv_folder, video_folder, output_folder, team_a, team_b):
    files = glob.glob(f'{video_folder}/*.mp4')
    files.sort()
    score=Score(0,0)
    for file in files:
        filename=re.sub(r"\.mp4$", "", os.path.basename(file))
        score = generate_from_video(filename, csv_folder, video_folder, output_folder, team_a, team_b, score)
   
# Get information from the file and insert the score to the video.
# Info should be in file [csv_folder]/[filename].csv.
# The original video is in [video_folder]/[filename].mp4.
# `a` and `b` represent the score at the beginning of the video.
# A video is generated in [output_folder]/[filename].output.mp4.
# The method return the score at the end of the video.
#
# If the output file already exists, is not regenerated 
# so we can stop the process and relaunch it to continue the execution.
def generate_from_video(filename, csv_folder, video_folder, output_folder, team_a, team_b, score=Score(0,0)):

    clip_filename = f"{video_folder}/{filename}.mp4"
    print(f"    Video: {clip_filename}")  
    video_clip = mpy.VideoFileClip(clip_filename)
    screen_size = video_clip.size
    duration = video_clip.duration
    print(f"    Duration: {duration}s")
    
    clips = [video_clip]
    
    csv_file=f"{csv_folder}/{filename}.csv" 
    print(f"    CSV: {csv_file}")  
    if os.path.isfile(csv_file):
        match_part = MatchPart.build_from_csv(csv_file, score)
        states = match_part.states(duration)
        clips += generate_score_clips(states, team_a, team_b, screen_size)
        score = match_part.final_score()
    else:
        print("    No csv file")
    
    output_file=f"{output_folder}/{filename}.output.mp4"
    print(f"    Output video: {output_file}")
    print(f"    Final score: {score}")  
    
    # Do not generate when the output file already exists
    if not os.path.isfile(output_file):
        final_clip = mpy.CompositeVideoClip(
            clips, 
            size=screen_size,
        ).set_duration(duration)
        # preset values: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow,
        final_clip.write_videofile(output_file, threads=8, preset="veryfast", fps=None)
    else:
        print(f"File {output_file} already exists. It's not regenerated")
    
    return score

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
            extracted_infos = EventFile().extract_infos(f"{self.csv_folder}/{filename}.csv", score.team_a, score.team_b)
            infos += [(self.format_score(Score(info[0], info[1])), info[0], info[1], start_time+info[2], start_time+info[3]) for info in extracted_infos[1:]]
            
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
        Recorder().record_input("tmp/output.csv")    
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
        
        
        
        # rm  MatchTest/output/*.*;clear;python3 video_generator.py full MatchTest