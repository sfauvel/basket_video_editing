


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
    
    padding=1
    fade_color=(30,30,30)
    print(filename)
   
    for (start_subclip, end_subclip) in collapse_overlaps(highlights, duration_before, duration_after):
        
        original_clip = mpy.VideoFileClip(filename) 
        # start_subclip = max(0, highlight.time_in_seconds-duration_before)
        # end_subclip = highlight.time_in_seconds+duration_after
        
        
        end_subclip = min(original_clip.duration, end_subclip) # to test
        print(f"    Extract from {start_subclip}s to {end_subclip}s")
        print(f"    Start from {start_in_final_clip}s")
        
        clip = original_clip.subclip(start_subclip, end_subclip).set_start(start_in_final_clip)
        clip=fx.all.fadeout(clip, padding, final_color=fade_color)
        clip=fx.all.fadein(clip, padding, initial_color=fade_color)
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
    clips = []
    
    total_time = 0
    for file in files_sorted(f'{csv_folder}/{csv_filter}.csv'):
        print(file)
        
        filename=os.path.basename(file).replace(".csv", "")
                   
        match = MatchPart.build_from_csv(f"{csv_folder}/{filename}.csv")
        highlights = [event for event in match.events if filter(event)]
        total_time = create_highights_clip(highlights, f"{video_folder}/{input_video_filename(filename)}.mp4", clips, total_time, duration_before, duration_after)
        
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
            video_folder=self.video_folder, 
            output_folder=self.output_folder,
            team_a=self.team_a, 
            team_b=self.team_b,
        )
        
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
        
        build_filename = lambda filename: f"{filename}.output"
        
        duration_before = 7
        duration_after = 2
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_slb", team_points, duration_before, duration_after, build_filename)
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_tous", points, duration_before, duration_after, build_filename)
        higlights(self.csv_folder, self.output_folder, self.output_folder, f"{self.root_name}_paniers_tous_les_points", all_points, duration_before, duration_after, build_filename)
    
    def display_by_quarter(self, stats):
 
        def compute_score(quarter, score):            
            last_quarter_score = stats[quarter-1].score if quarter > 1 else Score(0, 0)
            score_a = score.team_a-last_quarter_score.team_a
            score_b = score.team_b-last_quarter_score.team_b
            return Score(score_a, score_b)
        
        result = ""
        for (quarter, stat) in stats.items():
            result += f"{quarter}: " + f"{stat.score}".rjust(8)  + f" {compute_score(quarter, stat.score)}".rjust(10) + "\n"
            
        result = ""
        result += f"[%autowidth]\n|====\n"
        result += f"| Qt | A la fin | pendant \n"
        
        for (quarter, stat) in stats.items():
            result += f"| {quarter} |  {stat.score} | {compute_score(quarter, stat.score)}\n"
        result += f"|====\n"
            
        return result;
        
        
    def display_graph(self, infos):
        keep_when_score = []
        last_a = None
        last_b = None
        for info in infos:
            if info[1] != last_a or info[2] != last_b:
                keep_when_score.append(info)
            last_a=info[1]
            last_b=info[2]
                
        infos = keep_when_score
       
        scores = [b-a for (_,a,b,_,start_time,quarter_time) in infos]
        
        quarter_index = {}
        for (index, (_,_,_,_,_,quarter_time)) in enumerate(infos):
            quarter_index[quarter_time-1] = index
        
        formated_scores = "\n".join([f"{index}, {value}" for (index, value) in enumerate(scores)])
        delta_max=max(scores)
        delta_min=min(scores)
        print(f"delta_max: {delta_max}, delta_min: {delta_min}")
        
        scale_x=10
        scale_y=-5
       
        border_width=30
        margin_x=30
        height=440
        graph_x_0=border_width+margin_x
        graph_y_0=height/2+border_width
        
        
        result = """++++
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg"
width="700" height="500"     style="background-color:grey">
<style>
.graph {
    stroke:rgb(200,200,200);
    stroke-width:1;
}
.curve {
    fill:none;
    stroke-width:0.05;
    marker: url(#markerCircle);
    stroke:black;
}
</style>
"""
        result += f"""
<defs>
    <marker id="markerCircle" markerWidth="8" markerHeight="8" refX="5" refY="5">
        <circle cx="5" cy="5" r="0.02" style="stroke: none; fill:#000000;"/>
    </marker>
</defs>
<svg class="graph">
    <rect fill="white" width="640" height="440" x="30" y="30"/>
    <g class="grid">
        <line x1="{graph_x_0}" x2="{graph_x_0}" y1="440" y2="60"/>
    </g>
    <g class="grid">
        <line x1="{graph_x_0}" x2="640" y1="{graph_y_0}" y2="{graph_y_0}"/>
    </g>

    <text x="300" y="50" >Ecart de points</text>
"""

        for quarter in quarter_index.values():
            result += f"""<line x1="{graph_x_0+quarter*scale_x}" x2="{graph_x_0+quarter*scale_x}" y1="440" y2="60"/>"""
        

        result += f"""
    <line x1="{graph_x_0+quarter_index[1]*scale_x}" x2="{graph_x_0+quarter_index[1]*scale_x}" y1="440" y2="60"/>
        
    <text x="35" y="{graph_y_0+delta_max*scale_y+2}">{delta_max}</text>
    <line x1="56" x2="64" y1="{graph_y_0+delta_max*scale_y}" y2="{graph_y_0+delta_max*scale_y}"/>
    <text x="35" y="{graph_y_0+delta_min*scale_y+2}">{delta_min}</text>
    <line x1="56" x2="64" y1="{graph_y_0+delta_min*scale_y}" y2="{graph_y_0+delta_min*scale_y}"/>
    
    <text x="35" y="{graph_y_0+2}">0</text>
    <line x1="60" x2="60" y1="324" y2="328"/>
    <!-- text x="634" y="349"></text-->
    <line x1="639" x2="639" y1="324" y2="328"/>
</svg>
"""

        result += f"""
<polyline style="stroke:blue" class="curve" transform="translate({graph_x_0}, {graph_y_0}) scale({scale_x} {scale_y})" points="
    {formated_scores}
"/>

</svg>
++++
        """
        
        return result
    
    class PointStats:        
        def __init__(self):
            self.team_a = {1:0, 2:0, 3:0}
            self.team_b = {1:0, 2:0, 3:0}
            
        def add(self, record):
            if record.team == "A":
                self.team_a[record.points] += 1
            if record.team == "B":
                self.team_b[record.points] += 1
            
    class Stat:
        def __init__(self, score, points):
            self.score = score
            self.points = points
    
    def display_score(self):
        score = Score()
        
        infos = [(self.format_score(score), score.team_a, score.team_b, 0, 0, 1)]
        start_time = 0
        quarter_stats={}
        last_points = MatchVideo.PointStats() 
        for file in files_sorted(f'{self.csv_folder}/*.csv'):
            print(file)
            filename=os.path.basename(file).replace(".csv", "")
            extracted_infos = EventFile().extract_infos(f"{self.csv_folder}/{filename}.csv", score.team_a, score.team_b)
            infos += [(self.format_score(Score(info[0], info[1])), info[0], info[1], start_time+info[2], start_time+info[3], info[4]) for info in extracted_infos[1:]]
            
            (_,a,b,_,start_time,quarter_time) = infos[-1]
            
            for extracted in extracted_infos:
                last_points.add(extracted[5])
                
            score = Score(a, b)
            
            quarter_stats[quarter_time] = MatchVideo.Stat(score, last_points)
            
       
        output = "\n".join([f"{time}:".ljust(6) + f"{text}" + f" - {quarter_time} qt" for (text, _,_, time, _,quarter_time) in infos])
       
        result = ""
        result += self.display_by_quarter(quarter_stats)
        result += "\n\n"
        result += f"[%autowidth]\n|====\n"
        result += f"| Equipe | 1pt | 2pts | 3pts \n"
        result += f"| {self.team_a} |  {last_points.team_a[1]} | {last_points.team_a[2]} | {last_points.team_a[3]}\n"
        result += f"| {self.team_b} | {last_points.team_b[1]} | {last_points.team_b[2]} | {last_points.team_b[3]}\n"
        result += f"|====\n"
        
        result += "\n"
        result += self.display_graph(infos) 
        
        with (open(f"{self.root_folder}/stats.adoc", "w")) as stats_file:
            stats_file.write(result)
            
        print(result)
        return output

def extract_clips(video_file, clip_times, time_in_final_video = 0):
    clip_list = []

    for time in clip_times:
        video = mpy.VideoFileClip(video_file) 
        clip = video.subclip(time[0], time[1]).set_start(time_in_final_video)
        clip_list.append(clip)        
        time_in_final_video += clip.duration
    return clip_list
    
if __name__ == "__main__":
    args = sys.argv
    folder = args[2] if len(args) > 2 else "Match"
    match = MatchVideo(folder, "SLB", "TREILLIERES")
    if args[1] == "spike":
        match.csv_folder = f"{match.root_folder}/highlight"
        match.video_folder = f"{match.root_folder}/output"
        match.output_folder = f"{match.root_folder}/highlight"
        
        filter = lambda event: int(event.points) > 1
        filter = lambda event: True
        
        clip_list = extract_clips(f"{match.video_folder}/MatchTest_complet.mp4", [
            (1,4),
            (4,8),
            (1,4),
            ])
        
        output_folder = match.output_folder
        output_file = "MatchTest_extract"
        
        # total_time=0
        # final_clip_list = []
        # for clip in clip_list:
        #     print(total_time)
        #     final_clip_list.append(clip.set_start(total_time))
        #     total_time += clip.duration
        #     print(f"{clip.duration} {clip.s}" )
        #     final_clip_list.append(clip)
        # clip_list = final_clip_list
        
        padding=1
        fade_color=(30,30,30)
        clip_list = [fx.all.fadeout(clip, padding, final_color=fade_color) for clip in clip_list]
        clip_list = [fx.all.fadein(clip, padding, initial_color=fade_color) for clip in clip_list]
        
        
        clip = mpy.CompositeVideoClip(clip_list)
        
        
        
        clip.write_videofile(f"{output_folder}/{output_file}_x.mp4", threads=8, preset="veryfast")
        # higlights(match.csv_folder, match.video_folder, match.output_folder, f"{match.root_name}_highlight", filter, 
        #           duration_before=2, 
        #           duration_after=1,
        #           input_video_filename=lambda filename: f"{filename}")
       
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