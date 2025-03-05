class Alignement:
    LEFT=7
    CENTER=8
    RIGHT=9  
class Style:
    @staticmethod
    def text(name, fontsize,  primary_colour, secondary_colour, alignement, margin_l, margin_r, margin_v):
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
    def header():
        return """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
"""      

    def __init__(self, 
            name="Default",
            fontname="Arial",
            fontsize=20,
            primary_colour="&H00FFFFFF",
            secondary_colour="&H00FFFFFF",
            outline_colour="&H00303030",
            back_colour="&H80000008",
            bold=-1,
            italic=0,
            underline=0,
            strikeout=0,
            scale_x=100,
            scale_y=100,
            spacing=0.00,
            angle=0.00,
            border_style=1,
            outline=1.00,
            shadow=2.00,
            alignment=2,
            margin_l=10,
            margin_r=10,
            margin_v=10,
            encoding=0):
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


    def __str__(self):
        return f"Style: {self.name:>7}, {self.fontname:>7},{self.fontsize:>2},{self.primary_colour},{self.secondary_colour},{self.outline_colour},{self.back_colour},{self.bold},{self.italic},{self.underline},{self.strikeout},{self.scale_x},{self.scale_y},{self.spacing},{self.angle},{self.border_style},{self.outline},{self.shadow},{self.alignment},{self.margin_l},{self.margin_r},{self.margin_v},{self.encoding}"

class Event:
 
    def __init__(self, style, text, layer=1, start=0, end=0, name="", marginl=0, marginr=0, marginv=0, effect=""):
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
    def header(): 
        return """[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""

    def __str__(self):
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

class AssGenerator():

    def time_to_str(seconds):
        mm, ss = divmod(seconds, 60)
        hh, mm = divmod(mm, 60)
        return "%d:%02d:%02d.00" % (hh, mm, ss)

    def __init__(self, duration_in_seconds=0, team_local="LOCAL", team_visitor="VISITOR", quarter = 1):
        self.duration_in_seconds = duration_in_seconds
        self.team_local = team_local
        self.team_visitor = team_visitor    
        self.quarter = quarter

    def header(self):
        return """[Script Info]
Title: Default Aegisub file
ScriptType: v4.00+"""


    def _code_style(self, name, alignment, margin_left, margin_right):
        def style_line(name, opacities, alignment, margin_left, margin_right):
            (opacity1, opacity2) = opacities
            return f"Style: {name:>7},  Arial,20,&H{opacity1}00FFFF,&H{opacity1}FFFF00,&H{opacity1}303030,&H{opacity2}000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, {alignment} ,{margin_right},{margin_left},5,0"
        
        lines = [style_line(name, ("00", "80"), alignment, margin_left, margin_right)] + \
                [style_line(f"{name}{index+1}", opacities, alignment, margin_left, margin_right) 
                    for (index, opacities) in enumerate([("55", "A0"), ("99", "C0"), ("BB", "F0"), ("DD", "FD")])]
            
        return "\n".join(lines)

    def style(self):
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
    
    def events(self, events):
        for event in events:
            pass

        return "\n".join([
            Event.header(),
            "",
            str(Event(end=self.duration_in_seconds, style="Score", text="-")),
            str(Event(end=self.duration_in_seconds, style="TeamA", text=self.team_local)),
            str(Event(end=self.duration_in_seconds, style="TeamB", text=self.team_visitor)),
            str(Event(end=self.duration_in_seconds, style="Quarter", text=str(self.quarter), layer=2)),
        ])
    
