

class GameInfo():
    FILENAME = "info.txt"

    def __init__(self, date, locaux, visiteurs):
        self.date = date
        self.locaux = locaux
        self.visiteurs = visiteurs

    def load(filepath):
        with open(filepath, "r") as file:
            lines = file.readlines()

        data = {line[0].strip().lower(): line[1].strip() for line in [line.split(":") for line in lines]}
        print(data)
        
        return GameInfo(data["date"], data["locaux"], data["visiteurs"])