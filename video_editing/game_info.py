from typing import Self

class GameInfo():
    FILENAME = "info.txt"

    def __init__(self, date: str, locaux: str, visiteurs: str) -> None:
        self.date = date
        self.locaux = locaux
        self.visiteurs = visiteurs

    @classmethod
    def load(cls, filepath: str) -> Self:
        with open(filepath, "r") as file:
            lines = file.readlines()

        data = {line[0].strip().lower(): line[1].strip() for line in [line.split(":") for line in lines]}
        print(data)
        
        return cls(data["date"], data["locaux"], data["visiteurs"])