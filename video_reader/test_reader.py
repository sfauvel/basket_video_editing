
import io
import unittest

from reader import *

class TestEventData(unittest.TestCase):
    def test_add_event_sorted_by_time(self):
        data = EventData()
        data.add_event(123, 2, "A")
        data.add_event(456, 3, "B")
        data.add_event(234, 1, "A")
        
        assert Event(123, 2, "A") == data.events[0]
        assert Event(234, 1, "A") == data.events[1]
        assert Event(456, 3, "B") == data.events[2]
        
    def test_save(self):
        data = EventData()
        data.add_event(123, 2, "A")
        data.add_event(234, 1, "A")
       
        stream = io.StringIO("")
        data.save(stream)
        assert stream.getvalue() == "2;A;123\n1;A;234", stream.getvalue()
        
        
        
    def test_display_time(self):
        build_time = lambda value: str(timedelta(milliseconds=value))
    
        assert "0:00:01.034000" == build_time(1034)
        assert "0:00:01" == build_time(1000)
        assert "0:00:00" == build_time(0)
        assert "-1 day, 23:59:59.999000" == build_time(-1)
        
    def test_build_time_str(self):
        assert "0:00:01" == build_time_str(1034)
        assert "0:00:01" == build_time_str(1000)
        assert "0:01:40" == build_time_str(100000)
        assert "0:00:00" == build_time_str(0)
        assert "0:00:00" == build_time_str(-1)