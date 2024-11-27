

import os
import shutil
import unittest

from video_recorder import *
from video_match import *
from video_utils import *
from video_generator import collapse_overlaps


class TestEventRecord(unittest.TestCase):
    def test_event_record_to_csv(self):
        assert "3;A;0:00:12;2" == EventRecord(3, "A", 12, 2).to_csv()
        assert "3;A;0:00:02;2" == EventRecord(3, "A", 2, 2).to_csv(), EventRecord(3, "A", 2, 2).to_csv()
        
    def test_event_record_to_csv_with_minutes(self):
        assert "3;A;0:02:12;2" == EventRecord(3, "A", 132, 2).to_csv()
        
    def test_event_record_to_csv_without_quarter(self):
        assert "3;A;0:00:12" == EventRecord(3, "A", 12, None).to_csv()

    def test_event_record_from_csv(self):
        record = EventRecord.from_csv("3;A;0:12;2")
        assert 3 == record.points
        assert "A" == record.team
        assert 12 == record.time_in_seconds
        assert 2 == record.quarter_time

    def test_event_record_from_csv_without_quarter(self):
        record = EventRecord.from_csv("3;A;0:12")
        assert None == record.quarter_time
        
    def test_event_record_from_csv_with_time_in_minutes(self):
        record = EventRecord.from_csv("3;A;4:25;2")
        assert 4*60+25 == record.time_in_seconds
        
    def test_event_record_from_csv_with_time_in_minutes(self):
        try:
            record = EventRecord.from_csv("3;A;4:25m:s")
        except:
            return
        assert False, "An exception should be thrown"
        
    
    def test_event_record_from_csv_with_time_with_hour(self):
        record = EventRecord.from_csv("3;A;0:04:25;2")
        assert 4*60+25 == record.time_in_seconds
        
    def test_event_record_validation_ok(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([
                "0;-;0:00;4",
                "2;A;0:25;4",
                "0;-;1:00;4",
                ]))
            
        (result, valid) = EventRecord.validate("tmp")
        assert valid == True
        assert "tmp1.csv: Ok" in result, result
        
    def test_event_record_invalid(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([
                "0;-;0:00;4",
                "2;A;25;4",
                "0;-;1:00;4",
                ]))
            
        (result, valid) = EventRecord.validate("tmp")
        assert valid ==False
        assert "tmp1.csv: Invalid" in result, result
        assert "- Line 2: 2;A;25;4" in result, result
        
        
    def test_event_record_show_all_invalid_lines(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([
                "0;-;0:00;4",
                "2;A;25;4",
                "2;A;1:43;4",
                "2;A;56;4",
                "0;-;1:00;4",
                ]))
        with (open("tmp/tmp2.csv", "w")) as csv_file:
            csv_file.write("\n".join([
                "0;-;0:00;4",
                "2;B;12;4",
                "0;-;1:00;4",
                ]))
            
        (result, valid) = EventRecord.validate("tmp")
        assert valid ==False
        assert "tmp1.csv: Invalid" in result, result
        assert "- Line 2: 2;A;25;4" in result, result
        assert "- Line 4: 2;A;56;4" in result, result
        assert "tmp2.csv: Invalid" in result, result
        assert "- Line 2: 2;B;12;4" in result, result
        
    def test_event_record_when_time_is_not_well_ordered(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([
                "0;-;0:00;4",
                "2;A;1:25;4",
                "2;B;1:10;4",
                "0;-;1:00;4",
                ]))
            
        (result, valid) = EventRecord.validate("tmp")
        assert valid ==False
        assert "tmp1.csv: Invalid" in result, result
        assert "- Line 3: 2;B;1:10;4 -- Time should not be less than 0:01:10" in result, result
  
class TestVideoGenerator(unittest.TestCase):

    def test_build_match_part_from_csv(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        match_part = MatchPart.build_from_csv("tmp/tmp1.csv")
                
        states = match_part.states()
        
        assert states[0].start == 0
        assert states[0].end == 5
        assert states[0].score.team_a == 0
        assert states[0].score.team_b == 0

        assert states[1].start == 5
        assert states[1].end == 6
        assert states[1].score.team_a == 2
        assert states[1].score.team_b == 0
        
    
    def test_build_match_part_from_csv_with_initial_score(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            print("\n".join([e.to_csv() for e in events]))
            
        match_part = MatchPart.build_from_csv("tmp/tmp1.csv", Score(5,3))
                
        states = match_part.states()
        
        assert states[0].start == 0
        assert states[0].end == 5
        assert states[0].score.team_a == 5
        assert states[0].score.team_b == 3

        assert states[1].start == 5
        assert states[1].end == 6
        assert states[1].score.team_a == 7
        assert states[1].score.team_b == 3
        
    def test_extract_infos(self):
        infos = EventFile().extract_lines_infos([
            "2;A;0:03;3",
            "1;B;0:05;3",
            "3;A;0:07;3",
            "0;A;0:10;3",
        ], 0, 0, 0)
        assert infos[0] == (0, 0, 0, 3, EventRecord.from_csv("2;A;0:03;3"))
        assert infos[1] == (2, 0, 3, 5, EventRecord.from_csv("1;B;0:05;3"))
        assert infos[2] == (2, 1, 5, 7, EventRecord.from_csv("3;A;0:07;3"))
        assert infos[3] == (5, 1, 7, 10, EventRecord.from_csv("0;A;0:10;3"))
        assert len(infos) == 4
        
    def test_extract_infos_with_several_formats_with_an_initial_score_and_time(self):
        infos = EventFile().extract_lines_infos([
            "2;A;0:03;4",
            "0;A;0:08;4",
        ], 5, 8, 10)
        
        assert infos[0] == (5, 8, 10, 13, EventRecord.from_csv("2;A;0:03;4")), infos[0]
        assert infos[1] == (7, 8, 13, 18, EventRecord.from_csv("0;A;0:08;4")), infos[1]

    def test_extract_match_events_can_read_event_without_team(self):
        match_events = EventFile().extract_match_events([
            "0;;0:00",
            "2;A;0:03",
            "1;B;0:05",
            "3;A;0:07",
            "0;;0:10",
        ])
        assert match_events.events[0].time_in_seconds == 0
        assert match_events.events[0].points == 0
        assert match_events.events[0].team == ""
    
        assert match_events.events[-1].time_in_seconds == 10
        assert match_events.events[-1].points == 0
        assert match_events.events[-1].team == ""

    def test_extract_match_events(self):
        match_events = EventFile().extract_match_events([
            "0;X;0:00",
            "2;A;0:03",
            "1;B;0:05",
            "3;A;0:07",
            "0;A;0:10",
        ])
        assert match_events.start == 0
        assert match_events.end == 10
        assert match_events.events[0].time_in_seconds == 0
        assert match_events.events[0].points == 0
        assert match_events.events[0].team == "X"
        assert match_events.events[0].quarter_time == None
        
        assert match_events.events[1].time_in_seconds == 3
        assert match_events.events[1].points == 2
        assert match_events.events[1].team == "A"
        assert match_events.events[1].quarter_time == None
        
    
    def test_extract_match_states(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states()
        print(f"States: {states}")
        for state in states:
            print(f"State: {state}")
        
        assert states[0].start == 0
        assert states[0].end == 3
        assert states[0].score.team_a == 0
        assert states[0].score.team_b == 0
        assert states[0].quarter_time == None

        assert states[1].start == 3
        assert states[1].end == 5
        assert states[1].score.team_a == 2
        assert states[1].score.team_b == 0
        assert states[1].quarter_time == 2
    
    def test_extract_match_states_with_a_first_event(self):
        match_events = EventFile().extract_match_events([
            "0;X;0:00;1",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states()
        
        assert states[0].start == 0
        assert states[0].end == 0
        assert states[0].quarter_time == None

        assert states[1].start == 0
        assert states[1].end == 5
        assert states[1].score.team_a == 0
        assert states[1].score.team_b == 0
        assert states[1].quarter_time == 1
        
    def test_extract_match_states_compute_score(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states()
        
        assert states[0].score.team_a == 0
        assert states[0].score.team_b == 0
        
        assert states[1].score.team_a == 2
        assert states[1].score.team_b == 0

        assert states[2].score.team_a == 2
        assert states[2].score.team_b == 1
        
        
    def test_extract_match_states_with_initial_values(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ], initial_score=Score(6,3))
        
        states = match_events.states()
        
        assert states[0].score.team_a == 6
        assert states[0].score.team_b == 3
        
        assert states[1].score.team_a == 8
        assert states[1].score.team_b == 3

        assert states[2].score.team_a == 8
        assert states[2].score.team_b == 4
        
    def test_extract_match_states_last_state(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states()
        
        assert states[-1].start == 7
        assert states[-1].end == 10
        assert states[-1].score.team_a == 5
        assert states[-1].score.team_b == 1
        assert states[-1].quarter_time == 2
    
    
    def test_extract_match_states_align_to_the_time(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states(15)
        
        assert states[-1].start == 7
        assert states[-1].end == 15
    
    
    def test_extract_match_states_cut_last_state_if_not_in_time(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ])
        states = match_events.states(6)
        
        assert states[-1].start == 5
        assert states[-1].end == 6
        
    def test_extract_match_final_score(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "3;A;0:07;2",
            "0;A;0:10;2",
        ], initial_score=Score(20, 10))
        
        final_score = match_events.final_score()
        assert final_score.team_a == 25
        assert final_score.team_b == 11
    
    def test_collapse_overlap_without_overlap(self):
        events = EventFile().extract_match_events([
            "2;A;0:13;2",
            "1;B;0:25;2",
            "3;A;0:37;2",
            "0;-;0:50;2",
        ])
        
        assert collapse_overlaps(events.events, 5, 3) == [(8, 16), (20, 28), (32, 40), (45, 53)], collapse_overlaps(events.events, 5, 3)
        
    
    def test_collapse_overlap_with_overlap(self):
        events = EventFile().extract_match_events([
            "2;A;0:13;2",
            "1;B;0:25;2",
            "3;A;0:28;2",  # Overlap
            "0;-;0:50;2",
        ])
        
        assert collapse_overlaps(events.events, 5, 3) == [(8, 16), (20, 31), (45, 53)], collapse_overlaps(events.events, 5, 3)
        
    
    def test_collapse_overlap_first_event_before_0(self):
        events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:25;2",
        ])
        
        assert collapse_overlaps(events.events, 5, 3) == [(0, 6), (20, 28)], collapse_overlaps(events.events, 5, 3)


    def test_build_match_sheet_with_A_score(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
        ])
        
        assert match_events.game_sheet() == "\n".join([
            "              1              ",
            "0:00:03 (+2)  2              ",
        ]), "\n"+str(match_events.game_sheet())
        
    def test_build_match_sheet_with_B_score(self):
        match_events = EventFile().extract_match_events([
            "2;B;0:03;2",
        ])
        
        assert match_events.game_sheet() == "\n".join([
            "              1              ",
            "              2  (+2) 0:00:03",
        ]), "\n"+str(match_events.game_sheet())
        
        
    def test_build_match_sheet_with_some_scores(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:13;2",
            "1;B;0:25;2",
            "3;A;0:37;2",
        ])
        
        assert match_events.game_sheet() == "\n".join([
            "              1  (+1) 0:00:25",
            "0:00:13 (+2)  2              ",
            "              3              ",
            "              4              ",
            "0:00:37 (+3)  5              ",
        ]), "\n"+str(match_events.game_sheet())
        
    def test_build_match_sheet_start_at(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
        ])
        
        assert match_events.game_sheet(5) == "\n".join([
            "              6              ",
            "0:00:03 (+2)  7              ",
        ]), "\n"+str(match_events.game_sheet())
        
        
    def test_build_match_sheet_should_not_add_when_no_points(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "0;-;0:04;2",
            "1;B;0:05;2",
        ])
        assert match_events.game_sheet() == "\n".join([
            "              1  (+1) 0:00:05",
            "0:00:03 (+2)  2              ",
        ]), "\n"+str(match_events.game_sheet())
        
    def test_build_match_sheet_with_several_match_part(self):
        match_events_1= EventFile().extract_match_events([
            "2;A;0:03;2",
            "1;B;0:05;2",
            "0;-;0:10;2",
        ])
        match_events_2 = EventFile().extract_match_events([
            "3;A;0:02;2",
            "3;B;0:04;2",
            "2;B;0:06;2",
        ])
        game_sheet=MatchPart.game_sheet_multi_part([match_events_1, match_events_2])
        assert str(game_sheet) == "\n".join([
            "              1  (+1) 0:00:05",
            "0:00:03 (+2)  2              ",
            "              3              ",
            "              4  (+3) 0:00:14",
            "0:00:12 (+3)  5              ",
            "              6  (+2) 0:00:16",
        ]), "\n"+str(game_sheet)
        
    def test_build_match_sheet_with_several_match_part_should_add_1_second_each_2_files(self):
        match_events_1= EventFile().extract_match_events([
            "1;A;0:03;2",
        ])
        match_events_2 = EventFile().extract_match_events([
            "1;A;0:03;2",
        ])
        match_events_3 = EventFile().extract_match_events([
            "1;A;0:03;2",
        ])
        game_sheet=MatchPart.game_sheet_multi_part([match_events_1, match_events_2, match_events_3])
        assert str(game_sheet) == "\n".join([
            "0:00:03 (+1)  1              ",
            "0:00:06 (+1)  2              ",
            "0:00:10 (+1)  3              ",
        ]), "\n"+str(game_sheet)
        
    def test_build_match_display(self):
        match_events = EventFile().extract_match_events([
            "2;A;0:03;2",
            "0;-;0:04;2",
            "1;B;0:05;2",
        ])
        display = match_events.display("TEAM A", "TEAM B") 
        assert display == "\n".join([
            "0:00:03   +2  TEAM A   2 - 0   TEAM B      (2)   2 qt",
            "0:00:05       TEAM A   2 - 1   TEAM B  +1  (1)   2 qt",
        ]), "\n"+display
        
    def test_score_by_quarter(self):
        by_quarter = EventFile().extract_match_events([
            "2;A;0:03;1",
            "0;-;0:04;1",
            "1;B;0:05;1",
            "2;B;0:06;2",
            "3;A;0:07;2",
            "1;A;0:08;3",
        ]).score_by_quarter()
        
        assert Score(2,1) == Score(2,1) 
        assert by_quarter[1] == Score(2,1), f"quarter 1 => {by_quarter[1]}"
        assert by_quarter[2] == Score(3,2), f"quarter 2 => {by_quarter[2]}"
        assert by_quarter[3] == Score(1,0), f"quarter 3 => {by_quarter[3]}"
        assert 4 not in by_quarter, f"quarter 4 => {by_quarter[4]}"
    
    def test_score_equality(self):
        assert Score(2,1) == Score(2,1) 
        assert Score(2,4) != Score(2,1) 
        assert Score(5,1) != Score(2,1) 
         
        
if __name__ == "__main__":
    unittest.main()