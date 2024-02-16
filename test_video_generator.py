

import os
import shutil
import unittest

#from video_generator import *
from video_match import *

class TestEventRecord(unittest.TestCase):
    def test_event_record_to_csv(self):
        assert "3;A;12;2" == EventRecord(3, "A", 12, 2).to_csv()
        
    def test_event_record_to_csv_without_quarter(self):
        assert "3;A;12" == EventRecord(3, "A", 12, None).to_csv()

    def test_event_record_from_csv(self):
        record = EventRecord.from_csv("3;A;12;2")
        assert 3 == record.points
        assert "A" == record.team
        assert 12 == record.time_in_seconds
        assert 2 == record.quarter_time

    def test_event_record_from_csv_without_quarter(self):
        record = EventRecord.from_csv("3;A;12")
        assert None == record.quarter_time
        
    def test_event_record_from_csv_with_time_in_minutes(self):
        record = EventRecord.from_csv("3;A;4:25;2")
        assert 4*60+25 == record.time_in_seconds
        
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
            "2;A;3",
            "1;B;5",
            "3;A;7",
            "0;A;10",
        ], 0, 0, 0)
        assert infos[0] == (0, 0, 0, 3)
        assert infos[1] == (2, 0, 3, 5)
        assert infos[2] == (2, 1, 5, 7)
        assert infos[3] == (5, 1, 7, 10)
        assert len(infos) == 4
        
    def test_extract_infos_with_several_formats(self):
        infos = EventFile().extract_lines_infos([
            "2;A;3s",
            "1;B;5",
            "3;A;3:12",
            "0;A;1:02:14",
        ], 0, 0, 0)
        assert infos[0] == (0, 0, 0, 3)
        assert infos[1] == (2, 0, 3, 5)
        assert infos[2] == (2, 1, 5, 192)
        assert infos[3] == (5, 1, 192, 3734)
        assert len(infos) == 4
        
    def test_extract_infos_with_several_formats_with_an_initial_score_and_time(self):
        infos = EventFile().extract_lines_infos([
            "2;A;3s",
            "0;A;8s",
        ], 5, 8, 10)
        
        assert infos[0] == (5, 8, 10, 13), infos[0]
        assert infos[1] == (7, 8, 13, 18), infos[1]

    def test_extract_match_events(self):
        match_events = EventFile().extract_match_events([
            "0;X;0",
            "2;A;3",
            "1;B;5",
            "3;A;7",
            "0;A;10",
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
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
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
            "0;X;0;1",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
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
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
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
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
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
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
        ])
        states = match_events.states()
        
        assert states[-1].start == 7
        assert states[-1].end == 10
        assert states[-1].score.team_a == 5
        assert states[-1].score.team_b == 1
        assert states[-1].quarter_time == 2
    
    
    def test_extract_match_states_align_to_the_time(self):
        match_events = EventFile().extract_match_events([
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
        ])
        states = match_events.states(15)
        
        assert states[-1].start == 7
        assert states[-1].end == 15
    
    
    def test_extract_match_states_cut_last_state_if_not_in_time(self):
        match_events = EventFile().extract_match_events([
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
        ])
        states = match_events.states(6)
        
        assert states[-1].start == 5
        assert states[-1].end == 6
        
    def test_extract_match_final_score(self):
        match_events = EventFile().extract_match_events([
            "2;A;3;2",
            "1;B;5;2",
            "3;A;7;2",
            "0;A;10;2",
        ], initial_score=Score(20, 10))
        
        final_score = match_events.final_score()
        assert final_score.team_a == 25
        assert final_score.team_b == 11
    
    def test_time_to_seconds(self):
        assert 5 == time_to_seconds("5")
        assert 5 == time_to_seconds("5s")
        assert 4*60+25 == time_to_seconds("4:25")
        assert 2*3600+14*60+25 == time_to_seconds("2:14:25")

    # def test_display_score(self):
    #     shutil.rmtree("tmp")
    #     os.makedirs("tmp", exist_ok=True)
    #     events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
    #     with (open("tmp/tmp1.csv", "w")) as csv_file:
    #         csv_file.write("\n".join([e.to_csv() for e in events]))
            
    #     match = MatchVideo("", "A", "B")
    #     match.csv_folder = "tmp"
    #     output = match.display_score()
    #     assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B"
        
    # def test_display_score_from_several_files(self):
    #     shutil.rmtree("tmp")
    #     os.makedirs("tmp", exist_ok=True)
    #     events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
    #     with (open("tmp/tmp1.csv", "w")) as csv_file:
    #         csv_file.write("\n".join([e.to_csv() for e in events]))
            
    #     events = [EventRecord(3,"B",2),EventRecord(2,"A",4),EventRecord(0,"X",10)]
    #     with (open("tmp/tmp2.csv", "w")) as csv_file:
    #         csv_file.write("\n".join([e.to_csv() for e in events]))
            
    #     match = MatchVideo("", "A", "B")
    #     match.csv_folder = "tmp"
    #     output = match.display_score()
    #     assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B\n11: A 5 - 4 B\n13: A 7 - 4 B", output
        
        

if __name__ == "__main__":
    unittest.main()