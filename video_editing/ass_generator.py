from typing import List, Tuple, Optional

class Alignement:
    LEFT=7
    CENTER=8
    RIGHT=9  
class Style:
    @staticmethod
    def text(name: str, fontsize: int,  primary_colour: str, secondary_colour: str, alignement: int, margin_l: int, margin_r: int, margin_v: int) -> "Style":
        return Style(
            name=name,
            fontname="Arial",
            fontsize=fontsize,
            primary_colour=f"&H00{primary_colour}",
            secondary_colour=f"&H00{secondary_colour}",
            
            alignment=alignement,
            margin_l=margin_l,
            margin_r=margin_r,
            margin_v=margin_v,
        )
    
    @staticmethod
    def header() -> str:
        return """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""      

    def __init__(self, 
            name: str = "Default",
            fontname: str = "Arial",
            fontsize: int = 20,
            primary_colour: str = "&H00FFFFFF",
            secondary_colour: str = "&H00FFFFFF",
            outline_colour: str = "&H00303030",
            back_colour: str = "&H80000008",
            bold: int = -1,
            italic: int = 0,
            underline: int = 0,
            strikeout: int = 0,
            scale_x: int = 100,
            scale_y: int = 100,
            spacing: float = 0.00,
            angle: float = 0.00,
            border_style: int = 1,
            outline: float = 1.00,
            shadow: float = 2.00,
            alignment: int = 2,
            margin_l: int = 10,
            margin_r: int = 10,
            margin_v: int = 10,
            encoding: int = 0) -> None:
        self.name = name
        self.fontname = fontname
        self.fontsize = fontsize
        self.primary_colour = primary_colour
        self.secondary_colour = secondary_colour
        self.outline_colour = outline_colour
        self.back_colour = back_colour
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.strikeout = strikeout
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.spacing = spacing
        self.angle = angle
        self.border_style = border_style
        self.outline = outline
        self.shadow = shadow
        self.alignment = alignment
        self.margin_l = margin_l
        self.margin_r = margin_r
        self.margin_v = margin_v
        self.encoding = encoding


    def __str__(self) -> str:
        return f"Style: {self.name:>7}, {self.fontname:>7},{self.fontsize:>2},{self.primary_colour},{self.secondary_colour},{self.outline_colour},{self.back_colour},{self.bold},{self.italic},{self.underline},{self.strikeout},{self.scale_x},{self.scale_y},{self.spacing},{self.angle},{self.border_style},{self.outline},{self.shadow},{self.alignment},{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}"

class Event:
 
    def __init__(self, style: str, text: str, layer: int = 1, start: int = 0, end: int = 0, name: str = "", marginl: int = 0, marginr: int = 0, marginv: int = 0, effect: str = "") -> None:
        self.layer = layer
        self.start = start
        self.end = end
        self.style = style
        self.name = name
        self.marginl = marginl
        self.marginr = marginr
        self.marginv = marginv
        self.effect = effect
        self.text = text

    @staticmethod
    def header() -> str: 
        return """[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""

    def __str__(self) -> str:
        return f"Dialogue: " + ",".join([
            str(self.layer),
            AssGenerator.time_to_str(self.start),
            AssGenerator.time_to_str(self.end),
            str(self.style),
            self.name,
            str(self.marginl),
            str(self.marginr),
            str(self.marginv),
            self.effect,
            self.text
        ])

import os
import re
from video_utils import files_sorted
class AssGenerator():

    @staticmethod
    def time_to_str(seconds: int) -> str:
        mm, ss = divmod(seconds, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d.00" % (hh, mm, ss)

    @staticmethod
    def insert_score(ass_folder: str, video_folder: str, output_folder: str) -> None: 
        
        os.makedirs(output_folder, exist_ok=True)

        for file in files_sorted(f'{ass_folder}/*.ass'):
            filename=re.sub(r"\.ass$", "", os.path.basename(file))
            print(filename)
            prog = f'ffmpeg -i {video_folder}/{filename}.mp4 -vf "ass={ass_folder}/{filename}.ass" -c:a copy -c:v libx265 -crf 28 {output_folder}/{filename}.mp4'
            print(prog)
            os.system(prog)

    def __init__(self, duration_in_seconds: int = 0, team_local: str = "LOCAL", team_visitor: str = "VISITOR", quarter: int = 1) -> None:
        self.duration_in_seconds = duration_in_seconds
        self.team_local = team_local
        self.team_visitor = team_visitor    
        self.quarter = quarter

    def header(self) -> str:
        return """[Script Info]
Title: Default Aegisub file
ScriptType: v4.00+"""


    def _code_style(self, name: str, alignment: int, margin_left: int, margin_right: int) -> str:
        def style_line(name: str, opacities: Tuple[str, str], alignment: int, margin_left: int, margin_right: int) -> str:
            (opacity1, opacity2) = opacities
            return f"Style: {name:>7},  Arial,20,&H{opacity1}00FFFF,&H{opacity1}FFFF00,&H{opacity1}303030,&H{opacity2}000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, {alignment} ,{margin_right},{margin_left},5,0"
        
        lines = [style_line(name, ("00", "80"), alignment, margin_left, margin_right)] + \
                [style_line(f"{name}{index+1}", opacities, alignment, margin_left, margin_right) 
                    for (index, opacities) in enumerate([("55", "A0"), ("99", "C0"), ("BB", "F0"), ("DD", "FD")])]
            
        return "\n".join(lines)

    def style(self) -> str:
        return "\n".join([
            Style.header(),
            str(Style.text("TeamA",  14, "FFFFFF", "FFFFFF", Alignement.RIGHT, 0, 222, 8)),
            str(Style.text("TeamB",  14, "FFFFFF", "FFFFFF", Alignement.LEFT, 222, 0, 8)),
            str(Style.text("Quarter", 6, "00FFFF", "FFFF00", Alignement.CENTER, 0, 0, 5)),
            str(Style.text("Score",  20, "00FFFF", "FFFF00", Alignement.CENTER, 0, 0, 5)),
            "",
            self._code_style("ScoreA", 9, 200, 0),
            "",
            self._code_style("ScoreB", 7, 0, 200)  
        ])
    
    def events(self, events: List[Event]) -> str:
        for event in events:
            pass

        events_str = "\n".join([str(event) for event in events])
        return "\n".join([
            Event.header(),
            events_str + "\n" if len(events) > 0 else "",
            str(Event(end=self.duration_in_seconds, style="Score", text="-")),
            str(Event(end=self.duration_in_seconds, style="TeamA", text=self.team_local)),
            str(Event(end=self.duration_in_seconds, style="TeamB", text=self.team_visitor)),
            str(Event(end=self.duration_in_seconds, style="Quarter", text=str(self.quarter), layer=2)),
        ])
    
    def generate(self, events: List[Event]) -> str:
        return "\n\n".join([
            self.header(),
            self.style(),
            self.events(events)
        ])