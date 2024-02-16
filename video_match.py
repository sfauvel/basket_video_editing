import re

def read_content_of_file(file): 
    with open(file, "r") as input_file:
        return input_file.readlines()

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
    

"""Information from a record in csv file.
"""
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
        split = csv.split(";")
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
        
    def __str__(self) -> str:
        return f"{self.team_a} - {self.team_b}"

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
        events = [EventRecord.from_csv(line) for line in content]
            
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
            
            infos.append((a, b, start_time, end_time))
                       
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
    
