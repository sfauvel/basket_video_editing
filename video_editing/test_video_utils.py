from doc_as_test_pytest import DocAsTest, doc, doc_module

from video_utils import *

class TestTimeMapping:
    """
    Utilities to map time to string.
    """
    
    def test_time_to_seconds(self, doc):
        """
        The function `time_to_seconds` transform the text of a time to the number of seconds. 
        """
        
        def text_time_to_seconds(time):
            try:
                seconds = time_to_seconds(time)
                return f"- {time} -> {seconds}s"
            except Exception as e:
                return f"- {time} -> Exception: {e}"

        doc.write(' +\n'.join([
            text_time_to_seconds("0:05"),
            text_time_to_seconds("4:25"),
            text_time_to_seconds("134:25"),
            text_time_to_seconds("1:14:25"),
        ]))        
        doc.write("\n\nWhen text is mal formed, an exception is raised.\n\n")
        doc.write(' +\n'.join([
            text_time_to_seconds("5s"),
            text_time_to_seconds("1:02:14:25"),
        ]))
        
    def test_seconds_to_time(self, doc):
        """
        The function `seconds_to_time` transform a number of seconds to a time as text. 
        """
        
        def text_seconds_to_time(seconds):
            time = seconds_to_time(seconds)
            return f"- {seconds}s -> {time}"

        doc.write(' +\n'.join([
            text_seconds_to_time(5),
            text_seconds_to_time(4*60+25),
            text_seconds_to_time(1*3600+14*60+25),
        ]))