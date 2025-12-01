import glob
import math
import os
import re
import sys

import moviepy as mpy
import moviepy.video.fx as fx 

from game_info import GameInfo
from ass_generator import AssGenerator, Event
from video_graph import *
from video_match import *

SB_LOGO_PATH = "../SLB_Logo_OK_light.jpg"
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
            
        all_clips += [clip.with_start(state.start).with_end(state.end) for clip in clips]
    
    return all_clips

def generate_from_dir(csv_folder, video_folder, output_folder, team_a, team_b):
    score=Score(0,0)
    for file in files_sorted(f'{video_folder}/*.mp4'):
        filename=re.sub(r"\.mp4$", "", os.path.basename(file))
        # score = generate_from_video(filename, csv_folder, video_folder, output_folder, team_a, team_b, score)
        score = generate_ass(filename, csv_folder, video_folder, output_folder, team_a, team_b, score)
        

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
    output_file=f"{output_folder}/{filename}.mp4"
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

# Generate score to display
def generate_events(states, delay_after_event=1):
    delay = 0
    events = []
    for state in states:
              
        # Add a delay to display score after the event.
        start = state.start+delay
        delay = delay_after_event
        end = state.end+delay
        
        events.append(Event("ScoreA", layer=0, text=str(state.score.team_a), start=start, end=end))
        events.append(Event("ScoreB", layer=0, text=str(state.score.team_b), start=start, end=end))

    return events
   
# Get information from the file and insert the score to the video.
# Info should be in file [csv_folder]/[filename].csv.
# The original video is in [video_folder]/[filename].mp4.
# `a` and `b` represent the score at the beginning of the video.
# A video is generated in [output_folder]/[filename].output.mp4.
# The method return the score at the end of the video.
#
# If the output file already exists, is not regenerated 
# so we can stop the process and relaunch it to continue the execution.
def generate_ass(filename, csv_folder, video_folder, output_folder, team_a, team_b, score=Score(0,0)):

    clip_filename = f"{video_folder}/{filename}.mp4"
    print(f"    Video: {clip_filename}")  
    video_clip = mpy.VideoFileClip(clip_filename)
    screen_size = video_clip.size
    duration = video_clip.duration
    print(f"    Duration: {duration}s")
    
    csv_file=f"{csv_folder}/{filename}.csv" 
    print(f"    CSV: {csv_file}")  

    if os.path.isfile(csv_file):
        match_part = MatchPart.build_from_csv(csv_file, score)
        states = match_part.states(duration)
        score = match_part.final_score()

        ass_file_content = AssGenerator(duration, team_a, team_b, states[-1].quarter_time).generate(generate_events(states))
    
        os.makedirs(output_folder, exist_ok=True)
        output_file=f"{output_folder}/{filename}.ass"
        with open(f"{output_file}", "w") as file_ass:
            file_ass.write(ass_file_content)
    
    else:
        print("    No csv file")
    
    print(f"    Final score: {score}")  
    
    return score

    
def concat_file(folder, files, output_filepath="full.mp4"): 
    print(files)
    with open(f"{folder}/file_list.txt", "w") as file_list_file:
        file_list_file.write("\n".join([f"file '{filename}'" for filename in files]))
  
    print(f"Output: {output_filepath}")
    prog = f'ffmpeg -f concat -i {folder}/file_list.txt -c copy {output_filepath}'
    print(prog)
    os.system(prog)
    
    # ffmpeg -ss [start time] -t [duration] -i [input file] -c copy [output file]ffmpeg -ss [start time] -t [duration] -i [input file] -c copy [output file]
    #ffmpeg -ss 3 -i [input file] -c copy output.mp4
    
    # ffmpeg -i VID_20240204_110141.mp4 -c copy intermediate2.ts
    # ...
    # ffmpeg -i "concat:intermediate1.ts|intermediate1.ts|..." -c copy output.mp4
    
    # printf "file '%s'\n" *.mp4 > list.txt
    # ffmpeg -f concat -i list.txt -c copy outfile.mp4

#def insert_score(ass_folder, video_folder, output_folder): 
#    
#    os.makedirs(output_folder, exist_ok=True)
#
#    for file in files_sorted(f'{ass_folder}/*.ass'):
#        filename=re.sub(r"\.ass$", "", os.path.basename(file))
#        print(filename)
#        prog = f'ffmpeg -i {video_folder}/{filename}.mp4 -vf "ass={ass_folder}/{filename}.ass" -c:a copy -c:v libx265 -crf 28 {output_folder}/{filename}.mp4'
#        print(prog)
#        os.system(prog)
#        
#    # print(files)
#    # with open(f"{folder}/file_list.txt", "w") as file_list_file:
#        # file_list_file.write("\n".join([f"file '{filename}'" for filename in files]))
##   
#    # print(f"Output: {output_filepath}")
#    # prog = f'ffmpeg -f concat -i {folder}/file_list.txt -c copy {output_filepath}'
#    # print(prog)
#    # os.system(prog)
    

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
        
def collapse_overlaps(highlights, duration_before, duration_after):
    result = []
    (previous_start, previous_end) = (0, 0)
    for highlight in highlights:
        start_subclip = max(0, highlight.time_in_seconds-duration_before)
        end_subclip = highlight.time_in_seconds+duration_after
      
        if previous_end >= start_subclip:
            if len(result) > 0:
                result.pop()
            start_subclip = previous_start
        
        result.append((start_subclip, end_subclip))
        (previous_start, previous_end) = result[-1]
        
    return result
    
def create_highights_clip(highlights, 
        filename, 
        clips, 
        start_in_final_clip=0,
        duration_before = 7,
        duration_after = 1):
    
    clip = mpy.VideoFileClip(filename)
    original_clip_duration = clip.duration
    clip.close()
    video_parts = [(start_subclip, min(original_clip_duration, end_subclip)) for (start_subclip, end_subclip) in collapse_overlaps(highlights, duration_before, duration_after)]
    return add_clip_parts(video_parts, filename, clips, start_in_final_clip)
    
def add_clip_parts(video_parts, 
        filename, 
        clips, 
        start_in_final_clip=0):
    
    padding=1
    fade_color=(30,30,30)
    print(f"Filename: {filename}")

    original_clip = mpy.VideoFileClip(filename) 
    for (start_subclip, end_subclip) in video_parts:
        print(f"    Extract from {start_subclip}s to {end_subclip}s")
        print(f"    Start from {start_in_final_clip}s")
        
        clip = original_clip.subclipped(start_subclip, end_subclip).with_start(start_in_final_clip)
        clip=fx.FadeOut(padding, final_color=fade_color).apply(clip)
        clip=fx.FadeIn(padding, initial_color=fade_color).apply(clip)
        clips.append(clip)
        
        start_in_final_clip += (end_subclip-start_subclip)
        
    return start_in_final_clip
        
  
def higlights(csv_folder, 
              video_folder, 
              output_folder, 
              output_file, 
              filter, 
              duration_before = 7, 
              duration_after = 1,
              input_video_filename = lambda filename: filename,
              csv_filter = "*"):
    more_time_at_the_end = 2

    clips = []
    total_time = 0

    match_events=highlights_parts(csv_folder, filter, csv_filter, duration_before, duration_after, more_time_at_the_end)
    for (filepath, highlights) in match_events:
        print((filepath, highlights))

        filename=os.path.basename(filepath).replace(".csv", "")
        video_file=f"{video_folder}/{input_video_filename(filename)}.mp4"
        original_clip_duration = mpy.VideoFileClip(video_file).duration
        video_parts = [(start_subclip, min(original_clip_duration, end_subclip)) for (start_subclip, end_subclip) in highlights]
        total_time = add_clip_parts(video_parts, video_file, clips, total_time)
 

    clip = mpy.CompositeVideoClip(clips)   
    clip.write_videofile(f"{output_folder}/{output_file}.mp4", threads=8, preset="veryfast")
    ##clip.close()

def highlights_parts(csv_folder, filter, csv_filter, duration_before, duration_after, more_time_at_the_end):
    match_events_tmp = MatchPart.build_from_csv_folder(csv_folder, filter, csv_filter)
    match_events = [(filename, collapse_overlaps(highlights, duration_before, duration_after)) for (filename, highlights) in match_events_tmp]
    
    last_file_hightlights = match_events[-1][1]
    last_file_hightlights[-1] = (last_file_hightlights[-1][0],  last_file_hightlights[-1][1]+more_time_at_the_end)
    return match_events        

class MatchVideo:
    def __init__(self, root_folder, team_a="LOCAUX", team_b="VISITEUR"):
        
        self.root_folder = os.path.normpath(root_folder)
        self.root_name = os.path.basename(os.path.abspath(root_folder))
        self.csv_folder = f"{self.root_folder}/csv"
        self.video_folder = f"{self.root_folder}/video"
        self.output_folder = f"{self.root_folder}/output"
        self.ass_folder = f"{self.root_folder}/ass"
        self.with_logo_folder = f"{self.root_folder}/logo"
        self.team_a = team_a
        self.team_b = team_b
        
    def __str__(self):
        return f"""
        root_folder: {self.root_folder}
        root_name: {self.root_name}
        csv_folder: {self.csv_folder}
        video_folder: {self.video_folder}
        output_folder: {self.output_folder}
        ass_folder: {self.ass_folder}
        team_a: {self.team_a}
        team_b: {self.team_b}
        """
        
    def format_score(self, score):
        return f"{self.team_a} {str(score.team_a).rjust(3)} - {str(score.team_b).ljust(3)} {self.team_b} "
        
    def init_csv(self):
        if not os.path.isdir(self.video_folder):
            print(f"Folder {self.video_folder} does not exists")
            return
    
        if not os.path.isdir(self.csv_folder):
            os.makedirs(self.csv_folder)
        
        for file in files_sorted(f'{self.video_folder}/*.mp4'):
            filename=re.sub(r"\.mp4$", "", os.path.basename(file))
            csv_file=f"{self.csv_folder}/{filename}.csv"
            if not os.path.isfile(csv_file):
                with open(csv_file, "w") as csv_file:
                    csv_file.write("0;-;0:00;1")
        
    def generate(self):
        generate_from_dir(
            csv_folder=self.csv_folder,  
            video_folder=self.with_logo_folder,
            output_folder=self.ass_folder,
            team_a=self.team_a, 
            team_b=self.team_b,
        )
        

    def insert_score(self):
        AssGenerator.insert_score(self.ass_folder, self.with_logo_folder, self.output_folder)

    def extract(self, input_data):
        higlights("Match_2024_03_17/extract", 
                    "Match_2024_03_17/output", 
                    "Match_2024_03_17/extract", 
                    input_data, 
                    lambda event: True, 
                    duration_before = 5, 
                    duration_after = 3,
                    input_video_filename = lambda filename: f"{self.root_name}_complet",
                    csv_filter=input_data)
        
    def create_single_video(self):
        pattern="*.mp4"
        files = [file.split('/')[-1] for file in files_sorted(f"{self.output_folder}/{pattern}")]
    
        concat_file(self.output_folder, files, f"{self.root_folder}/{self.root_name}_complet.mp4")
        
    def create_single_by_quarter(self):
        compute_key = lambda quarter: quarter
        
        all_files = self.split_by_quarter(compute_key)
    
        for (key, files) in all_files.items():
            concat_file(self.output_folder, files, f"{self.root_folder}/{self.root_name}_quart_temps_{key}.mp4")
    
    def create_single_by_halftime(self):
        compute_key = lambda quarter: math.ceil(quarter / 2)
        
        all_files = self.split_by_quarter(compute_key)
       
        for (key, files) in all_files.items(): 
            concat_file(self.output_folder, files, f"{self.root_folder}/{self.root_name}_mi_temps_{key}.mp4")
            
    def split_by_quarter(self, compute_key):
        pattern="*.mp4"
        files = [file.split('/')[-1] for file in files_sorted(f"{self.output_folder}/{pattern}")]
      
        all_files = {}
        for file in files:
            filename=os.path.basename(file).replace(".mp4", "")
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

    def highlightA(self): 
        self.highlight_team_points("A", team_name=self.team_a)
        
    def highlightB(self):         
        self.highlight_team_points("B", team_name=self.team_b)
    
    # Build video with all moment with some points. 
    # TODO it could be better to keep all moment with team 'X' and have this option in video editor.
    def highlight_match(self):
        def team_points(event):
            return int(event.points) > 0
        
        filename = f'{self.root_name}_highlights'

        duration_before = 7 
        duration_after = 4
        higlights(self.csv_folder, self.output_folder, self.root_folder, filename, team_points, duration_before, duration_after)
        
    def highlight(self): 
        duration_before = 7
        duration_after = 2
        
        
        # self.highlight_team_points(team_to_highlight, duration_before, duration_after, build_input_video_filename)
        
        # team_to_highlight = "A" if self.team_a == "SLB" else "B"
        self.highlight_team_points("A", duration_before, duration_after, team_name=self.team_a)
        self.highlight_team_points("B", duration_before, duration_after, team_name=self.team_b)
        
        # self.highlight_points(duration_before, duration_after, build_input_video_filename)
        # self.highlight_all_points(duration_before, duration_after, build_input_video_filename)
        # self.output_folder=self.with_logo_folder
        # self.highlight_all_points(duration_before, duration_after)
    
    def highlight_team_points(self, team, duration_before = 7, duration_after = 2, build_input_video_filename = lambda filename: filename, team_name="slb"):
        def team_points(event):
            return int(event.points) > 1 and event.team.upper() == team
        
        filename = f'{self.root_name}_paniers_{team_name.lower().replace(" ", "_").replace("/", "_")}'

        higlights(self.csv_folder, self.output_folder, self.root_folder, filename, team_points, duration_before, duration_after, build_input_video_filename)
        
    def highlight_points(self, duration_before = 7, duration_after = 2, build_input_video_filename = lambda filename: filename):
        def points(event):
            return int(event.points) > 1
        
        higlights(self.csv_folder, self.output_folder, self.root_folder, f"{self.root_name}_paniers_tous", points, duration_before, duration_after, build_input_video_filename)
        
    def highlight_all_points(self, duration_before = 7, duration_after = 2, build_input_video_filename = lambda filename: filename):
        def all_points(event):
            return int(event.points) > 0
        
        higlights(self.csv_folder, self.output_folder, self.root_folder, f"{self.root_name}_paniers_tous_les_points", all_points, duration_before, duration_after, build_input_video_filename)
        
    
    def display_by_quarter(self, match_parts):
 
        by_quarter = match_parts.score_by_quarter()
        last_quarter = max([int(quarter) for quarter in by_quarter.keys()])
        
        result = ""
        result += f"[%autowidth]\n|====\n"
        result += f"| Qt | A la fin | pendant \n"
        
        total_score = Score(0, 0)
        for quarter in range(1, last_quarter+1):
            score = by_quarter[quarter]
            total_score = Score(total_score.team_a+score.team_a, total_score.team_b+score.team_b)
            result += f"| {quarter} | {total_score} | {score}\n"
        result += f"|====\n"
            
        return result;
    
    class PointStats:        
        def __init__(self):
            self.team_a = {1:0, 2:0, 3:0}
            self.team_b = {1:0, 2:0, 3:0}
            
        def add(self, record):
            if record.team == "A":
                self.team_a[record.points] += 1
            if record.team == "B":
                self.team_b[record.points] += 1
    
    def final_score(self):
        match_parts = MatchPart.concat_match_parts([MatchPart.build_from_csv(f"{file}") for file in files_sorted(f'{self.csv_folder}/*.csv')])        
        score = match_parts.final_score()
        return f"{score.team_a}-{score.team_b}"
    
    def final_score_before(self, first_file_exclude):
        csv_folder = self.csv_folder
        # csv_folder = f"{self.root_folder}/auto_detect"
        match_parts = MatchPart.concat_match_parts([MatchPart.build_from_csv(f"{file}") for file in files_before(f'{csv_folder}/*.csv', f"{csv_folder}/{first_file_exclude}")])        
        score = match_parts.final_score()
        return f"{score.team_a}-{score.team_b}"
    
    def display_score(self):
        match_parts = MatchPart.concat_match_parts([MatchPart.build_from_csv(f"{file}") for file in files_sorted(f'{self.csv_folder}/*.csv')])        
        game_sheet=match_parts.game_sheet()
        print(f"========\n{game_sheet}\n==========")
         
        ## Display by quarter
        result = ""
        result += self.display_by_quarter(match_parts)
        result += "\n\n"
        
        ## Display by points
        last_points = MatchVideo.PointStats() 
        for event in [event for event in match_parts.events if event.points > 0]:
            last_points.add(event)
       
        result += f"[%autowidth]\n|====\n"
        result += f"| Equipe | 1pt | 2pts | 3pts \n"
        result += f"| {self.team_a} |  {last_points.team_a[1]} | {last_points.team_a[2]} | {last_points.team_a[3]}\n"
        result += f"| {self.team_b} | {last_points.team_b[1]} | {last_points.team_b[2]} | {last_points.team_b[3]}\n"
        result += f"|====\n\n"
        
        ## Display graph
        try:
            result += display_graph(match_parts) 
        except Exception as e:  
            result += f"Error: {e}"
            print(f"!!!!!!!!!!!!\nError: {e}\n!!!!!!!!!!!!")
        
        ## Write to stat file
        # print(result)        
        with (open(f"{self.root_folder}/stats.adoc", "w")) as stats_file:
            stats_file.write(result)
            
        return match_parts.display(self.team_a, self.team_b)


def higlights_sequence(csv_folder, 
              video_folder, 
              output_folder, 
              output_file_path, 
              filter, 
              duration_before = 7, 
              duration_after = 1,
              input_video_filename = lambda filename: filename,
              csv_filter = "*",
              dry_run=False):
    clips = []
    
    parts_by_filename = []
    for file in files_sorted(f'{csv_folder}/{csv_filter}.csv'):
        print(file)
        
        filename=os.path.basename(file).replace(".csv", "")
                   
        match = MatchPart.build_from_csv(f"{csv_folder}/{filename}.csv")
        highlights = [event for event in match.events if filter(event)]
        
        index = 0        
        video_parts = []
        sequences_are_closed = True
        for index in range(0, len(highlights)):
            if highlights[index].team == ">":
                if not sequences_are_closed:
                    print(f"ERROR: sequence open twice: {highlights[index]}")
                    print(f"   File: {filename}")
                    print(f"   Time: {seconds_to_time(highlights[index].time_in_seconds)}")
                    raise 
                sequences_are_closed = False
                video_parts.append((highlights[index].time_in_seconds, None))
            elif highlights[index].team == "<":
                sequences_are_closed = True
                video_parts[-1] = (video_parts[-1][0], highlights[index].time_in_seconds)
        
        assert sequences_are_closed
        parts_by_filename.append((filename, video_parts))
    
    if dry_run:
        print("Dry mode: sequence video not generate")
        return
    
    total_time = 0
    for (filename, video_parts) in parts_by_filename:        
        total_time = add_clip_parts(video_parts, f"{output_folder}/{input_video_filename(filename)}.mp4", clips, total_time)
            
    clip = mpy.CompositeVideoClip(clips)   
    clip.write_videofile(f"{output_file_path}.mp4", threads=8, preset="veryfast")
    clip.close()


def higlights_demo():

    # Actuellement
    # Incrustation du score dans chaque video (reencodage)
    # Concatenation des videos avec FadeIn/FadeOut (reencodage)
    
    # Montage rapide
    # Extraction des moments forts puis concatenation des clips (pas de reencodage)

    input_folder="Match_2024_10_05/video"
    video_file="VID_20241005_160156"
    output_folder="tmp"
    output_file=f"{video_file}_cut"
    #

    video_parts = []
   
    video_parts.append((10, 15))
    video_parts.append((20, 25))
    video_parts.append((30, 35))
    
    print(f"output_folder: {output_folder}")
    ffmpeg = True
    if ffmpeg:
        files=[]
        for (i, part) in enumerate(video_parts):
            output_part_file=f"{video_file}_part_{i}.mp4"
            files.append(output_part_file)
            prog = f"ffmpeg -i {input_folder}/{video_file}.mp4 -ss 00:00:{part[0]} -t 00:00:{part[1]-part[0]}  -c copy {output_folder}/{output_part_file}"
            print(prog)
            os.system(prog)
            
        with open(f"{output_folder}/file_list.txt", "w") as file_list_file:
            file_list_file.write("\n".join([f"file '{filename}'" for filename in files]))    
            
        prog = f'ffmpeg -f concat -i {output_folder}/file_list.txt -c copy {output_folder}/{output_file}.mp4'
        
        print(prog)
        os.system(prog)
    else:
        clips = []
        total_time = 0
        total_time = add_clip_parts(video_parts, f"{input_folder}/{video_file}.mp4", clips, total_time)
            
        clip = mpy.CompositeVideoClip(clips)   
        clip.write_videofile(f"{output_folder}/{output_part_file}.mp4", threads=8, preset="veryfast")


def sequence(match, dry_run=False):
    csv_folder=f"{match.root_folder}/sequence"
    files = EventRecord.files_sorted(f"{csv_folder}/*.csv")
        
    higlights_sequence(f"{match.root_folder}/sequence",
                    f"{match.root_folder}/video",
                    f"{match.root_folder}/output",
                    f"{match.root_folder}/sequence",
                    lambda event: True, 
                    0, 
                    0,
                    dry_run=dry_run)

def extract_clips(video_file, clip_times, time_in_final_video = 0):
    clip_list = []

    for time in clip_times:
        video = mpy.VideoFileClip(video_file) 
        clip = video.subclipped(time[0], time[1]).with_start(time_in_final_video)
        clip_list.append(clip)        
        time_in_final_video += clip.duration
    return clip_list
    
if __name__ == "__main__":
    args = sys.argv
    folder = args[2] if len(args) > 2 else "Match"

    game_info = GameInfo.load(f"{folder}/{GameInfo.FILENAME}")

    match = MatchVideo(folder, game_info.locaux, game_info.visiteurs)
    if args[1] == "spike":
        match.csv_folder = f"{match.root_folder}/test"
        match.video_folder = f"{match.root_folder}/video"
        match.output_folder = f"{match.root_folder}/test"
   
        print(f"Match {folder}:\n{match}")
   
    elif args[1] == "validate":
        (output, valid) = EventRecord.validate(match.csv_folder)
        print(output)
        print("Ok" if valid else "ERRORS")
    elif args[1] == "score":
        print(match.display_score())
    elif args[1] == "final_score":
        print(match.final_score())
    elif args[1] == "score_before":
        before_csv_file = args[3] if len(args) > 3 else None
        if before_csv_file:
            print(match.final_score_before(before_csv_file))
        else:
            print(match.final_score())
        
    elif args[1] == "extract":
        match.extract("big_fautes")
        
    elif args[1] == "generate":
        match.generate()

    elif args[1] == "csv":
        match.init_csv()
        
    elif args[1] == "concat":
        concat_file("short")
        
    elif args[1] == "compress":
        # compress("/media/sfauvel/USB DISK1/Match_2024_02_04/VID_20240204_105730.mp4")
        compress("short/full.output.mp4", output_file="short/compress.output.mp4")
        
    elif args[1] == "highlight":
        match.highlight()
        
    elif args[1] == "highlightA":
        match.highlightA()

    elif args[1] == "highlightB":
        match.highlightB()

    elif args[1] == "quarter":
        match.create_single_by_quarter()
        
    elif args[1] == "half":
        match.create_single_by_halftime()
        
    elif args[1] == "single":
        match.create_single_video()
        
    elif args[1] == "full":
        match.generate()
        match.insert_score()
        match.highlightA()
        match.highlightB()
        match.create_single_video()
        sequence(match)
        
    elif args[1] == "sequence":
        sequence(match)
        
    elif args[1] == "sequence_dry":
        try:
            sequence(match, True)
        except:
            print("ERROR")
            exit(1)
    elif args[1] == "xxx":
       # match.highlight_match()

        match.insert_score()

    else:
        print(f"Unrecognized command `{args[1]}`")
        
        
        
        # rm  MatchTest/output/*.*;clear;python3 video_generator.py full MatchTest