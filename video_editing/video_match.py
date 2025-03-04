# Structure to manage a match

from video_recorder import EventRecord
from video_utils import *

def read_content_of_file(file): 
    with open(file, "r") as input_file:
        return input_file.readlines()

     
class Score:
    def __init__(self, team_a = 0, team_b = 0):
        self.team_a = team_a
        self.team_b = team_b
        
    def add(self, points, team):
        if (team == "A"):
            return Score(self.team_a+points, self.team_b)
        else:
            return Score(self.team_a, self.team_b+points)
        
    def __str__(self) -> str:
        return f"{self.team_a} - {self.team_b}"
    
    def __eq__(self, other):
        return isinstance(other, Score) \
            and self.team_a == other.team_a \
            and self.team_b == other.team_b

class MatchEvent:
    def __init__(self, start_time, end_time):
        self.start = start_time
        self.end = end_time
        self.quarter_time = None
        self.points = None

"""A state is defined by all can be change during the game.
It's defined for a period of time.
"""
class MatchState:
    def __init__(self, start, end, score, quarter_time):
        self.start=start
        self.end=end
        self.score=score
        self.quarter_time=quarter_time

    def __str__(self) -> str:
        return f"start={self.start}, end={self.end}, score={self.score}, quarter_time={self.quarter_time}"

    
class MatchPart:
    def build_from_csv(csv_file, score=Score(0,0)):
        content = read_content_of_file(csv_file)
        events = [EventRecord.from_csv(line) for line in content if line.strip() != ""]
            
        return MatchPart(0, 0, events, score)
    
    def __init__(self, start_time, end_time, events, score=Score(0,0)):
        self.start = start_time
        self.end = end_time
        self.events = events
        self.initial_score = score
        
    def final_score(self):
        score = self.initial_score
        for event in self.events:
            score = score.add(event.points, event.team)
        return score
        
    def states(self, full_time=None):
        initial_state = MatchState(0, 0, self.initial_score, None)
        states = []
        current_state = initial_state
        for event in self.events:
            current_state.end = event.time_in_seconds
            
            states.append(current_state)
            if full_time != None and current_state.end > full_time:
                current_state.end = full_time
                return states

            current_state = MatchState(current_state.end, current_state.end, current_state.score.add(event.points, event.team), event.quarter_time)
        
        if full_time != None:
            states[-1].end = full_time
        return states 
    
    def concat_match_parts(parts):
        def adjust_time(event, start_time):
            event.time_in_seconds += start_time
            return event
        
        match=MatchPart(0, 0, [])
        last_time=0
        is_even = False
        for part in parts:
            match.events += [adjust_time(event, last_time) for event in part.events]
            last_time = match.events[-1].time_in_seconds + (1 if is_even else 0)
            is_even = not is_even
            
        return match
    
    def game_sheet(self, start_point=0):
        scoreA=[]
        scoreB=[]
        for event in [event for event in self.events if event.points > 0]:
            score_to_append = scoreA if event.team == "A" else scoreB
            score_to_append += [None] * (event.points-1)
            score_to_append += [(event.points, seconds_to_time(event.time_in_seconds))]

        empty_score="              "
        lines=[]
        points=0
        for i in range(max(len(scoreA), len(scoreB))):
            a = f"{scoreA[i][1]} (+{scoreA[i][0]})  " if i < len(scoreA) and scoreA[i] != None else empty_score 
            b = f"  (+{scoreB[i][0]}) {scoreB[i][1]}" if i < len(scoreB) and scoreB[i] != None else empty_score 
            
            points=i+1+start_point
            lines.append(f"{a}{points}{b}")
        return "\n".join(lines)

    def game_sheet_multi_part(parts):        
        return MatchPart.concat_match_parts(parts).game_sheet()

    def display(self, team_a, team_b):
        def format_score(score):
            return f"{team_a} {str(score.team_a).rjust(3)} - {str(score.team_b).ljust(3)} {team_b} "
        
        def max_length(events):
            score = Score(0,0)
            max_text_length=0
            for event in [event for event in events if event.points > 0]:
                score = score.add(event.points, event.team)
                max_text_length = max(max_text_length, len(format_score(score)))
            return max_text_length
                  
        max_text_length = max_length(self.events)
        
        lines=[]
        score = Score(0,0)
        for event in [event for event in self.events if event.points > 0]:
            score = score.add(event.points, event.team)
            
            point_a = f"+{event.points}" if event.team == "A" else ""
            point_b = f"+{event.points}" if event.team == "B" else ""
            line = f"{seconds_to_time(event.time_in_seconds)}".ljust(10) + f"{point_a}".ljust(4) + f"{format_score(score)}".ljust(max_text_length+1) + f"{point_b}".ljust(4) + f"({score.team_a-score.team_b})".ljust(6) + f"{event.quarter_time} qt"
      
            lines.append(line)
            
        return "\n".join(lines)
    
    def score_by_quarter(self):
        scores = {}
        for event in [event for event in self.events if event.points > 0]:
            quarter = event.quarter_time
            if not quarter in scores:
                scores[quarter] = Score(0,0)
            scores[quarter] = scores[quarter].add(event.points, event.team)
                
        return scores

class EventFile:
    
    def extract_lines_infos(self, lines, a, b, initial_start_time):
        infos = []
        score = Score(a, b)
        start_time = initial_start_time
        for line in lines:
            record = EventRecord.from_csv(line)
            points = record.points
            team = record.team
            end_time = record.time_in_seconds + initial_start_time
            
            infos.append((a, b, start_time, end_time, record))
                       
            score = score.add(points, team)
            a = score.team_a
            b = score.team_b
            start_time = end_time
                
        return infos

    def extract_match_events(self, lines, initial_score=Score(0,0)) -> MatchPart:
        start_time = 0
        end_time = 0
        events = []
        for line in lines:
            record = EventRecord.from_csv(line)
            end_time = record.time_in_seconds
            events.append(record)
            start_time = end_time
        
        return MatchPart(0, end_time, events, score=initial_score)
    
    # Generate information to insert in the video
    def extract_infos(self, input_name, a, b, start_time=0):
        infos=[]
        with open(input_name, "r") as input_file:
            lines = input_file.readlines()
            return self.extract_lines_infos(lines, a, b, start_time)
    
