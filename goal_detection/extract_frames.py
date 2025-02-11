import re
import sys

def generate_part(frames, margin):
    parts = []
    for (frame, time) in frames:
        from_frame = max(0, frame-margin)
        to_frame = frame+margin
        if len(parts) > 0 and from_frame <= parts[-1][1]:
            parts[-1] = (parts[-1][0], to_frame, parts[-1][2])
        else:
            parts.append((from_frame, to_frame, time))
    return parts

def generate_sequence_file(parts):
    """Generate a command line to extract the video sequence and display time information in video"""
    return "\n".join([f"echo -e \"1\\n00:00:00,000 --> 10:00:00,000\\n{part[2]} {part[0]}:{part[1]}\" > subtitle.srt;ffmpeg -i $INPUT -vf \"trim=start_frame={part[0]}:end_frame={part[1]},setpts=PTS-STARTPTS,subtitles=subtitle.srt:force_style='alignment=1'\" -an output_{part[0]}_{part[1]}.mp4" for part in parts])
        
def file_list(parts):
    """Generate a list of files to concatenate"""
    return "\n".join([f"file 'output_{part[0]}_{part[1]}.mp4'" for part in parts])
    
def generate_csv(parts):
    """Generate the csv file to be used in video reader"""
    return "\n".join([f"0;?;{part[2]};0" for part in parts])
    
def extract_frames(filename):
    """Extract information produce by 'detection.py' script"""
    def extract_frame_from_line(line):
        found = re.search(r'Frame: (\d+) Time: (.*)', line.strip())
        return (int(found.group(1)), found.group(2))
        
    # lit le fichier et garde les lignes commencant par "Frame"
    with open(frame_file, 'r') as f:
        lines = f.readlines()
        # extrait le numero de frame de la ligne avec une regexp
        frames = [extract_frame_from_line(line) for line in lines if line.startswith("Frame")]
        return frames

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 extract_frames.py <frames_file>")
        sys.exit(1)

    frame_file = sys.argv[1]
    frames = extract_frames(frame_file)
    
    parts = generate_part(frames, 30)
    
    # print(f"echo -e \"{file_list(parts)}\" > files_to_concat.txt")
    # print("")
    # print(generate_sequence_file(parts))
        
        
    print(generate_csv(parts))
    