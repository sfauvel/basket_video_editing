

import os
import shutil
import unittest

from video_generator import *

class TestVideoGenerator(unittest.TestCase):

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

    def test_generate_score(self):
        print(generate_score([
                (2, EQUIPE.A, 3),
                (2, EQUIPE.B, 5),
                (1, EQUIPE.A, 8),
            ]))
        
        self.assertEqual([
                (0, 0, 0),
                (2, 0, 3),
                (2, 2, 5),
                (3, 2, 8),
            ], 
            generate_score([
                (2, EQUIPE.A, 3),
                (2, EQUIPE.B, 5),
                (1, EQUIPE.A, 8),
            ])
        )
    
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

    def test_time_to_seconds(self):
        assert 5 == time_to_seconds("5")
        assert 5 == time_to_seconds("5s")
        assert 4*60+25 == time_to_seconds("4:25")
        assert 2*3600+14*60+25 == time_to_seconds("2:14:25")

    def test_display_score(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        match = MatchVideo("", "A", "B")
        match.csv_folder = "tmp"
        output = match.display_score()
        assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B"
        
    def test_display_score_from_several_files(self):
        shutil.rmtree("tmp")
        os.makedirs("tmp", exist_ok=True)
        events = [EventRecord(2,"A",5),EventRecord(1,"B",6),EventRecord(3,"A",7),EventRecord(0,"X",9)]
        with (open("tmp/tmp1.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        events = [EventRecord(3,"B",2),EventRecord(2,"A",4),EventRecord(0,"X",10)]
        with (open("tmp/tmp2.csv", "w")) as csv_file:
            csv_file.write("\n".join([e.to_csv() for e in events]))
            
        match = MatchVideo("", "A", "B")
        match.csv_folder = "tmp"
        output = match.display_score()
        assert output == "0: A 0 - 0 B\n5: A 2 - 0 B\n6: A 2 - 1 B\n7: A 5 - 1 B\n11: A 5 - 4 B\n13: A 7 - 4 B", output
        
        

if __name__ == "__main__":
    unittest.main()