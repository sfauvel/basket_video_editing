


import glob
import math
import os
import re
import sys

import moviepy.editor as mpy
from moviepy.video import fx


from video_match import *
from video_recorder import *

SB_LOGO_PATH = "./SBL_Logo_OK_light.jpg"
SCORE_FONT_SIZE = 50
TEAM_FONT_SIZE = 40
SHADOW_COLOR="rgb(23, 54, 93)"  # #17365d

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
    
def create_score_clip(text, color="Yellow"):
    return create_text_clip(text, font_size=SCORE_FONT_SIZE, color=color)
    
def create_team_names(team_a, team_b, separator_clip):
     # Should be compute with score_a_clip width with value 100
    delta_x_label = 140
    delta_y_label = SCORE_FONT_SIZE-TEAM_FONT_SIZE
    
    team_a_clip = create_text_clip(team_a, font_size=TEAM_FONT_SIZE, color="White")
    team_a_clip = position_left_from(team_a_clip, separator_clip, delta_x_label, delta_y_label)
    
    team_b_clip = create_text_clip(team_b, font_size=TEAM_FONT_SIZE, color="White")
    team_b_clip = position_right_from(team_b_clip, separator_clip, delta_x_label, delta_y_label)
    
    
    shadow_team_a_clip = set_shadow_position(team_a_clip,
        mpy.TextClip(
                team_a,
                font="Charter-bold",
                color=SHADOW_COLOR,
                kerning=4,
                fontsize=TEAM_FONT_SIZE,
            ))
    
    shadow_team_b_clip = set_shadow_position(team_b_clip,
            mpy.TextClip(
                team_b,
                font="Charter-bold",
                color=SHADOW_COLOR,
                kerning=4,
                fontsize=TEAM_FONT_SIZE,
            ))
    
    return [shadow_team_a_clip, team_a_clip, shadow_team_b_clip, team_b_clip]
       
    
def set_shadow_position(clip, shadow_clip, delta=3):
    return shadow_clip.set_position((clip.pos(0)[0]+delta, clip.pos(0)[1]+delta))

# Generate score and logo to display
def generate_score_clips(states, team_a, team_b, size):
    print(f"{team_a} {team_b}")    
    sb_logo = mpy.ImageClip(SB_LOGO_PATH)\
        .set_position(('left', 0))\
        .resize(width=80)

    all_clips = [sb_logo]
    
    for state in states:
        clips = []
        
        separator_clip = center(create_score_clip("-"), size)
        clips.append(set_shadow_position(separator_clip, create_score_clip("-", color=SHADOW_COLOR)))
        clips.append(separator_clip)
        
        score_a_clip = position_left_from(create_score_clip(f"{state.score.team_a}"), separator_clip, 10)
        clips.append(set_shadow_position(score_a_clip, create_score_clip(f"{state.score.team_a}", color=SHADOW_COLOR)))
        clips.append(score_a_clip)
        
        score_b_clip = position_right_from(create_score_clip(f"{state.score.team_b}"), separator_clip, 10)
        clips.append(set_shadow_position(score_b_clip, create_score_clip(f"{state.score.team_b}", color=SHADOW_COLOR)))
        clips.append(score_b_clip)
        
        clips += create_team_names(team_a, team_b, separator_clip)
        
        if state.quarter_time != None:
            quarter_clip = create_text_clip(str(state.quarter_time), font_size=20, color="White")
            quarter_clip = quarter_clip.set_position((size[0]/2-quarter_clip.size[0]/2, 0))
            clips.append(set_shadow_position(quarter_clip, create_text_clip(str(state.quarter_time), font_size=20, color=SHADOW_COLOR), 2))
            clips.append(quarter_clip)
            
        all_clips += [clip.set_start(state.start).set_end(state.end) for clip in clips]
    
    return all_clips

def files_sorted(pattern):
    files = glob.glob(pattern)
    files.sort()
    return files 

def generate_from_dir(csv_folder, video_folder, output_folder, team_a, team_b):
    score=Score(0,0)
    for file in files_sorted(f'{video_folder}/*.mp4'):
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
    
    os.makedirs(output_folder, exist_ok=True)
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

    
def concat_file(folder, files, output_filename="full.mp4"): 
    print(files)
    with open(f"{folder}/file_list.txt", "w") as file_list_file:
        file_list_file.write("\n".join([f"file '{filename}'" for filename in files]))
  
    print(f"Output: {output_filename}")
    prog = f'ffmpeg -f concat -i {folder}/file_list.txt -c copy {folder}/{output_filename}'
    print(prog)
    os.system(prog)
    
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
        
    
def create_highights_clip(highlights, filename, clips):
    
    padding=1
    fade_color=(30,30,30)
    print(filename)
    for highlight in highlights:
        duration_before = 7
        duration_after = 1
        
        original_clip = mpy.VideoFileClip(filename) 
        print(f"    Extract from {highlight.time_in_seconds-duration_before}s to {highlight.time_in_seconds+duration_after}s")
        print(f"    Start from {(duration_before+duration_after)*len(clips)}s")
        
        clip = original_clip.subclip(highlight.time_in_seconds-duration_before, highlight.time_in_seconds+duration_after).set_start((duration_before+duration_after)*len(clips))
        clip=fx.all.fadeout(clip, padding, final_color=fade_color)
        clip=fx.all.fadein(clip, padding, initial_color=fade_color)
        clips.append(clip)
        
  
def higlights(csv_folder, video_folder, output_folder, output_file, filter):    
    clips = []
    
    for file in files_sorted(f'{csv_folder}/*.csv'):
        print(file)
        
        filename=os.path.basename(file).replace(".csv", "")
                   
        match = MatchPart.build_from_csv(f"{csv_folder}/{filename}.csv")
        highlights = [event for event in match.events if filter(event)]
        
        create_highights_clip(highlights, f"{video_folder}/{filename}.output.mp4", clips)
        
    clip = mpy.CompositeVideoClip(clips)   
    clip.write_videofile(f"{output_folder}/{output_file}.mp4", threads=8, preset="veryfast")

class MatchVideo:
    def __init__(self, root_folder, team_a="LOCAUX", team_b="VISITEUR"):
        self.root_folder = root_folder
        self.root_name = self.root_folder.split("/")[-1]
        self.csv_folder = f"{self.root_folder}/csv"
        self.video_folder = f"{self.root_folder}/video"
        self.output_folder = f"{self.root_folder}/output"
        self.team_a = team_a
        self.team_b = team_b

        
    def format_score(self, score):
        return f"{self.team_a} {str(score.team_a).rjust(3)} - {str(score.team_b).ljust(3)} {self.team_b} ({score.team_a-score.team_b})"
        
    def generate(self):
        generate_from_dir(
            csv_folder=self.csv_folder, 
            video_folder=self.video_folder, 
            output_folder=self.output_folder,
            team_a=self.team_a, 
            team_b=self.team_b,
        )
        
    def create_single_video(self):
        pattern="*.output.mp4"
        files = [file.split('/')[-1] for file in files_sorted(f"{self.output_folder}/{pattern}")]
    
        concat_file(self.output_folder, files, f"{self.root_name}_complet.mp4")
        
    def create_single_by_quarter(self):
        compute_key = lambda quarter: quarter
        
        all_files = self.split_by_quarter(compute_key)
    
        for (key, files) in all_files.items():
            concat_file(self.output_folder, files, f"{self.root_name}_quart_temps_{key}.mp4")
    
    def create_single_by_halftime(self):
        compute_key = lambda quarter: math.ceil(quarter / 2)
        
        all_files = self.split_by_quarter(compute_key)
       
        for (key, files) in all_files.items(): 
            concat_file(self.output_folder, files, f"{self.root_name}_mi_temps_{key}.mp4")
            
    def split_by_quarter(self, compute_key):
        pattern="*.output.mp4"
        files = [file.split('/')[-1] for file in files_sorted(f"{self.output_folder}/{pattern}")]
      
        all_files = {}
        for file in files:
            filename=os.path.basename(file).replace(".output.mp4", "")
            csv_file=f"{self.csv_folder}/{filename}.csv"
            if os.path.isfile(csv_file):
                match = MatchPart.build_from_csv(csv_file)
                quarter = match.events[0].quarter_time
                
                key = compute_key(quarter)
                if not key in all_files:
                    all_files[key] = []
                all_files[key].append(file)
            else:
                print(f"Csv file '{csv_file}' does not exists")
                
        return all_files
        
    def highlight(self):
        
        team_to_highlight = "A" if self.team_a == "SLB" else "B"
        def team_points(event):
            return int(event.points) > 1 and event.team.upper() == team_to_highlight
                   
        def points(event):
            return int(event.points) > 1
        
        def all_points(event):
            return int(event.points) > 0
        
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_slb", team_points)
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_tous", points)
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_tous_les_points", all_points)
    
    def display_score(self):
        score = Score()
        
        infos = [(self.format_score(score), score.team_a, score.team_b, 0, 0)]
        start_time = 0
        for file in files_sorted(f'{self.csv_folder}/*.csv'):
            print(file)
            filename=os.path.basename(file).replace(".csv", "")
            extracted_infos = EventFile().extract_infos(f"{self.csv_folder}/{filename}.csv", score.team_a, score.team_b)
            infos += [(self.format_score(Score(info[0], info[1])), info[0], info[1], start_time+info[2], start_time+info[3]) for info in extracted_infos[1:]]
            
            (_,a,b,_,start_time) = infos[-1]
            score = Score(a, b)
            
        output = "\n".join([f"{time}:".ljust(6) + f"{text}" for (text, _,_, time, _) in infos])
        return output
    
if __name__ == "__main__":
    args = sys.argv
    folder = args[2] if len(args) > 2 else "Match"
    match = MatchVideo(folder, "SLB", "BOUAYE")
    if args[1] == "spike":
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
    
    elif args[1] == "validate":
        (output, valid) = EventRecord.validate(match.csv_folder)
        print(output)
        print("Ok" if valid else "ERRORS")
    elif args[1] == "score":
        print(match.display_score())
            
    elif args[1] == "generate":
        match.generate()
        
    elif args[1] == "concat":
        concat_file("short")
        
    elif args[1] == "compress":
        # compress("/media/sfauvel/USB DISK1/Match_2024_02_04/VID_20240204_105730.mp4")
        compress("short/full.output.mp4", output_file="short/compress.output.mp4")
        
    elif args[1] == "highlight":
        match.highlight()
        
    elif args[1] == "quarter":
        match.create_single_by_quarter()
        
    elif args[1] == "half":
        match.create_single_by_halftime()
        
    elif args[1] == "all":
        match.create_single_video()
        
    elif args[1] == "full":
        match.generate()
        match.highlight()
        match.create_single_by_quarter()
        
    else:
        print(f"Unrecognized command `{args[1]}`")
        
        
        
        # rm  MatchTest/output/*.*;clear;python3 video_generator.py full MatchTest