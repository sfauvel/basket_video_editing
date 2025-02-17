# A command line tool to record events during a game and generate a csv file.
# It's the equivalent to a score board used during a game.
# You can launch it and watching a video at the same time to record event as they happen. 

import glob
import re

from datetime import timedelta, datetime
from video_utils import time_to_seconds, seconds_to_time

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

        score = (0,0)
        records=[]
       
        quarter = self.ask_quarter()
        records.append(EventRecord(0, "-", 0, quarter))
                
        while True:
            print("Tapez 'ENTRER' au prochain panier ou 'e' pour finir...")
            x = input()
            
            next_time = datetime.now()-start_time
            if x == "e":
                records.append(EventRecord(0, "-", round(timedelta.total_seconds(next_time)), quarter))
                break

            (points, team) = self.wait_for_points()
            
            score = (score[0]+points, score[1]) if team.upper() == "A" else (score[0], score[1]+points)

            print(f'{team} +{points} => {score[0]} - {score[1]} | {str(next_time).split(".")[0]}')
            records.append(EventRecord(points, team, round(timedelta.total_seconds(next_time)), quarter))
        
        print(f"Score final: {score[0]} - {score[1]}")
        
        output = "\n".join([r.to_csv() for r in records])
        with open(filename, "w") as output_file:
            output_file.write(output)
        
        print(f"File {filename} generated")
        return score
    

"""Information from a record in csv file.
"""
class EventRecord:
    def __init__(self, points, team, time_in_seconds, quarter_time=None):
        self.points = points
        self.team = team
        self.time_in_seconds = time_in_seconds
        self.quarter_time = quarter_time
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    
    # !! Duplicated from video_generator
    def files_sorted(pattern):
        files = glob.glob(pattern)
        files.sort()
        return files 

    # !! Duplicated from video_match
    def read_content_of_file(file): 
        with open(file, "r") as input_file:
            return input_file.readlines()


    def _validate_csv_file(file):
        content = EventRecord.read_content_of_file(file)
        is_valid = True
        result = ""
        last_time = 0
        for line_number, line in enumerate(content, start=1):
            line = line.strip()
            try:
                event = EventRecord.from_csv(line)
                if event.time_in_seconds < last_time:
                     result += f"- Line {line_number}: {line} -- Time should not be less than {EventRecord._seconds_to_string(event.time_in_seconds)}"
                     print(f"Invalid: {result}")
                     is_valid = False
                last_time = event.time_in_seconds
            except:
                result += f"- Line {line_number}: {line} -- Line is not well formatted"
                print(f"Invalid: {result}")
                is_valid = False
        
        return (f"{file}: " + ("Ok" if is_valid else "Invalid") + "\n" + result, is_valid)
        
    
    def validate(csv_folder):
        files = EventRecord.files_sorted(f"{csv_folder}/*.csv")
        
        results = [EventRecord._validate_csv_file(file) for file in files]
        
        is_valid = all(is_valid for (_, is_valid) in results)
        return ("\n".join([result for (result, is_valid) in results]), is_valid)
    
    def _seconds_to_string(time_in_seconds):
        return seconds_to_time(time_in_seconds)
        # minutes = int(time_in_seconds / 60)
        # seconds = time_in_seconds % 60
        # return f"{minutes}:{seconds:02d}"
        
    def to_csv(self):
        values = [str(self.points), self.team, EventRecord._seconds_to_string(self.time_in_seconds)]
        if self.quarter_time:
            values.append(str(self.quarter_time))
        return ";".join(values)
    
    def from_csv(csv):
        split = csv.split(";")
        print(split)
        quarter = int(split[3]) if len(split) > 3 else None 
        return EventRecord(int(split[0]), split[1], time_to_seconds(split[2]), quarter) 

    def __str__(self) -> str:
        return f"points:{self.points}, team:{self.team}, time_in_seconds:{self.time_in_seconds}, quarter_time:{self.quarter_time}"

if __name__ == "__main__":
    Recorder().record_input("tmp/output.csv")