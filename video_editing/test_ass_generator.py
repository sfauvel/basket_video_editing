from doc_as_test_pytest import DocAsTest, doc, doc_module

from game_info import GameInfo
from ass_generator import AssGenerator

class TestAss:
    """
    ASS: https://fr.wikipedia.org/wiki/SubStation_Alpha[SubStation_Alpha]

    You can find information in https://github.com/libass/libass/wiki/ASS-File-Format-Guide[ASS-File-Format-Guide]
    """

    def test_header_section(self, doc): 
        ass = AssGenerator()
        doc.write("\n".join([
            "----",
            ass.header(),
            "----",]))


    def test_style_section(self, doc): 
        ass = AssGenerator()
        doc.write("\n".join([
            "----",
            ass.style(),
            "----",]))
        
    def test_event_section(self, doc): 
        duration_in_seconds=120
        team_local="SLB"
        team_visitor="NBH"
        quarter=2
        ass = AssGenerator(duration_in_seconds, team_local, team_visitor, quarter)
        doc.write("\n".join([
            "We generate an event section for:",
            "",    
            f"* a duration of *{duration_in_seconds}* seconds",
            f"* a local team *{team_local}*",
            f"* a visitor team *{team_visitor}*",
            f"* on quart *{quarter}*",
            "",
            "----",
            ass.events([]),
            "----",]))

#         
# Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding

# Style: TeamA,   Arial,14,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,222,8,0
# Style: TeamB,   Arial,14,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,222,0,8,0
# Style: Score,   Arial,20,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 8 ,0,0,5,0

# Style: ScoreA,   Arial,20,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,200,5,0
# Style: ScoreA1,  Arial,20,&H5500FFFF,&H55FFFF00,&H55303030,&HA0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,200,5,0
# Style: ScoreA2,  Arial,20,&H9900FFFF,&H99FFFF00,&H99303030,&HC0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,200,5,0
# Style: ScoreA3,  Arial,20,&HBB00FFFF,&HBBFFFF00,&HBB303030,&HF0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,200,5,0
# Style: ScoreA3,  Arial,20,&HDD00FFFF,&HDDFFFF00,&HDD303030,&HFD000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 9 ,0,200,5,0

# Style: ScoreB,   Arial,20,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,200,0,5,0
# Style: ScoreB1,  Arial,20,&H5500FFFF,&H55FFFF00,&H55303030,&HA0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,200,0,5,0
# Style: ScoreB2,  Arial,20,&H9900FFFF,&H99FFFF00,&H99303030,&HC0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,200,0,5,0
# Style: ScoreB3,  Arial,20,&HBB00FFFF,&HBBFFFF00,&HBB303030,&HF0000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,200,0,5,0
# Style: ScoreB3,  Arial,20,&HDD00FFFF,&HDDFFFF00,&HDD303030,&HFD000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 7 ,200,0,5,0

# Style: Quarter, Arial, 6,&H0000FFFF,&H00FFFF00,&H00303030,&H80000008,-1,0,0,0,100,100,0.00,0.00,1,1.00,2.00, 8 ,0,0,5,0

    def test_time_to_str(self, doc): 
        values = [0, 1, 60, 3600, 36000]
        doc.write("\n".join([
            "|====",
            "| Time in seconds | Ass time",
            "",
            "\n".join([f"| {time} | {AssGenerator.time_to_str(time)}" for time in values]),
            "|====",
            ]))