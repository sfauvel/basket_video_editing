import re

from datetime import timedelta, datetime


def time_to_seconds(time):
  
    result = re.match(r'^(\d)+:\d\d$', time)
    if result == None:
        raise Exception(f"Invalid time: '{time}'")
    
    split = time.split(":")
    seconds = 0
    if len(split) >= 1:
        seconds += int(split[-1].replace("s",""))
    
    if len(split) >= 2:
        seconds += 60*int(split[-2])
    
    if len(split) >= 3:
        seconds += 60*60*int(split[-3])

    return int(seconds)
    
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
        records.append(EventRecord(0, "X", 0, quarter))
                
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
    
    def _seconds_to_string(self):
        minutes = int(self.time_in_seconds / 60)
        seconds = self.time_in_seconds % 60
        return f"{minutes}:{seconds:02d}"
        
    def to_csv(self):
        values = [str(self.points), self.team, self._seconds_to_string()]
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
