# To generate score in video

import os

import moviepy as mpy # type: ignore

from video_match import Score, MatchPart, MatchState

SB_LOGO_PATH = "../SLB_Logo_OK_light.jpg"
SCORE_FONT_SIZE = 50
TEAM_FONT_SIZE = 40
SHADOW_COLOR="rgb(23, 54, 93)"  # #17365d

def create_text_clip(text: str, font_size: int, color: str) -> mpy.TextClip:
    return mpy.TextClip(
                text,
                font="Charter-bold",
                color=color,
                kerning=4,
                fontsize=font_size,
            )

def position_left_from(clip: mpy.VideoClip, clip_from: mpy.VideoClip, margin_x: int, margin_y: int=0) -> mpy.VideoClip:
    from_right_pos = clip_from.pos(0)[0]
    return clip.set_position((from_right_pos-clip.size[0]-margin_x, margin_y))

def position_right_from(clip: mpy.VideoClip, clip_from: mpy.VideoClip, margin_x: int, margin_y: int=0) -> mpy.VideoClip:
    from_left_pos = clip_from.pos(0)[0]+clip_from.size[0]
    return clip.set_position((from_left_pos+margin_x, margin_y))

def center(clip: mpy.VideoClip, video_size: tuple[int, int]) -> mpy.VideoClip:
    return clip.set_position((video_size[0]/2-clip.size[0]/2, 0))
    
def create_score_clip(text: str, color: str="Yellow") -> mpy.TextClip:
    return create_text_clip(text, font_size=SCORE_FONT_SIZE, color=color)
    
def create_team_names(team_a: str, team_b: str, separator_clip: mpy.VideoClip) -> list[mpy.VideoClip]:
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
       
    
def set_shadow_position(clip: mpy.VideoClip, shadow_clip: mpy.VideoClip, delta: int=3) -> mpy.VideoClip:
    return shadow_clip.set_position((clip.pos(0)[0]+delta, clip.pos(0)[1]+delta))



# Get information from the file and insert the score to the video.
# Info should be in file [csv_folder]/[filename].csv.
# The original video is in [video_folder]/[filename].mp4.
# `a` and `b` represent the score at the beginning of the video.
# A video is generated in [output_folder]/[filename].output.mp4.
# The method return the score at the end of the video.
#
# If the output file already exists, is not regenerated 
# so we can stop the process and relaunch it to continue the execution.
def generate_from_video(filename: str, csv_folder: str, video_folder: str, output_folder: str, team_a: str, team_b: str, score: Score=Score(0,0)) -> Score:

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
        match_part: MatchPart = MatchPart.build_from_csv(csv_file, score)
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

def generate_score_clips(states: list[MatchState], team_a: str, team_b: str, size: tuple[int, int]) -> list[mpy.VideoClip]:
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